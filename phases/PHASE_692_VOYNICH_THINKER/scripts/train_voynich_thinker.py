#!/usr/bin/env python3
"""
Phase 692 Step 3: LoRA fine-tune DeepSeek-R1-Distill-Qwen-14B on Voynich corpus.

Two-stage training:
  Stage A: Knowledge ingestion (training_text.jsonl) - 1 epoch
           Plain causal LM with structural metadata headers.

  Stage B: Instruction tuning (training_chat.jsonl) - 1 epoch
           ChatML conversational format with system prompt.

Uses LoRA (rank=32, alpha=64) for memory efficiency. ~14B base in bf16 (~28GB)
+ LoRA adapter (~200MB) fits on a single A6000 (48GB VRAM).

Saves LoRA adapter to results/voynich_thinker_lora/.
"""
import argparse
import functools
import json
import math
import sys
import time
from pathlib import Path

print = functools.partial(print, flush=True)

import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

PHASE_DIR = Path(__file__).resolve().parent.parent


class JsonlTextDataset(Dataset):
    """Loads {"text": "..."} JSONL for causal LM training."""
    def __init__(self, path, tokenizer, max_length=2048):
        self.records = []
        with open(path, encoding='utf-8') as f:
            for line in f:
                r = json.loads(line)
                self.records.append(r['text'])
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        text = self.records[idx]
        enc = self.tokenizer(text, return_tensors=None, truncation=True,
                             max_length=self.max_length, padding=False)
        ids = enc['input_ids']
        return torch.tensor(ids, dtype=torch.long)


class JsonlChatDataset(Dataset):
    """Loads {"messages": [...]} JSONL, formats with model's chat template."""
    def __init__(self, path, tokenizer, max_length=2048):
        self.records = []
        with open(path, encoding='utf-8') as f:
            for line in f:
                r = json.loads(line)
                self.records.append(r['messages'])
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        messages = self.records[idx]
        # Apply chat template (DeepSeek-R1 has its own template)
        try:
            text = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=False,
            )
        except Exception:
            # Fallback for tokenizers without chat template
            parts = []
            for m in messages:
                parts.append(f"{m['role']}: {m['content']}")
            text = '\n\n'.join(parts)
        enc = self.tokenizer(text, return_tensors=None, truncation=True,
                             max_length=self.max_length, padding=False)
        return torch.tensor(enc['input_ids'], dtype=torch.long)


def collate_pad(batch, pad_id=0):
    L = max(len(x) for x in batch)
    out = torch.full((len(batch), L), pad_id, dtype=torch.long)
    for i, x in enumerate(batch):
        out[i, :len(x)] = x
    attn = (out != pad_id).long()
    return out, attn


