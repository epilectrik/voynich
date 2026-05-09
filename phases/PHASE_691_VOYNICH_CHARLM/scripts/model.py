#!/usr/bin/env python3
"""
Small encoder transformer for Voynich char-LM.

Locked architecture per Phase 691.1 pre-registration:
  - 6 layers, 256 hidden dim, 8 heads, FFN dim 1024
  - Max seq length 256
  - Char-level vocab (~28 tokens)
  - ~6M params total
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class CharLM(nn.Module):
    def __init__(self, vocab_size, d_model=256, nhead=8, num_layers=6,
                 dim_feedforward=1024, max_seq_len=256, dropout=0.1):
        super().__init__()
        self.d_model = d_model
        self.vocab_size = vocab_size
        self.max_seq_len = max_seq_len

        self.tok_embed = nn.Embedding(vocab_size, d_model)
        self.pos_embed = nn.Embedding(max_seq_len, d_model)
        self.embed_dropout = nn.Dropout(dropout)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            activation='gelu',
            batch_first=True,
            norm_first=True,  # Pre-LN: more stable for small models
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.layer_norm = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size)

        # Tie weights
        self.lm_head.weight = self.tok_embed.weight

        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, std=0.02)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Embedding):
                nn.init.normal_(m.weight, std=0.02)

    def forward(self, ids, attn_mask=None, return_hidden=False, return_attentions=False):
        """
        ids: [B, L] long tensor of token IDs
        attn_mask: [B, L] bool tensor, True at PAD positions (to be IGNORED)
        Returns:
            logits: [B, L, V]
            (optionally) hidden states, attention weights
        """
        B, L = ids.shape
        positions = torch.arange(L, device=ids.device).unsqueeze(0).expand(B, L)
        h = self.tok_embed(ids) + self.pos_embed(positions)
        h = self.embed_dropout(h)

        # PyTorch encoder uses src_key_padding_mask: True = ignore
        h = self.encoder(h, src_key_padding_mask=attn_mask)
        h = self.layer_norm(h)
        logits = self.lm_head(h)

        if return_hidden:
            return logits, h
        return logits

    @torch.no_grad()
    def encode(self, ids, attn_mask=None):
        """Encode without LM head — returns final hidden states."""
        B, L = ids.shape
        positions = torch.arange(L, device=ids.device).unsqueeze(0).expand(B, L)
        h = self.tok_embed(ids) + self.pos_embed(positions)
        h = self.encoder(h, src_key_padding_mask=attn_mask)
        h = self.layer_norm(h)
        return h


def count_params(model):
    return sum(p.numel() for p in model.parameters())


if __name__ == '__main__':
    m = CharLM(vocab_size=28)
    print(f"Total params: {count_params(m):,}")
    # Test forward
    x = torch.randint(0, 28, (2, 32))
    mask = torch.zeros(2, 32, dtype=torch.bool)
    logits = m(x, mask)
    print(f"Output shape: {logits.shape}")
