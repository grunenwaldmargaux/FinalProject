import streamlit as st
import os
import matplotlib.pyplot as plt
import wordcloud
from wordcloud import WordCloud
from PIL import Image
import numpy as np
import Script_PiYo 
from Script_PiYo import main #Fonction main du Script 2 (Pierre et Youssef)
import shutil
import Script_Mala
from Script_Mala import main_Mala



#Remove all files from Export directory at the beggining of the process
dir = 'Export_Audio'
for f in os.listdir(dir):
    os.remove(os.path.join(dir, f))


st.write("""
# Hacensor
Déposez vos fichiers audio ! Si c'est trash on censure pour vous :)
""")

st.image("img/Logo.png", width=150)

col1, col2, col3 = st.columns(3)


uploaded_file = st.file_uploader("Importer un fichier", type=["wav", "mp3", "m4a"])
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    st.audio(uploaded_file, format='audio')

    with open(os.path.join("Import_Audio",uploaded_file.name),"wb") as f:
        f.write(uploaded_file.getbuffer())

    #Lancement du script de transformation de mp3 m4a .. à .wav
    exec(open("to_wav.py").read())
    print("towav script")

    #Lancement du script de Margot
    exec(open("Script_Margot.py").read())
    print("Margot script")


    #Lancement du script de Pierre et Youssef -> Lancement de la fonction main
    output_final, Message = main()

    if output_final >= 1:

        #Import Script Malamine -> Lancement de la transcription
        try:
            keep_output_final, Path_Audio1, Transcription_audio_to_text = main_Mala()
            if keep_output_final == False:
                output_final = 0
        except NameError:
            pass    
        
    if output_final == 0 :
        image = Image.open('img/Option0.jpg')
        Message2 = "On ne voit pas de vulgarités ici ! OMG Vous êtes un saint ! Soyez Béni ! "

    elif output_final == 1 :
        image = Image.open('img/Option1.jpg')
        Message2 = "C'est que vous êtes un peu vulgaire vous ! On va nettoyer tout ça  !"

    elif output_final == 2 :
        image = Image.open('img/Option2.jpg')
        Message2 = "Attention ! Ton langage ne me plaît pas trop ! Je vais nettoyer tout ça"

    elif output_final == 3 :
        image = Image.open('img/Option3.jpg')
        Message2 = "Quelle vulgarité ! Tu l'auras bien cherché ! Tu as 5 secondes pour télécharger le fichier propre ou ça va mal se passer !"

    if output_final != 0:
        st.image(image)
        st.write(Message2)
        st.audio(Path_Audio1, format='audio')
        st.download_button("Télécharger", Path_Audio1)


        st.write("""-------------------------------------- Transcription de votre audio --------------------------------------""")
        st.write(Transcription_audio_to_text)


        # generate a word cloud excluding stopwords from the text file

        micro_mask = np.array(Image.open("img/micro.png"))

        st.write("Nuage de Mots")
        st.set_option('deprecation.showPyplotGlobalUse', False)

        wd = wordcloud.WordCloud(background_color="white", contour_width=1, stopwords=[], max_words=50, mask=micro_mask)
        # Generate wordcloud 
        cloud = wd.generate(Transcription_audio_to_text)

        # Show plot
        plt.imshow(cloud)
        plt.axis("off")
        plt.show()
        st.pyplot()

    else:
        st.write(Message2)
        st.image(image)

        st.write("""-------------------------------------- Transcription de votre audio --------------------------------------""")
        st.write(Transcription_audio_to_text)


        # generate a word cloud excluding stopwords from the text file

        micro_mask = np.array(Image.open("img/micro.png"))

        st.write("Nuage de Mots")
        st.set_option('deprecation.showPyplotGlobalUse', False)

        wd = wordcloud.WordCloud(background_color="white", contour_width=1, stopwords=[], max_words=50, mask=micro_mask)
        # Generate wordcloud 
        cloud = wd.generate(Transcription_audio_to_text)

        # Show plot
        plt.imshow(cloud)
        plt.axis("off")
        plt.show()
        st.pyplot()



else: 
    st.error('Veuillez déposer un fichier audio.')


import streamlit as st
import SessionState  # Assuming SessionState.py lives on this folder

session = SessionState.get(run_id=0)

if st.button("Recommencer"):
  session.run_id += 1


#Remove all files from import directory at the end of the process
dir = 'Import_Audio'
for f in os.listdir(dir):
    os.remove(os.path.join(dir, f))