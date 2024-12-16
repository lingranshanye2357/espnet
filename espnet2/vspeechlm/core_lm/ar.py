#!/usr/bin/env python3

# Copyright 2024 Jinchuan Tian
#  Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)

# Implementation of UniAudio architecture: https://arxiv.org/abs/2310.00704

from typing import Dict, Tuple

import torch

from espnet2.vspeechlm.core_lm.abs_core_lm import AbsCoreLM, VSpeechLMInferenceOptions


class ARLM(AbsCoreLM):
    def __init__(
        self,
        vocab_size: int,
        nq: int,
        token_bias: dict,
        pad_id: int,
        hf_model_tag: str = None,
        share_emb: bool = False,
        qk_norm: bool = False,
        dropout: float = 0.0,
        att_unit: int = 256,
        head: int = 2,
        layer: int = 4,
        n_ctx: int = 3000,
        sos_eos: int = 5,
    ):
        """Initialize standard Auto-regressive LM .

        Args:
            vocab_size (int): Dimention of vocabulary.
            nq (int): Number of codes for each token / frame, usually for speech codec.
            share_emb (bool): If true, share the embedding and lm_head weight.
            qk_norm: (bool): If true, apply LayerNorm to q and k in atention.
            dropout: (float): dropout rate for attention layers.
            att_unit (int): Dimention of global Transformer attention.
            head (int): Number of heads in global Transformer attention.
            layer (int): Number of layers in global Transformer.
            n_ctx (int): maximum context length of global Transformer.
        """
        super(ARLM, self).__init__()

        self.emb = torch.nn.Embedding(vocab_size, att_unit)
        self.lm_head = torch.nn.Linear(att_unit, vocab_size, bias=False)
        if share_emb:
            self.lm_head.weight = self.emb.weight

        self.decoders = TransformerDecoder(
            n_ctx=n_ctx,
            n_state=att_unit,
            n_head=head,
            n_layer=layer,
            qk_norm=qk_norm,
            dropout=dropout,
            hf_model_tag=hf_model_tag,
            token_bias=token_bias,
        )

        self.nq = nq
        self.n_ctx = n_ctx
        self.sos_eos = sos_eos
        self.pad_id = pad_id

        self.decoders.init_embeddings(self.emb, self.lm_head)
        self.criterion = FusedLinearCrossEntropyLoss(self.lm_head, self.pad_id)

    def forward(
        self,
        dec_seq: torch.Tensor,
        dec_seq_lengths: torch.Tensor = None,
        enc_seq: torch.Tensor = None,
        enc_seq_lengths: torch.Tensor = None,
        prefix_len: torch.Tensor = None,
        compute_loss: bool = True,
    ) -> Tuple[torch.Tensor, Dict, torch.Tensor]:
        """Auto-Regresive LM forward for training.

        Args:
            dec_seq (LongTensor): Batch of decoder sequences (B, T, nq).
            dec_seq_lengths (LongTensor): Lengths of batched decoder sequences (B,).
            enc_seq (LongTensor): Batch of encoder sequences (B, T, nq), keep the interface,
                may not be used.
            enc_seq_lengths (LongTensor): Lengths of batched encoder sequences (B,),
                keep the interface, may not be used.
            prefix_len (LongTensor): Lengths of condition part in dec_seq (B,).
            compute_loss (bool): whether to compute loss or just logits.
        """
        assert dec_seq.dim() == 3

        target = dec_seq[:, 1:, :1]
        x = dec_seq[:, :-1]
        x = self.emb(x).mean(dim=2)
        x = self.decoders(x)
        x = x.unsqueeze(2)

        loss, logits, stats, weight = self.criterion(x, target)

        return loss, logits, stats, weight

    def _init_embeddings(self):
        if "text_bpe" not in self.token_bias:
            return

        start = self.token_bias["text_bpe"]
        values = list(self.token_bias.values())

    @torch.no_grad()
    def inference(
        self,
        prefix: torch.Tensor,
        opts: VSpeechLMInferenceOptions,
        enc_seq: torch.Tensor = None,
        suffix: torch.Tensor = None,
    ):
        """Auto-Regresive MultiScale Inference.

        Args:
            prefix (LongTensor): Prefix part of dec_seq (B, T_dec, nq).
            opts (VSpeechLMInferenceOptions): inference options.
            enc_seq (LongTensor): Encoder token sequence (B, T_enc, nq).
            suffix (LongTensor): suffix part of dec_seq (B, T_dec, nq),
                usually the target sequence for teacher-forcing.
        """

        raise NotImplementedError
