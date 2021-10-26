import speech_recognition as sr
import pyttsx3, pandas as pd
from translate import Translator

df=pd.read_csv('datasets/language-codes.csv')
lang2=input('Language for Speech Input: ').title()

index = df.index
condition = df['language'] == lang2
code_index = index[condition].tolist()
ci = code_index[0]
lang_code = df['alpha2'].iloc[ci]
#print(lang_code)

recognizer=sr.Recognizer()
engine=pyttsx3.init()

with sr.Microphone() as source:
    print('Speak anything')
    try:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio=recognizer.listen(source)

        result=recognizer.recognize_google(audio, language=lang_code)#'gu')
        #print(recognizer.recognize_sphinx(audio))
        print('You said: ',result)

        trans = Translator(from_lang=lang_code,to_lang='en')
        trans_text = trans.translate(result)
        print('Translated speech: ',trans_text)
    except:
        print('Sorry could not recognise your voice correctly')

# def trans():
#     lan_ip=input('Type the language code you want to translate')
#     tranlator=google_translator()
#     tranlated_text=tranlator.translate(str(result),lang_tgt=str(lan_ip))
#     print(tranlated_text)
#     engine.say(str(tranlated_text))
#     engine.runAndWait()
#
#
# trans()
