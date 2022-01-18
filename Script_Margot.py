import pathlib
import pandas as pd
import subprocess
import sox
import soundfile as sf
import os
from os import listdir
from os.path import isfile, join
import wave
import librosa

def main_Margot():

  folder = pathlib.Path("Import_Audio")
  audio = [str(audio_path) for audio_path in list(folder.glob('*'))]

  for i in range(len(audio)):
    path = audio[i] 
    text = ' > Texte/Texte_from_audio' + str(i) + '.txt'
    model = 'deepspeech --model deepspeech-0.9.3-models.pbmm --scorer deepspeech-0.9.3-models.scorer --audio '
    path_script = model + path + text
    print(path_script)
    text_output = subprocess.run(str(path_script), shell=True, check=True)

  def TextToLabelise(text) :
      text = str(text).split()
      text = [text [x:x+50] for x in range(0, len(text),50)]
      return text

  df_complete = pd.DataFrame()


  for i in range(0, 1):
      df = pd.read_csv('Texte/Texte_from_audio{}.txt'.format(i), header=None)
      list_words = TextToLabelise(df[0][0])
      dataset = pd.DataFrame(data = [list_words]).T
      dataset['id'] = i
      df_complete = pd.concat([df_complete, dataset])

  df_complete = df_complete.rename(columns={0: "text"})
  df_complete = df_complete.reset_index().drop('index', axis = 1)
  df_complete['label'] = 0

  ## Best one <3

  bad_words = ['fuck', 'fucked', 'fucking', 'ass',
               'asshole', 'motherfucker', 'bitch',
               'bitchies', 'dick', 'dickhead', 'motherfucker',
               'pussy', 'cunt', 'shit', 'piss','bastard', 'shag', 'wanker',
               'bitchies', 'fuckwit', 'bullshit', 'nigga', 'nigger',
               'cocksucker', 'crap', 'goddamn', 'twat', 'arse',
               'tits', 'boobs','butt', 'damn', 'niggas', 'douchebag', 'suck',
               'fucker', 'slag', 'fucker', 'douche', 'pussycat', 'ship', 'as', 'faced']


  for index in range(len(df_complete)):
    if len(set(df_complete['text'][index]) & set(bad_words)):
      df_complete['label'][index] = 1
    else:
      df_complete['label'][index] = 0


  df_complete.to_csv('Texte/df_output_labelised.csv')

main_Margot()