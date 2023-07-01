# JamBotEncore
In this project I revisit my semester thesis\
__JamBot: Music Theory Aware Chord Based Generation of Polyphonic Music with LSTMs__ _(https://arxiv.org/abs/1711.07682)_ \
that led to a paper that was presented at ICTAI 2017.

__Jambot__ is an artificial neural network that generates MIDI music.
The music is generated in two steps. First, a chord LSTM predicts a chord progression.
A second LSTM then generates polyphonic music based on the predicted chord progression.



__JamBotEncore__ aims to:
- Refactor the original JamBot code to bring it up to current standards.
- Allow for experimentation with different machine learning models
(e.g. using transformers instead of LSTMs). 
- Allow for extension, experimentation and being creative. 
- Be used as sample application to experiment with software engineering technologies that I want to explore.


## Modules
### Preprocessing

This module processes the raw midi data, so it can be used to train the LSTMs.\
The preprocessing steps are:
1. Shift the tempo of all the midi files to 120 bmp
2. Create a histogram of which notes are played for each bar of every song
3. Create a histogram of which notes are played for each song
4. Shift all the notes of the midi files to the key of C major (or its relative A minor, which uses exactly the same notes)
5. Create a note-index pianoroll-representation of all the key and tempo shifted midi files
6. Create a histogram of which notes are played for each bar of every key shifted song
7. Extract a chord for each bar from histogram data
8. Make a chord dictionary that maps the 50 most used chords to an index
9. Create chord-index sequence for each song 


### Training

To do

### Generation

To do
