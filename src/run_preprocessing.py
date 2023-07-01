import logging
from pathlib import Path

import settings
from preprocessing.midi_data_preprocessor_config import MidiDataPreprocessorConfig
from preprocessing.midi_data_processor import MidiDataPreprocessor

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def preprocess_midi_data():
    data_folder = Path('../data/2000_songs_data_set')

    midi_preprocesser_config = MidiDataPreprocessorConfig(
        source_folder=data_folder.joinpath('0_original'),
        tempo_shift_folder=data_folder.joinpath('1_tempo_shifted_to_120bpm'),
        histogram_per_bar_folder=data_folder.joinpath('2_histogram_per_bar'),
        histogram_per_song_folder=data_folder.joinpath('3_histogram_per_song'),
        key_shifted_folder=data_folder.joinpath('4_key_shifted_to_c'),
        piano_roll_folder=data_folder.joinpath('5_shifted_pianoroll'),
        key_shifted_histogram_per_bar_folder=data_folder.joinpath('6_shifted_histo'),
        chords_folder=data_folder.joinpath('7_shifted_chords'),
        dict_path=data_folder.joinpath('8_chord_dicts'),
        chords_index_folder=data_folder.joinpath('9_shifted_chords_index'),
        chord_dict_name='shifted_chord_dict.pickle',
        index_dict_name='shifted_index_dict.pickle',

        sampling_frequency=settings.sampling_frequency,
    )

    midi_preprocesser = MidiDataPreprocessor(midi_preprocesser_config)

    logging.info('1. Shift the tempo of all the midi files to 120 bmp')
    midi_preprocesser.save_tempo_shifted_midi_files()

    logging.info('2. Create a histogram of which notes are played for each bar of every song')
    midi_preprocesser.save_note_histograms_per_bar()

    logging.info('3. Create a histogram of which notes are played for each song')
    midi_preprocesser.save_note_histograms_per_song()

    logging.info('4. Shift all the notes of the midi files to the key of C major')
    midi_preprocesser.save_shifted_midi_files()

    logging.info('5. Create a pianoroll representation of tempo/key shifted midi files')
    midi_preprocesser.save_note_index_from_pianorolls()

    logging.info('6. Create a histogram of which notes are played for each bar of every key shifted song')
    midi_preprocesser.save_histo_oct_from_shifted_midi_folder()

    logging.info('7. Extract a chord for each bar from histogram data')
    midi_preprocesser.save_chords_from_histogram()
    logging.info('8. Make a chord dictionary that maps the 50 most used chords to an index')
    midi_preprocesser.make_chord_dict(settings.num_chords)
    logging.info('9. Create chord-index sequence for each song ')
    midi_preprocesser.save_chord_index_sequence()


if __name__ == '__main__':
    preprocess_midi_data()
