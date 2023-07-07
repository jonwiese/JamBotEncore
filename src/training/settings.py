import settings

# train on key shifted dataset
shifted = True

# dimension of the chord embedding vector
chord_embedding_dim = 10
chord_lstm_hidden_layer_size = 512

samples_per_bar = settings.sampling_frequency * 2

num_chords = settings.num_chords

chord_n = settings.notes_per_chord

sampling_frequency = settings.sampling_frequency
