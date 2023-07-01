from pathlib import Path


class MidiDataPreprocessorConfig:
    def __init__(self, source_folder: Path, tempo_shift_folder: Path, histogram_per_bar_folder: Path, key_shifted_folder: Path,
                 key_shifted_histogram_per_bar_folder: Path, piano_roll_folder: Path, histogram_per_song_folder: Path,
                 chords_folder: Path, chords_index_folder: Path, dict_path: Path, chord_dict_name: str,
                 index_dict_name: str, sampling_frequency: int):
        self.source_folder = source_folder
        self.tempo_shift_folder = tempo_shift_folder
        self.histogram_per_bar_folder = histogram_per_bar_folder
        self.key_shifted_folder = key_shifted_folder
        self.key_shifted_histogram_per_bar_folder = key_shifted_histogram_per_bar_folder
        self.piano_roll_folder = piano_roll_folder
        self.histogram_per_song_folder = histogram_per_song_folder
        self.chords_folder = chords_folder
        self.dict_path = dict_path
        self.chords_index_folder = chords_index_folder
        self.chord_dict_name = chord_dict_name
        self.index_dict_name = index_dict_name
        self.sampling_frequency = sampling_frequency
