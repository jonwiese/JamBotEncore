from pathlib import Path

import torch

from training.chord_lstm.chord_lstm import ChordLstm
from training.lstm_trainer import LstmTrainerConfig, LstmTrainer
from training.chord_lstm.data_loader import ChordDataLoader

if __name__ == '__main__':

    chord_index_folder = Path('../data/2000_songs_data_set/9_shifted_chords_index')
    chord_data_loader = ChordDataLoader(chord_index_folder)
    training_data, test_data = chord_data_loader.get_chord_train_and_test_set()

    model = ChordLstm()

    trainer_config = LstmTrainerConfig(
        loss_fn=torch.nn.NLLLoss(),
        optimizer=torch.optim.Adam(model.parameters(), lr=1e-2),
        num_epochs=100,
        model_folder=Path('../models/2000_songs_data_set')
    )

    trainer = LstmTrainer(model, training_data, test_data, trainer_config)

    trainer.train()
