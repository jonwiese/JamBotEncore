from pathlib import Path

import settings
import numpy as np
import _pickle as pickle
import pretty_midi as pm
import mido


def shift_midi(shift: int, song_name: str, source_path: Path, target_path: Path) -> None:
    midi = pm.PrettyMIDI(str(source_path.joinpath(song_name)))
    for instrument in midi.instruments:
        if not instrument.is_drum:
            for note in instrument.notes:
                note.pitch -= shift
    midi.write(str(target_path.joinpath(song_name)))


def chords_to_index(chords: list, chord_to_index: dict) -> list:
    chords_index = []
    for chord in chords:
        if chord in chord_to_index:
            chords_index.append(chord_to_index[chord])
        else:
            chords_index.append(chord_to_index[settings.UNKNOWN_CHORD])
    return chords_index


def chords_to_index_save(chords_file: Path, chords_index_folder: Path, chord_to_index: dict) -> None:
    chords = pickle.load(open(chords_file, 'rb'))
    chords_index = chords_to_index(chords, chord_to_index)
    pickle.dump(chords_index, open(chords_index_folder.joinpath(chords_file.name), 'wb'))


def song_histogram_to_key(song_histogram: np.ndarray, key_n: int) -> tuple:
    max_n = song_histogram.argsort(axis=0)[-key_n:]
    max_n.sort()
    return tuple(max_n)


def histo_to_chords(histo, chord_n):
    max_n = histo.argsort(axis=0)[-chord_n:]
    chords = []
    for i in range(0, max_n.shape[1]):
        chord = []
        for note in max_n[:, i]:
            if histo[note, i] != 0:
                chord.append(note)
        chord.sort()
        chords.append(tuple(chord))
    return chords


def pianoroll_to_note_index(pianoroll):
    note_ind = []
    for i in range(0, pianoroll.shape[1]):
        step = []
        for j, note in enumerate(pianoroll[:, i]):
            if note != 0:
                step.append(j)
        note_ind.append(tuple(step))
    return note_ind


def load_histo_save_song_histo(histogram_file: Path, song_histogram_path: Path):
    histo = pickle.load(open(histogram_file, 'rb'))
    song_histo = np.sum(histo, axis=1)
    pickle.dump(song_histo, open(song_histogram_path.joinpath(histogram_file.name), 'wb'))


def chord_histogram_to_chords(chord_n: int, chord_histogram_path: Path, chords_path: Path) -> None:
    chord_histogram = pickle.load(open(chord_histogram_path, 'rb'))
    chords = histo_to_chords(chord_histogram, chord_n)
    pickle.dump(chords, open(chords_path.joinpath(chord_histogram_path.name), 'wb'))


def pianoroll_to_histogram_per_bar(pianoroll: np.ndarray, samples_per_bar: int) -> np.ndarray:
    # Make histogramm for every samples_per_bar samples
    histo_bar = np.zeros((pianoroll.shape[0], int(pianoroll.shape[1] / samples_per_bar)))
    for i in range(0, pianoroll.shape[1] - samples_per_bar + 1, samples_per_bar):
        histo_bar[:, int(i / samples_per_bar)] = np.sum(pianoroll[:, i:i + samples_per_bar], axis=1)
    return histo_bar


def squash_octaves(histo_bar: np.ndarray, octave: int) -> np.ndarray:
    histo_oct = np.zeros((octave, histo_bar.shape[1]))
    for i in range(0, histo_bar.shape[0] - octave + 1, octave):
        histo_oct = np.add(histo_oct, histo_bar[i:i + octave])
    return histo_oct


def midi_to_histo_oct(samples_per_bar: int, octave: int, fs: int, midi_file: Path, histogram_path: Path) -> None:
    pianoroll = get_pianoroll(midi_file, fs)
    histogram_per_bar = pianoroll_to_histogram_per_bar(pianoroll, samples_per_bar)
    histogram_per_bar_squashed_octaves = squash_octaves(histogram_per_bar, octave)
    pickle.dump(histogram_per_bar_squashed_octaves, open(histogram_path.joinpath(midi_file.name + '.pickle'), 'wb'))


def over_sample(midi_file: pm.PrettyMIDI) -> np.ndarray:
    pianoroll_double_sampled = midi_file.get_piano_roll(fs=settings.sampling_frequency * settings.over_sample_factor)
    pianoroll = []
    for i in range(0, pianoroll_double_sampled.shape[1], settings.over_sample_factor):
        vec = np.sum(pianoroll_double_sampled[:, i:(i + settings.over_sample_factor)], axis=1)
        pianoroll.append(vec)
    pianoroll = np.array(pianoroll)
    pianoroll = np.transpose(pianoroll)
    return pianoroll


def save_note_ind(midi_file: Path, target_path: Path, fs: int) -> None:
    midi = pm.PrettyMIDI(str(midi_file))
    if settings.over_sample_midi_files:
        pianoroll = over_sample(midi)
    else:
        pianoroll = midi.get_piano_roll(fs=fs)
    for i, _ in enumerate(pianoroll):
        for j, _ in enumerate(pianoroll[i]):
            if pianoroll[i, j] != 0:
                pianoroll[i, j] = 1
    note_index_pianoroll = pianoroll_to_note_index(pianoroll)
    pickle.dump(note_index_pianoroll, open(target_path.joinpath(midi_file.name + '.pickle'), 'wb'))


def get_notes(midi_file: Path, fs: int) -> np.ndarray:
    midi = pm.PrettyMIDI(str(midi_file))
    if settings.over_sample_midi_files:
        pianoroll = over_sample(midi)
    else:
        pianoroll = midi.get_piano_roll(fs=fs)
    return pianoroll


def get_pianoroll(midi_file: Path, fs: int) -> np.ndarray:
    pianoroll = get_notes(midi_file, fs)
    for i, _ in enumerate(pianoroll):
        for j, _ in enumerate(pianoroll[i]):
            if pianoroll[i, j] != 0:
                pianoroll[i, j] = 1
    return pianoroll


def myround(x, base) -> int:
    return int(base * round(float(x) / base))


def change_tempo_of_midi_file(midi_file: Path, target_path: Path) -> None:
    mid = mido.MidiFile(midi_file)
    new_mid = mido.MidiFile()
    new_mid.ticks_per_beat = mid.ticks_per_beat
    for track in mid.tracks:
        new_track = mido.MidiTrack()
        for msg in track:
            new_msg = msg.copy()
            if new_msg.type == 'set_tempo':
                new_msg.tempo = 500000
            if settings.discretize_time:
                print(msg.time)
                new_msg.time = myround(msg.time, base=mid.ticks_per_beat / (settings.discritezition / 4))
            if settings.offset_time:
                print((mid.ticks_per_beat / (settings.offset / 4)))
                new_msg.time = int(msg.time + mid.ticks_per_beat / (settings.offset))
            new_track.append(new_msg)
        new_mid.tracks.append(new_track)
    new_mid.save(target_path.joinpath(midi_file.name))
