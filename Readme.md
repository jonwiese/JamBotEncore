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



