from pathlib import Path

import settings
import numpy as np
import _pickle as pickle
import pretty_midi as pm
import mido


def change_tempo_of_midi_file(midi_file: Path, target_path: Path) -> None:
    midi = mido.MidiFile(midi_file)
    shifted_midi = mido.MidiFile()
    shifted_midi.ticks_per_beat = midi.ticks_per_beat
    for track in midi.tracks:
        new_track = mido.MidiTrack()
        for msg in track:
            new_msg = msg.copy()
            if new_msg.type == 'set_tempo':
                new_msg.tempo = mido.bpm2tempo(settings.midi_bpm)
            new_track.append(new_msg)
        shifted_midi.tracks.append(new_track)
    shifted_midi.save(target_path.joinpath(midi_file.name))


def pianoroll_to_histogram_per_bar(pianoroll: np.ndarray, samples_per_bar: int) -> np.ndarray:
    histogram_per_bar = np.zeros((pianoroll.shape[0], int(pianoroll.shape[1] / samples_per_bar)))
    for i in range(0, pianoroll.shape[1] - samples_per_bar + 1, samples_per_bar):
        histogram_per_bar[:, int(i / samples_per_bar)] = np.sum(pianoroll[:, i:i + samples_per_bar], axis=1)
    return histogram_per_bar


def shift_midi(semitones_to_shift: int, song_name: str, source_path: Path, target_path: Path) -> None:
    midi = pm.PrettyMIDI(str(source_path.joinpath(song_name)))
    for instrument in midi.instruments:
        if not instrument.is_drum:
            for note in instrument.notes:
                note.pitch -= semitones_to_shift
    midi.write(str(target_path.joinpath(song_name)))


def chords_to_index(chords: list, chord_to_index: dict) -> list:
    chords_index = []
    for chord in chords:
        if chord in chord_to_index:
            chords_index.append(chord_to_index[chord])
        else:
            chords_index.append(chord_to_index[settings.unknown_chord_tag])
    return chords_index


def chords_to_index_save(chords_file: Path, chords_index_folder: Path, chord_to_index: dict) -> None:
    chords = pickle.load(open(chords_file, 'rb'))
    chords_index = chords_to_index(chords, chord_to_index)
    pickle.dump(chords_index, open(chords_index_folder.joinpath(chords_file.name), 'wb'))


def song_histogram_to_key(song_histogram: np.ndarray, key_n: int) -> tuple:
    most_played_notes_per_song = song_histogram.argsort(axis=0)[-key_n:]
    most_played_notes_per_song.sort()
    return tuple(most_played_notes_per_song)


def bar_histogram_to_chords(histogram_per_bar: np.ndarray, notes_per_chord: int) -> list:
    most_played_notes_per_bar = histogram_per_bar.argsort(axis=0)[-notes_per_chord:]
    chords = []
    for i in range(0, most_played_notes_per_bar.shape[1]):
        chord = []
        for note in most_played_notes_per_bar[:, i]:
            if histogram_per_bar[note, i] != 0:
                chord.append(note)
        chord.sort()
        chords.append(tuple(chord))
    return chords


def pianoroll_to_note_index(pianoroll: np.ndarray) -> list[tuple]:
    note_index = []
    for i in range(0, pianoroll.shape[1]):
        step = []
        for j, note in enumerate(pianoroll[:, i]):
            if note != 0:
                step.append(j)
        note_index.append(tuple(step))
    return note_index


def load_histo_save_song_histo(histogram_per_bar_file: Path, song_histogram_path: Path) -> None:
    histogram_per_bar = pickle.load(open(histogram_per_bar_file, 'rb'))
    histogram_of_song = np.sum(histogram_per_bar, axis=1)
    pickle.dump(histogram_of_song, open(song_histogram_path.joinpath(histogram_per_bar_file.name), 'wb'))


def chord_histogram_to_chords(notes_per_chord: int, chord_histogram_path: Path, chords_path: Path) -> None:
    chord_histogram = pickle.load(open(chord_histogram_path, 'rb'))
    chords = bar_histogram_to_chords(chord_histogram, notes_per_chord)
    pickle.dump(chords, open(chords_path.joinpath(chord_histogram_path.name), 'wb'))


def squash_octaves(histogram_per_bar: np.ndarray, semitones_in_octave: int) -> np.ndarray:
    squashed_histogram = np.zeros((semitones_in_octave, histogram_per_bar.shape[1]))
    for i in range(0, histogram_per_bar.shape[0] - semitones_in_octave + 1, semitones_in_octave):
        squashed_histogram = np.add(squashed_histogram, histogram_per_bar[i:i + semitones_in_octave])
    return squashed_histogram


def midi_to_histo_oct(samples_per_bar: int, semitones_in_octave: int, fs: int, midi_file: Path, histogram_path: Path) -> None:
    pianoroll = get_pianoroll(midi_file, fs)
    histogram_per_bar = pianoroll_to_histogram_per_bar(pianoroll, samples_per_bar)
    histogram_per_bar_squashed_octaves = squash_octaves(histogram_per_bar, semitones_in_octave)
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


def get_pianoroll(midi_file: Path, fs: int) -> np.ndarray:
    pianoroll = get_notes(midi_file, fs)
    for i, _ in enumerate(pianoroll):
        for j, _ in enumerate(pianoroll[i]):
            if pianoroll[i, j] != 0:
                pianoroll[i, j] = 1
    return pianoroll


def get_notes(midi_file: Path, fs: int) -> np.ndarray:
    midi = pm.PrettyMIDI(str(midi_file))
    if settings.over_sample_midi_files:
        pianoroll = over_sample(midi)
    else:
        pianoroll = midi.get_piano_roll(fs=fs)
    return pianoroll
