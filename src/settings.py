# oversampling gives a better chord representation
over_sample_midi_files = True
over_sample_factor = 2

discretize_time = False
offset_time = False
discritezition = 8
offset = 16


# Parameters to extract the pianorolls

# sampling_frequency = 4 for 8th notes
sampling_frequency = 4
samples_per_bar = sampling_frequency * 2
half_steps_in_octave = 12
melody_fs = 4

# Number of notes in extracted chords
NOTES_IN_A_CHORD = 3
# Number of notes in a key
NOTES_IN_A_KEY = 7
# Chord Vocabulary size
num_chords = 50

# unknown chord tag
UNKNOWN_CHORD = '<unk>'

# Some Chords:
C = tuple((0, 4, 7))
Cm = tuple((0, 3, 7))
Csus4 = tuple((0, 5, 7))
Csus6 = tuple((0, 7, 9))
Dm = tuple((2, 5, 9))
D = tuple((2, 6, 9))
Dsus4 = tuple((2, 7, 9))
Em = tuple((4, 7, 11))
E = tuple((4, 8, 11))
F = tuple((0, 5, 9))
Fm = tuple((0, 5, 8))
G = tuple((2, 7, 11))
Gm = tuple((2, 7, 10))
Gsus4 = tuple((0, 2, 7))
Am = tuple((0, 4, 9))
Asus7 = tuple((4, 7, 9))
A = tuple((1, 4, 9))
H = tuple((3, 6, 11))
Hverm = tuple((2, 5, 11))
Hm = tuple((2, 6, 11))
B = tuple((2, 5, 10))
Es = tuple((3, 7, 10))
As = tuple((0, 3, 8))
Des = tuple((1, 5, 8))
Fis = tuple((1, 6, 10))
