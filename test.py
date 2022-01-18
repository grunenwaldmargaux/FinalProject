import os
from os import listdir
from os.path import isfile, join
import wave
import librosa

print(os.path.join(os.path.abspath('Import_Audio/'+listdir('Import_Audio')[0])))