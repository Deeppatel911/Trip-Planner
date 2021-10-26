from gtts import gTTS
import os
import pandas as pd
from translate import Translator

df=pd.read_csv('datasets/language-codes.csv')
my_text=input('Enter text: ')
lang2=input('Target language for translation: ').title()

index = df.index
condition = df['language'] == lang2
code_index = index[condition].tolist()
ci = code_index[0]
lang_code = df['alpha2'].iloc[ci]
print(lang_code)

trans=Translator(to_lang=lang_code)
trans_text=trans.translate(my_text)
print(trans_text)

output=gTTS(text=trans_text,lang=lang_code,slow=False)
output.save('output.mp3')

os.system('start output.mp3')