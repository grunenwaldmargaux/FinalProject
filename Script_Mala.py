from google.cloud import speech
import librosa
from pydub import AudioSegment
import soundfile as sf
import os
from os import listdir
from os.path import isfile, join
import io
import pandas as pd
import wave


def main_Mala():
    def My_file():
        #Affiche le fichier présent dans le dossier "Import_Audio et créer une variable dessus"
        Audio_to_treat = listdir('Import_Audio')[0]

        #Import du fichier audio
        filename = 'Import_Audio/'+Audio_to_treat
        y, sr = librosa.load(filename)

        return Audio_to_treat, filename, y, sr

    Audio_to_treat, filename, y, sr = My_file()

    #---------------------------------------------------------------------------------------------------------
    #Creation de la fonction qui va Transcrire notre texte avec les timestamp
    def Transcription():
        
        #Adresse de la clé Google API
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "Key_Google_API/key_Google.json"
        
        # Creates google client
        client = speech.SpeechClient()

        # Full path of the audio file
        file_name = os.path.join(os.path.abspath('Import_Audio/'+Audio_to_treat))

        #Loads the audio file into memory
        with io.open(file_name, "rb") as audio_file:
            content = audio_file.read()
            audio = speech.RecognitionAudio(content=content)

        #Get the channel
        with wave.open(file_name, "rb") as wave_file:
            channels = wave_file.getnchannels()
            
        #Config
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            audio_channel_count=channels,
            language_code="en-US",
            enable_word_time_offsets=True,
        )

        # Sends the request to google to transcribe the audio
        response = client.recognize(request={"config": config, "audio": audio})

        Text = []
        Start = []
        End = []
        

        for result in response.results:
            alternative = result.alternatives[0]

            Transcription_audio_to_text = alternative.transcript


            for word_info in alternative.words:
                word = word_info.word
                start_time = word_info.start_time
                end_time = word_info.end_time
            
                Text.append(word)
                Start.append(start_time.total_seconds())
                End.append(end_time.total_seconds())

            #del file_name, audio_file, content, wave_file, channels
                
            return Text, Start, End, Transcription_audio_to_text
    #---------------------------------------------------------------------------------------------------------
    #Lancement de la transcription
    Text, Start, End, Transcription_audio_to_text = Transcription()

    #---------------------------------------------------------------------------------------------------------
    #Transformation de l'output en pandas dataframe
    def Transformation():
        df = {'Texte':Text,'Start':Start, 'End': End}
        df = pd.DataFrame(df)
        #---------------------------------------------------------------------------------------------------------
        #Import du fichier des vulgarités en FR
        df2 = pd.read_csv('Big_words/English_big_words.csv')
        #---------------------------------------------------------------------------------------------------------
        #On récupère l'index des vulgarités du dataset
        #Les gros mots peuvent être composés jusqu'à 3 ou 4 mots donc il faut qu'on analyse toutes ces séquences
        idx_Big_Words = []
        for i in range(len(df['Texte'])):
            if i < (len(df['Texte']) - 3):
                texte = df['Texte'][i] +' ' + df['Texte'][i+1] +' ' + df['Texte'][i+2] +' ' + df['Texte'][i+3] 
                
                for j in range(len(df2['Key_words'])):
                    if df2['Key_words'][j] in texte :
                        idx_Big_Words.append(i)
                        idx_Big_Words = list(set(idx_Big_Words))
                        idx_Big_Words.sort()
        
        return df, df2, idx_Big_Words, texte

    df, df2, idx_Big_Words, texte = Transformation()
    #---------------------------------------------------------------------------------------------------------
    #Selectionner le bon indice du dataframe où on va insérer notre audio de "BIP" car on ne peut pas le faire sur chacun des indices (on perdrait de l'audio)
    def following_values(liste):

        Final_liste = []   

        for i in range(len(liste)-1):
            if (liste[i + 1] - 1) != (liste[i]):
                Final_liste.append(idx_Big_Words[i])
        Final_liste.append(liste[-1])
        return Final_liste

    #---------------------------------------------------------------------------------------------------------
    #Ajout des indices 0 et du dernier indice du dataframe dans le cas où ils n'existerait pas de mots vulgaires en début et fin de séquence
    def Split_idx():
        idx_to_split = following_values(idx_Big_Words)


        if idx_to_split[0] != 0:
            idx_to_split.insert(0,0)

        if idx_to_split[-1] != (len(df)-1):
            idx_to_split.append(len(df)-1)

        return idx_to_split

    #---------------------------------------------------------------------------------------------------------
    #Fonction permettant de splitter l'audio sur 2 secondes
    from pydub import AudioSegment
    import math

    #Définition de la classe avec l'adresse des fichiers
    class SplitWavAudio():
        def __init__(self, folder, filename):
            self.folder = folder
            self.filename = filename
            self.filepath = folder + '/' + filename
            
            self.audio = AudioSegment.from_wav(self.filepath)
        
        #Fonction pour retourner la durée de l'audio
        def get_duration(self):
            return self.audio.duration_seconds
        
       

        def Clean_audio(self):
            bip_sound = AudioSegment.from_wav("Bip_sound/bip-sound.wav") #Son de BIP à ajouter
            
            colonne1_df = 1 #Permet d'alterner sur les colonnes du dataframe (début ou fin vulgarité)
            colonne2_df = 1
            
            Audio_list = []
            
            for i in range(len(idx_to_split)-1):
                t1 = df.iloc[idx_to_split[i] , colonne1_df] * 1000
                
                if i != len(idx_to_split)-2:  #Si c'est la dernière piste à analyser cette condition va modifier la colonne (colonne2_df)
                    t2 = df.iloc[idx_to_split[i+1] , colonne2_df] * 1000
                
                else: 
                    t2 = df.iloc[idx_to_split[i+1] , 2] * 1000
                            
                split_audio = self.audio[t1:t2]
                            
                Audio_list.append(split_audio)
                
                if i != len(idx_to_split)-2:  #Si c'est la dernière piste audio cette condition ne va pas ajouter de bip
                    Audio_list.append(bip_sound)
                
                colonne1_df = 2 #Permet de changer la colonne sélectionnée du dataframe (début ou fin vulgarité)            
            
            combined_sound = sum(Audio_list)

            Path_Audio = "Export_Audio/{}".format(Audio_to_treat)
            combined_sound.export(Path_Audio, format="wav")
            
            print('Your File is Fuc.. euuh.. incredibly clean sorry :)')

            return Path_Audio

            
    def GetPathAudio():
        Test_cleaning = SplitWavAudio('Import_Audio', Audio_to_treat)
        Path_Audio1 = Test_cleaning.Clean_audio()
        return Path_Audio1

    if idx_Big_Words != []:
        idx_to_split = Split_idx()
        Path_Audio1 = GetPathAudio()
        keep_output_final = True

    else:
        keep_output_final = False
        Path_Audio1 = ""
        print("Nothing to clean")

    return keep_output_final, Path_Audio1, Transcription_audio_to_text

