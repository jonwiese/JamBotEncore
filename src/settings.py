over_sample_midi_files = True               # oversampling gives a better chord representation
over_sample_factor = 2

discretize_time = False
offset_time = False
discretization = 8
offset = 16


# Parameters to extract the pianorolls
sampling_frequency = 4                      # 4 for 8th notes
samples_per_bar = sampling_frequency * 2
half_steps_in_octave = 12

# Number of notes in extracted chords
notes_per_chord = 3
# Number of notes in a key
notes_per_key = 7
# Chord Vocabulary size
num_chords = 50

# for 120 bpm the midi tempo is 500'000
midi_bpm = 120

# unknown chord tag
unknown_chord_tag = '<unk>'
