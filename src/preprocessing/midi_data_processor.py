import os
import logging
import numpy as np
from collections import Counter
import _pickle as pickle

from mido import KeySignatureError

import settings
from utils import midi_functions
from preprocessing.midi_data_preprocessor_config import MidiDataPreprocessorConfig


class MidiDataPreprocessor:
    def __init__(self, config: MidiDataPreprocessorConfig):
        self.config = config
        self.intercepted_errors =\
            (ValueError, EOFError, IndexError, OSError, KeyError, ZeroDivisionError, AttributeError, KeySignatureError)
    def save_tempo_shifted_midi_files(self) -> None:
        self.config.tempo_shift_folder.mkdir(exist_ok=True)
        for midi_file in self.config.source_folder.rglob('*.mid'):
            try:
                midi_functions.change_tempo_of_midi_file(midi_file, self.config.tempo_shift_folder)
            except self.intercepted_errors as e:
                logging.debug(f'Unexpected error when processing {midi_file}: {e}')

    def save_note_histograms_per_bar(self) -> None:
        self.config.histogram_per_bar_folder.mkdir(exist_ok=True)
        for midi_file in self.config.source_folder.rglob('*.mid'):
            try:
                midi_functions.midi_to_histo_oct(settings.samples_per_bar, settings.half_steps_in_octave,
                                                 settings.sampling_frequency, midi_file,
                                                 self.config.histogram_per_bar_folder)
            except self.intercepted_errors as e:
                logging.debug(f'Unexpected error when processing {midi_file}: {e}')

    def save_note_histograms_per_song(self) -> None:
        self.config.histogram_per_song_folder.mkdir(exist_ok=True)
        for histogram_file in self.config.histogram_per_bar_folder.rglob('*.pickle'):
            midi_functions.load_histo_save_song_histo(histogram_file, self.config.histogram_per_song_folder)

    def save_shifted_midi_files(self) -> None:
        self.config.key_shifted_folder.mkdir(exist_ok=True)
        for histogram_file in self.config.histogram_per_song_folder.rglob('*.pickle'):
            song_histogram = pickle.load(open(histogram_file, 'rb'))
            key = midi_functions.song_histogram_to_key(song_histogram, settings.notes_per_key)
            shift = self.__get_shift(key)
            song_name = histogram_file.name.replace('.pickle', '')
            if shift != 'other':
                try:
                    midi_functions.shift_midi(
                        shift, song_name, self.config.tempo_shift_folder, self.config.key_shifted_folder)
                except self.intercepted_errors as e:
                    logging.debug(f'Unexpected error when processing {histogram_file}: {e}')

    def save_note_index_from_pianorolls(self) -> None:
        self.config.piano_roll_folder.mkdir(exist_ok=True)
        for midi_file in self.config.key_shifted_folder.rglob('*.mid'):
            intercepted_errors = (ValueError, EOFError, IndexError, OSError, KeyError, ZeroDivisionError)
            try:
                midi_functions.save_note_ind(midi_file, self.config.piano_roll_folder, settings.sampling_frequency)
            except self.intercepted_errors as e:
                logging.debug(f'Unexpected error when processing {midi_file}: {e}')

    def save_histo_oct_from_shifted_midi_folder(self) -> None:
        self.config.key_shifted_histogram_per_bar_folder.mkdir(exist_ok=True)
        for midi_file in self.config.key_shifted_folder.rglob('*.mid'):
            try:
                midi_functions.midi_to_histo_oct(settings.samples_per_bar, settings.half_steps_in_octave,
                                                 settings.sampling_frequency, midi_file,
                                                 self.config.key_shifted_histogram_per_bar_folder)
            except self.intercepted_errors as e:
                logging.debug(f'Unexpected error when processing {midi_file}: {e}')

    def save_chords_from_histogram(self) -> None:
        self.config.chords_folder.mkdir(exist_ok=True)
        for histogram_file in self.config.key_shifted_histogram_per_bar_folder.rglob('*.pickle'):
            midi_functions.chord_histogram_to_chords(settings.notes_per_chord, histogram_file, self.config.chords_folder)

    def make_chord_dict(self, num_chords: int) -> None:
        self.config.dict_path.mkdir(exist_ok=True)
        cntr = self.__count_chords(self.config.chords_folder, num_chords)
        chord_to_index = dict()
        chord_to_index[settings.unknown_chord_tag] = 0
        for chord, _ in cntr:
            chord_to_index[chord] = len(chord_to_index)
        index_to_chord = {v: k for k, v in chord_to_index.items()}
        pickle.dump(chord_to_index, open(self.config.dict_path.joinpath(self.config.chord_dict_name), 'wb'))
        pickle.dump(index_to_chord, open(self.config.dict_path.joinpath(self.config.index_dict_name), 'wb'))

    def save_chord_index_sequence(self) -> None:
        chord_to_index, _ = self.__get_chord_dict()
        self.config.chords_index_folder.mkdir(exist_ok=True)
        for chords_file in self.config.chords_folder.rglob('*.pickle'):
            midi_functions.chords_to_index_save(chords_file, self.config.chords_index_folder, chord_to_index)

    def __get_shift(self, scale):
        diatonic_scales, harmonic_scales, melodic_scales, blues_scales = self.__get_scales()
        if scale in diatonic_scales:
            return diatonic_scales.index(scale)
        #    elif scale in harmonic_scales:
        #        return harmonic_scales.index(scale)
        #    elif scale in melodic_scales:
        #        return melodic_scales.index(scale)
        else:
            return 'other'

    def __get_chord_dict(self) -> tuple[dict, dict]:
        chord_to_index = pickle.load(open(self.config.dict_path.joinpath(self.config.chord_dict_name), 'rb'))
        index_to_chord = pickle.load(open(self.config.dict_path.joinpath(self.config.index_dict_name), 'rb'))
        return chord_to_index, index_to_chord

    @staticmethod
    def __get_scales() -> tuple:
        # get all scales for every root note
        diatonic_scale = tuple((0, 2, 4, 5, 7, 9, 11))
        diatonic_scales = []
        for i in range(0, 12):
            diatonic_scales.append(tuple(np.sort((np.array(diatonic_scale) + i) % 12)))

        harmonic_scale = tuple((0, 2, 4, 5, 8, 9, 11))
        harmonic_scales = []
        for i in range(0, 12):
            harmonic_scales.append(tuple(np.sort((np.array(harmonic_scale) + i) % 12)))

        melodic_scale = tuple((0, 2, 4, 6, 8, 9, 11))
        melodic_scales = []
        for i in range(0, 12):
            melodic_scales.append(tuple(np.sort((np.array(melodic_scale) + i) % 12)))
        blues_scale = tuple((0, 3, 5, 6, 7, 10))
        blues_scales = []
        for i in range(0, 12):
            blues_scales.append(tuple(np.sort((np.array(blues_scale) + i) % 12)))

        return diatonic_scales, harmonic_scales, melodic_scales, blues_scales

    @staticmethod
    def __count_chords(chords_folder, num_chords) -> list:
        chord_cntr = Counter()
        for path, subdirs, files in os.walk(chords_folder):
            for name in files:
                _path = path.replace('\\', '/') + '/'
                _name = name.replace('\\', '/')
                chords = pickle.load(open(_path + _name, 'rb'))
                for chord in chords:
                    if chord in chord_cntr:
                        chord_cntr[chord] += 1
                    else:
                        chord_cntr[chord] = 1
        return chord_cntr.most_common(n=num_chords - 1)
