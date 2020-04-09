from torch.nn import TransformerEncoder, TransformerEncoderLayer, LayerNorm

import torch
import torch.nn as nn
import torch.nn.functional as F


class EmbeddingTransformer(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        seq_len: int,
        intent_class_num: int,
        entity_class_num: int,
        d_model=512,
        nhead=8,
        num_encoder_layers=6,
        dim_feedforward=2048,
        dropout=0.1,
        activation="relu",
    ):
        super(EmbeddingTransformer, self).__init__()

        self.seq_len = seq_len
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.position_embedding = nn.Embedding(seq_len, d_model)
        self.encoder = nn.TransformerEncoder(
            TransformerEncoderLayer(
                d_model, nhead, dim_feedforward, dropout, activation
            ),
            num_encoder_layers,
            LayerNorm(d_model),
        )
        self.intent_feature = nn.Linear(d_model, intent_class_num)
        self.entity_feature = nn.Linear(d_model, entity_class_num)

    def forward(self, x):
        embedding = self.embedding(x)
        embedding += self.position_embedding(
            torch.arange(self.seq_len).repeat(x.size(0), 1)
        )

        feature = self.encoder(embedding.transpose(1, 0))  # (N,S,E) -> (S,N,E)
        # first token in sequence used to intent classification
        intent_feature = self.intent_feature(feature[0, :, :])
        # other tokens in sequence used to entity classification
        entity_feature = self.entity_feature(feature[:, :, :])

        return intent_feature, entity_feature.transpose(1, 0)  # (S,N,E) -> (N,S,E)