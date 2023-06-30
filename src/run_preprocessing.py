import logging
from pathlib import Path

import settings
from preprocessing.midi_data_preprocessor_config import MidiDataPreprocessorConfig
from preprocessing.midi_data_processor import MidiDataPreprocessor


def preprocess_midi_data():
    midi_preprocesser_config = MidiDataPreprocessorConfig(
        source_folder=Path('../data/lmd_full/small_set/0_original'),
        tempo_shift_folder=Path('../data/lmd_full/small_set/1_tempo_shifted_to_120bpm'),
        histogram_per_bar_folder=Path('../data/lmd_full/small_set/2_histogram_per_bar'),
        histogram_per_song_folder=Path('../data/lmd_full/small_set/3_histogram_per_song'),
        key_shifted_folder=Path('../data/lmd_full/small_set/4_key_shifted_to_c'),
        piano_roll_folder=Path('../data/lmd_full/small_set/5_shifted_pianoroll'),
        key_shifted_histogram_per_bar_folder=Path('../data/lmd_full/small_set/6_shifted_histo'),
        chords_folder=Path('../data/lmd_full/small_set/7_shifted_chords'),
        chords_index_folder=Path('../data/lmd_full/small_set/8_shifted_chords_index'),
        dict_path=Path('../data/lmd_full/small_set/9_chord_dicts'),
        chord_dict_name='shifted_chord_dict.pickle',
        index_dict_name='shifted_index_dict.pickle',

        sampling_frequency=settings.sampling_frequency,
    )

    midi_preprocesser = MidiDataPreprocessor(midi_preprocesser_config)

    logging.log(logging.INFO, 'change tempo to 120 bpm')
    midi_preprocesser.change_tempo_of_midi_files()

    logging.log(logging.INFO, 'make note histogram for each bar')
    midi_preprocesser.make_note_histograms_per_bar()

    logging.log(logging.INFO, 'make note histogram for whole song')
    midi_preprocesser.make_histograms_per_song()

    logging.log(logging.INFO, 'shifting midi files the key of C')
    midi_preprocesser.shift_midi_files()

    logging.log(logging.INFO, 'making note indexes')
    midi_preprocesser.note_ind_folder()

    logging.log(logging.INFO, 'histogramming')
    midi_preprocesser.save_histo_oct_from_shifted_midi_folder()

    logging.log(logging.INFO, 'extracting chords')
    midi_preprocesser.save_chords_from_histo()
    logging.log(logging.INFO, 'getting dictionary')
    midi_preprocesser.make_chord_dict(settings.num_chords)
    logging.log(logging.INFO, 'converting chords to index sequences')
    midi_preprocesser.save_index_from_chords()


if __name__ == '__main__':
    preprocess_midi_data()
