import pickle
from pathlib import Path

import torch


class ChordDataLoader:
    def __init__(self, chords_index_folder: Path):
        self.chords_index_folder = chords_index_folder

    def get_chord_train_and_test_set(self):
        chord_sequences = self.__load_chord_sequences()
        data_set = self.__make_dataset(chord_sequences)

        train_set, test_set = torch.utils.data.random_split(data_set, [0.75, 0.25])
        return train_set, test_set

    def __load_chord_sequences(self) -> list[list]:
        data = []
        for chords_song_file in self.chords_index_folder.rglob('*.pickle'):
            song = pickle.load(open(chords_song_file, 'rb'))
            data.append(song)
        return data

    @staticmethod
    def __make_dataset(chord_sequences: list[list]) -> list[tuple]:
        dataset = []
        for chord_sequence in chord_sequences:
            chord_input = chord_sequence[:-1]
            chord_target = chord_sequence[1:]
            dataset.append((chord_input, chord_target))
        return dataset
