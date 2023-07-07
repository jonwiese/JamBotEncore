import torch.nn as nn

from training.chord_lstm import settings


class ChordLstm(nn.Module):
    def __init__(self):
        super(ChordLstm, self).__init__()
        self.chord_embedding = nn.Embedding(settings.num_chords, settings.chord_embedding_dim)
        self.lstm = nn.LSTM(settings.chord_embedding_dim, settings.chord_lstm_hidden_layer_size)
        self.hidden_to_chord = nn.Linear(settings.chord_lstm_hidden_layer_size, settings.num_chords)
        self.log_softmax = nn.LogSoftmax(dim=1)

    def forward(self, chord_sequence):
        embeddings = self.chord_embedding(chord_sequence)
        hidden, _ = self.lstm(embeddings.view(len(chord_sequence), 1, -1))
        chord_space = self.hidden_to_chord(hidden.view(len(chord_sequence), -1))
        chord_scores = self.log_softmax(chord_space)
        return chord_scores

