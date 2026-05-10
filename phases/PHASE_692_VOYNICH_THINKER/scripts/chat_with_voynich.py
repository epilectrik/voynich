#!/usr/bin/env python3
"""
Phase 692 Step 5: Interactive chat with the Voynich-thinker model.

Loads the v2 LoRA adapter on top of DeepSeek-R1-Distill-Qwen-14B and provides
a streaming chat REPL. The model has been fine-tuned on the project corpus
(2018 constraints, 691 phases, full H-track transcript, workshop dictionaries,
cold-read tables, memory notes, methodology docs).

Usage:
  python chat_with_voynich.py
  python chat_with_voynich.py --temperature 0.7  (more creative)
  python chat_with_voynich.py --no-stream         (don't stream, just print final)

Commands within the chat:
  /quit             exit
  /reset            clear conversation history
  /save <name>      save conversation to a file
  /system <text>    replace the system prompt
  /temp <float>     change temperature
  /verify           extract C-numbers from last response, look them up in CONSTRAINT_TABLE
"""
import argparse
import re
import sys
from pathlib import Path

import torch

PHASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PHASE_DIR.parents[1]


SYSTEM_PROMPT = """You are an expert on the Voynich Manuscript research project. The project has registered 2018+ structural constraints across 691+ research phases. You have read the full H-track transcript, all constraint files, phase reports, workshop dictionaries, and cold-read tables.

You reason in terms of:
- Constraints (cited as C####), tier-marked (Tier 0=frozen, 1=falsified, 2=established, 3=speculative, 4=exploratory)
- Operational categories from C1394 (HEAD+MOD*+TERM atom system)
- Workshop interpretations (PT-### Catalan-grounded definitions)
- Confirmed Phase 668 recipe-folio matches with Pseudo-Lull chapters

Critical distinctions you maintain:
- Atom decomposition (e.g., kee = heat.cool.cool) is STRUCTURAL ONLY, not semantic.
- Compound/operational reading (e.g., kee = "gentle stabilized heat", balneum mariae signature per C1455) is the meaningful interpretation.
- You distinguish corroborated (Tier 2) from speculative (Tier 3-4) claims.
- You cite specific constraints when making claims.
- You acknowledge what is falsified (Tier 1) and refuse to reproduce it.

When asked about specific folios, lines, or tokens, draw on actual transcript content. When asked about cross-folio patterns, attempt corpus-mining reasoning. When uncertain, say so honestly rather than confabulating."""


def load_constraints():
    """Load real constraint numbers for /verify command."""
    real = set()
    table = PROJECT_ROOT / 'context' / 'CONSTRAINT_TABLE.txt'
    if table.exists():
        text = table.read_text(encoding='utf-8', errors='ignore')
        for m in re.findall(r'C(\d{3,4})', text):
            real.add(int(m))
    idx = PROJECT_ROOT / 'context' / 'CLAIMS' / 'INDEX.md'
    if idx.exists():
        text = idx.read_text(encoding='utf-8', errors='ignore')
        for m in re.findall(r'C(\d{3,4})', text):
            real.add(int(m))
    return real


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', default='deepseek-ai/DeepSeek-R1-Distill-Qwen-14B')
    parser.add_argument('--adapter',
                        default=str(PHASE_DIR / 'results' / 'voynich_thinker_lora_v2' / 'final'))
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--temperature', type=float, default=0.6)
    parser.add_argument('--max-new', type=int, default=1024)
    parser.add_argument('--no-stream', action='store_true')
    args = parser.parse_args()

    from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer
    from peft import PeftModel

    device = torch.device(args.device if torch.cuda.is_available() else 'cpu')
    print(f"Loading {args.base}...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(args.base, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Loading model in bf16...", flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.base, torch_dtype=torch.bfloat16, trust_remote_code=True,
    ).to(device)
    print(f"Loading LoRA adapter: {args.adapter}", flush=True)
    model = PeftModel.from_pretrained(model, args.adapter)
    model.eval()
    print(f"Ready.\n", flush=True)

    real_constraints = load_constraints()
    print(f"Loaded {len(real_constraints)} real constraints for /verify\n")

    history = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    last_response = ''
    temperature = args.temperature

    print("=" * 70)
    print("VOYNICH-THINKER CHAT")
    print("=" * 70)
    print("Commands: /quit /reset /save <name> /system <text> /temp <float> /verify")
    print()

    while True:
        try:
            user = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user:
            continue

        # Commands
        if user == '/quit':
            break
        if user == '/reset':
            history = [{'role': 'system', 'content': SYSTEM_PROMPT}]
            last_response = ''
            print("[history reset]")
            continue
        if user.startswith('/save '):
            name = user[6:].strip() or 'chat_log.txt'
            out = PHASE_DIR / 'results' / 'chat_logs' / name
            out.parent.mkdir(parents=True, exist_ok=True)
            with open(out, 'w', encoding='utf-8') as f:
                for m in history:
                    f.write(f"[{m['role']}]\n{m['content']}\n\n")
            print(f"[saved to {out}]")
            continue
        if user.startswith('/system '):
            new_sys = user[8:].strip()
            history[0] = {'role': 'system', 'content': new_sys}
            print(f"[system prompt updated]")
            continue
        if user.startswith('/temp '):
            try:
                temperature = float(user[6:].strip())
                print(f"[temperature = {temperature}]")
            except ValueError:
                print("[invalid temperature]")
            continue
        if user == '/verify':
            cited = set(int(c) for c in re.findall(r'C(\d{3,4})', last_response))
            real = sorted(c for c in cited if c in real_constraints)
            fake = sorted(c for c in cited if c not in real_constraints)
            print(f"  Cited: {sorted(cited)}")
            print(f"  REAL:  {real}")
            print(f"  FAKE:  {fake}")
            continue

        # Generate
        history.append({'role': 'user', 'content': user})
        prompt_text = tokenizer.apply_chat_template(
            history, tokenize=False, add_generation_prompt=True,
        )
        enc = tokenizer(prompt_text, return_tensors='pt').to(device)

        print("\nthinker> ", end='', flush=True)
        if args.no_stream:
            with torch.no_grad():
                out = model.generate(
                    **enc, max_new_tokens=args.max_new,
                    do_sample=temperature > 0.01,
                    temperature=max(0.01, temperature),
                    top_p=0.9, pad_token_id=tokenizer.eos_token_id,
                )
            response = tokenizer.decode(out[0][enc['input_ids'].shape[1]:], skip_special_tokens=True)
            print(response)
        else:
            streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
            with torch.no_grad():
                out = model.generate(
                    **enc, max_new_tokens=args.max_new,
                    do_sample=temperature > 0.01,
                    temperature=max(0.01, temperature),
                    top_p=0.9, pad_token_id=tokenizer.eos_token_id,
                    streamer=streamer,
                )
            response = tokenizer.decode(out[0][enc['input_ids'].shape[1]:], skip_special_tokens=True)

        last_response = response
        history.append({'role': 'assistant', 'content': response})
        print()


if __name__ == '__main__':
    main()
