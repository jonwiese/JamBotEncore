from pathlib import Path

import settings
from preprocessing.midi_data_processor import MidiDataPreprocessor


def preprocess_midi_data():
    midi_preprocesser = MidiDataPreprocessor(
        source_folder='../data/lmd_full/small_set/0_original',
        tempo_shift_folder='../data/lmd_full/small_set/1_tempo',
        histo_folder_1='../data/lmd_full/small_set/2_histo',
        song_histo_folder='../data/lmd_full/small_set/3_shifted_song_histograms',
        key_shifted_folder='../data/lmd_full/small_set/4_shifted_tempo',
        piano_roll_folder='../data/lmd_full/small_set/5_shifted_pianoroll',
        shifted_histo_folder='../data/lmd_full/small_set/6_shifted_histo',
        chords_folder='../data/lmd_full/small_set/7_shifted_chords',
        chords_index_folder='../data/lmd_full/small_set/8_shifted_chords_index',
        dict_path='../data/lmd_full/small_set/9_chord_dicts',
        chord_dict_name='shifted_chord_dict.pickle',
        index_dict_name='shifted_index_dict.pickle',

        sampling_frequency=settings.sampling_frequency,
    )
    print('changing Tempo')
    midi_preprocesser.change_tempo_of_midi_files()

    print('histogramming')
    midi_preprocesser.save_histo_oct_from_midi_folder()

    print('make song histo')
    midi_preprocesser.save_song_histo_from_histo()

    print('shifting midi files')
    midi_preprocesser.shift_midi_files()

    print('making note indexes')
    midi_preprocesser.note_ind_folder()

    print('histogramming')
    midi_preprocesser.save_histo_oct_from_shifted_midi_folder()

    print('extracting chords')
    midi_preprocesser.save_chords_from_histo()
    print('getting dictionary')
    chord_to_index, index_to_chord = midi_preprocesser.make_chord_dict(settings.num_chords)
    print('converting chords to index sequences')
    midi_preprocesser.save_index_from_chords()

if __name__ == '__main__':
    preprocess_midi_data()