def train_loop(model, loader, optimizer, scheduler, device, n_epochs, label, save_dir):
    model.train()
    n_steps = 0
    losses = []
    start = time.time()
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    for epoch in range(n_epochs):
        for ids, attn in loader:
            ids = ids.to(device)
            attn = attn.to(device)
            labels = ids.clone()
            labels[attn == 0] = -100

            out = model(input_ids=ids, attention_mask=attn, labels=labels)
            loss = out.loss

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            if scheduler:
                scheduler.step()

            losses.append(loss.item())
            n_steps += 1

            if n_steps % 25 == 0:
                avg = sum(losses[-25:]) / min(25, len(losses))
                elapsed = time.time() - start
                print(f"  [{label}] step {n_steps}: loss={avg:.4f}  elapsed={elapsed:.0f}s")

        # End of epoch
        avg = sum(losses[-50:]) / min(50, len(losses))
        print(f"  [{label}] epoch {epoch+1}/{n_epochs} done. last-50 avg loss={avg:.4f}")

    return n_steps, losses


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='deepseek-ai/DeepSeek-R1-Distill-Qwen-14B')
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--epochs-text', type=int, default=1)
    parser.add_argument('--epochs-chat', type=int, default=1)
    parser.add_argument('--batch-size', type=int, default=1)
    parser.add_argument('--max-length', type=int, default=2048)
    parser.add_argument('--lr', type=float, default=1e-4)
    parser.add_argument('--lora-rank', type=int, default=32)
    parser.add_argument('--lora-alpha', type=int, default=64)
    parser.add_argument('--gradient-accumulation', type=int, default=4)
    parser.add_argument('--save-dir', default=str(PHASE_DIR / 'results' / 'voynich_thinker_lora'))
    parser.add_argument('--text-only', action='store_true', help='Skip chat stage')
    parser.add_argument('--chat-only', action='store_true', help='Skip text stage')
    args = parser.parse_args()

    from transformers import AutoModelForCausalLM, AutoTokenizer, get_cosine_schedule_with_warmup
    from peft import LoraConfig, get_peft_model, TaskType

    device = torch.device(args.device if torch.cuda.is_available() else 'cpu')
    print(f"Loading model: {args.model}")
    print(f"Device: {device}")
    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    pad_id = tokenizer.pad_token_id

    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.bfloat16, trust_remote_code=True,
    ).to(device)
    # Enable gradient checkpointing — recomputes activations to save memory
    model.gradient_checkpointing_enable()
    model.enable_input_require_grads()  # required for grad checkpointing with PEFT
    if hasattr(model, 'config'):
        model.config.use_cache = False  # incompatible with grad ckpt
    print(f"  Base params: {sum(p.numel() for p in model.parameters()):,}")

    # Configure LoRA
    target_modules = ['q_proj', 'k_proj', 'v_proj', 'o_proj',
                      'gate_proj', 'up_proj', 'down_proj']
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=args.lora_rank, lora_alpha=args.lora_alpha,
        lora_dropout=0.05,
        target_modules=target_modules,
        bias='none',
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # Datasets
    text_path = PHASE_DIR / 'data' / 'training_text.jsonl'
    chat_path = PHASE_DIR / 'data' / 'training_chat.jsonl'
    print(f"\nLoading {text_path}...")
    text_ds = JsonlTextDataset(text_path, tokenizer, args.max_length)
    print(f"  {len(text_ds)} samples")
    print(f"Loading {chat_path}...")
    chat_ds = JsonlChatDataset(chat_path, tokenizer, args.max_length)
    print(f"  {len(chat_ds)} samples")

    save_dir = Path(args.save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    eff_batch = args.batch_size * args.gradient_accumulation
    print(f"\nEffective batch size: {eff_batch}")

    # Optimizer (LoRA params only)
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=args.lr, weight_decay=0.01, betas=(0.9, 0.95),
    )

    # Stage A: Text training
    if not args.chat_only:
        print(f"\n=== Stage A: Knowledge ingestion (text format, {args.epochs_text} epochs) ===")
        loader = DataLoader(
            text_ds, batch_size=args.batch_size, shuffle=True,
            collate_fn=lambda b: collate_pad(b, pad_id=pad_id),
            num_workers=2,
        )
        n_total = len(loader) * args.epochs_text
        scheduler = get_cosine_schedule_with_warmup(
            optimizer, num_warmup_steps=200, num_training_steps=n_total,
        )
        train_loop(model, loader, optimizer, scheduler, device,
                   args.epochs_text, 'text', save_dir)
        # Save mid-stage adapter
        model.save_pretrained(str(save_dir / 'after_text'))
        tokenizer.save_pretrained(str(save_dir / 'after_text'))
        print(f"  Saved adapter to {save_dir / 'after_text'}")

    # Stage B: Chat training
    if not args.text_only:
        print(f"\n=== Stage B: Instruction tuning (chat format, {args.epochs_chat} epochs) ===")
        loader = DataLoader(
            chat_ds, batch_size=args.batch_size, shuffle=True,
            collate_fn=lambda b: collate_pad(b, pad_id=pad_id),
            num_workers=2,
        )
        # Lower LR for chat stage
        for g in optimizer.param_groups:
            g['lr'] = args.lr * 0.5
        n_total = len(loader) * args.epochs_chat
        scheduler = get_cosine_schedule_with_warmup(
            optimizer, num_warmup_steps=100, num_training_steps=n_total,
        )
        train_loop(model, loader, optimizer, scheduler, device,
                   args.epochs_chat, 'chat', save_dir)
        model.save_pretrained(str(save_dir / 'final'))
        tokenizer.save_pretrained(str(save_dir / 'final'))
        print(f"  Saved final adapter to {save_dir / 'final'}")

    # Save metadata
    meta = {
        'base_model': args.model,
        'lora_rank': args.lora_rank,
        'lora_alpha': args.lora_alpha,
        'lr': args.lr,
        'epochs_text': args.epochs_text,
        'epochs_chat': args.epochs_chat,
        'max_length': args.max_length,
        'batch_size': args.batch_size,
        'gradient_accumulation': args.gradient_accumulation,
    }
    with open(save_dir / 'training_metadata.json', 'w') as f:
        json.dump(meta, f, indent=2)
    print(f"\nDone. Adapter at {save_dir}")


if __name__ == '__main__':
    main()
