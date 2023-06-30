from pathlib import Path

import settings
import numpy as np
from utils import midi_functions
import _pickle as pickle
import os
import sys
from collections import Counter


class MidiDataPreprocessor:
    def __init__(self, source_folder: Path, tempo_shift_folder: Path, histo_folder_1: Path, key_shifted_folder: Path,
                 shifted_histo_folder: Path, piano_roll_folder: Path, song_histo_folder: Path, chords_folder: Path,
                 chords_index_folder: Path, dict_path: Path, chord_dict_name: str, index_dict_name: str,
                 sampling_frequency: int):
        self.source_folder = source_folder
        self.tempo_shift_folder = tempo_shift_folder
        self.histo_folder_1 = histo_folder_1
        self.key_shifted_folder = key_shifted_folder
        self.histo_folder_2 = shifted_histo_folder
        self.piano_roll_folder = piano_roll_folder
        self.song_histo_folder = song_histo_folder
        self.chords_folder = chords_folder
        self.chords_index_folder = chords_index_folder
        self.dict_path = dict_path
        self.chord_dict_name = chord_dict_name
        self.index_dict_name = index_dict_name
        self.sampling_frequency = sampling_frequency

    def note_histogram_of_all_songs(self):
        histo = [0] * 128
        for path, subdirs, files in os.walk(self.tempo_shift_folder):
            for name in files:
                _path = path.replace('\\', '/') + '/'
                _name = name.replace('\\', '/')
                pianoroll = midi_functions.get_pianoroll(_name, _path, self.sampling_frequency)
                histo += np.sum(pianoroll, axis=1)
        return histo

    def get_scales(self):
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

    def get_shift(self, scale):
        diatonic_scales, harmonic_scales, melodic_scales, blues_scales = self.get_scales()
        if scale in diatonic_scales:
            return diatonic_scales.index(scale)
        #    elif scale in harmonic_scales:
        #        return harmonic_scales.index(scale)
        #    elif scale in melodic_scales:
        #        return melodic_scales.index(scale)
        else:
            return 'other'

    def shift_midi_files(self):
        for path, subdirs, files in os.walk(self.song_histo_folder):
            for name in files:
                _path = path.replace('\\', '/') + '/'
                _name = name.replace('\\', '/')
                tempo_path = self.tempo_shift_folder + _path[len(self.song_histo_folder):]
                target_path = self.key_shifted_folder + _path[len(self.song_histo_folder):]
                song_histo = pickle.load(open(_path + _name, 'rb'))
                key = midi_functions.histo_to_key(song_histo, settings.NOTES_IN_A_KEY)
                shift = self.get_shift(key)
                _name = _name[:-7]
                if shift != 'other':
                    if not os.path.exists(target_path):
                        os.makedirs(target_path)
                    try:
                        midi_functions.shift_midi(shift, _name, tempo_path, target_path)
                    except (ValueError, EOFError, IndexError, OSError, KeyError, ZeroDivisionError) as e:
                        exception_str = 'Unexpected error in ' + name + ':\n', e, sys.exc_info()[0]
                        print(exception_str)

    def count_scales(self):
        # get all scales for every root note
        diatonic_scales, harmonic_scales, melodic_scales, blues_scales = self.get_scales()

        scale_cntr = Counter()
        other_cntr = Counter()
        for path, subdirs, files in os.walk(self.song_histo_folder):
            for name in files:
                _path = path.replace('\\', '/') + '/'
                _name = name.replace('\\', '/')
                song_histo = pickle.load(open(_path + _name, 'rb'))
                key = midi_functions.histo_to_key(song_histo, settings.NOTES_IN_A_KEY)
                if key in diatonic_scales:
                    scale_cntr['diatonic'] += 1

                elif key in harmonic_scales:
                    scale_cntr['harmonic'] += 1

                elif key in melodic_scales:
                    scale_cntr['melodic'] += 1
                elif key[:-1] in blues_scales:
                    scale_cntr['blues'] += 1
                else:
                    scale_cntr['other'] += 1
                    other_cntr[key] += 1
        return scale_cntr, other_cntr

    def count_keys(self):
        key_cntr = Counter()
        for path, subdirs, files in os.walk(self.song_histo_folder):
            for name in files:
                _path = path.replace('\\', '/') + '/'
                _name = name.replace('\\', '/')
                song_histo = pickle.load(open(_path + _name, 'rb'))
                key = midi_functions.histo_to_key(song_histo, settings.NOTES_IN_A_KEY)
                if key in key_cntr:
                    key_cntr[key] += 1
                else:
                    key_cntr[key] = 1
        return key_cntr

    def save_song_histo_from_histo(self):
        for path, subdirs, files in os.walk(self.histo_folder_1):
            for name in files:
                _path = path.replace('\\', '/') + '/'
                _name = name.replace('\\', '/')
                target_path = self.song_histo_folder + _path[len(self.histo_folder_1):]
                if not os.path.exists(target_path):
                    os.makedirs(target_path)
                midi_functions.load_histo_save_song_histo(_name, _path, target_path)

    def save_index_from_chords(self):
        chord_to_index, index_to_chords = self.get_chord_dict()
        for path, subdirs, files in os.walk(self.chords_folder):
            for name in files:
                _path = path.replace('\\', '/') + '/'
                _name = name.replace('\\', '/')
                target_path = self.chords_index_folder + _path[len(self.chords_folder):]
                if not os.path.exists(target_path):
                    os.makedirs(target_path)
                midi_functions.chords_to_index_save(_name, _path, target_path, chord_to_index)

    def get_chord_dict(self):
        chord_to_index = pickle.load(open(self.dict_path + self.chord_dict_name, 'rb'))
        index_to_chord = pickle.load(open(self.dict_path + self.index_dict_name, 'rb'))
        return chord_to_index, index_to_chord

    def make_chord_dict(self, num_chords):
        cntr = self.count_chords(self.chords_folder, num_chords)
        chord_to_index = dict()
        chord_to_index[settings.UNKNOWN_CHORD] = 0
        for chord, _ in cntr:
            chord_to_index[chord] = len(chord_to_index)
        index_to_chord = {v: k for k, v in chord_to_index.items()}
        pickle.dump(chord_to_index, open(self.dict_path + self.chord_dict_name, 'wb'))
        pickle.dump(index_to_chord, open(self.dict_path + self.index_dict_name, 'wb'))
        return chord_to_index, index_to_chord

    def count_chords(self, chords_folder, num_chords):
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

    def count_chords2(self, chords_folder):
        chord_cntr = Counter()
        for path, subdirs, files in os.walk(chords_folder):
            for name in files:
                _path = path.replace('\\', '/') + '/'
                _path = _path.replace('/shifted', '')
                _name = name.replace('\\', '/')
                chords = pickle.load(open(_path + _name, 'rb'))
                for chord in chords:
                    if chord in chord_cntr:
                        chord_cntr[chord] += 1
                    else:
                        chord_cntr[chord] = 1
        return chord_cntr

    def save_chords_from_histo(self):
        for path, subdirs, files in os.walk(self.histo_folder_2):
            for name in files:
                _path = path.replace('\\', '/') + '/'
                _name = name.replace('\\', '/')
                target_path = self.chords_folder + _path[len(self.histo_folder_2):]
                if not os.path.exists(target_path):
                    os.makedirs(target_path)
                midi_functions.load_histo_save_chords(settings.NOTES_IN_A_CHORD, _name, _path, target_path)

    def save_histo_oct_from_midi_folder(self):
        print(self.tempo_shift_folder)
        for path, subdirs, files in os.walk(self.tempo_shift_folder):
            for name in files:
                _path = path.replace('\\', '/') + '/'
                _name = name.replace('\\', '/')
                target_path = self.histo_folder_1 + _path[len(self.tempo_shift_folder):]
                if not os.path.exists(target_path):
                    os.makedirs(target_path)
                try:
                    midi_functions.midi_to_histo_oct(settings.samples_per_bar, settings.half_steps_in_octave, settings.sampling_frequency, _name, _path, target_path)
                except (ValueError, EOFError, IndexError, OSError, KeyError, ZeroDivisionError) as e:
                    exception_str = 'Unexpected error in ' + name + ':\n', e, sys.exc_info()[0]
                    print(exception_str)

    def save_histo_oct_from_shifted_midi_folder(self):
        print(self.key_shifted_folder)
        for path, subdirs, files in os.walk(self.key_shifted_folder):
            for name in files:
                _path = path.replace('\\', '/') + '/'
                _name = name.replace('\\', '/')
                target_path = self.histo_folder_2 + _path[len(self.key_shifted_folder):]
                if not os.path.exists(target_path):
                    os.makedirs(target_path)
                try:
                    midi_functions.midi_to_histo_oct(settings.samples_per_bar, settings.half_steps_in_octave, settings.sampling_frequency, _name, _path, target_path)
                except (ValueError, EOFError, IndexError, OSError, KeyError, ZeroDivisionError) as e:
                    exception_str = 'Unexpected error in ' + name + ':\n', e, sys.exc_info()[0]
                    print(exception_str)

    def note_ind_folder(self):
        for path, subdirs, files in os.walk(self.key_shifted_folder):
            for name in files:
                _path = path.replace('\\', '/') + '/'
                _name = name.replace('\\', '/')
                target_path = self.piano_roll_folder + _path[len(self.key_shifted_folder):]
                if not os.path.exists(target_path):
                    os.makedirs(target_path)
                try:
                    midi_functions.save_note_ind(_name, _path, target_path, settings.sampling_frequency)
                except (ValueError, EOFError, IndexError, OSError, KeyError, ZeroDivisionError) as e:
                    exception_str = 'Unexpected error in ' + name + ':\n', e, sys.exc_info()[0]
                    print(exception_str)

    def change_tempo_of_midi_files(self):
        for path, subdirs, files in os.walk(self.source_folder):
            for name in files:
                _path = path.replace('\\', '/') + '/'
                _name = name.replace('\\', '/')
                target_path = self.tempo_shift_folder + _path[len(self.source_folder):]
                if not os.path.exists(target_path):
                    os.makedirs(target_path)
                try:
                    midi_functions.change_tempo(_name, _path, target_path)
                except (ValueError, EOFError, IndexError, OSError, KeyError, ZeroDivisionError, AttributeError) as e:
                    exception_str = 'Unexpected error in ' + name + ':\n', e, sys.exc_info()[0]
                    print(exception_str)
