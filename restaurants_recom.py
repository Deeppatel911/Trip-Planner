import pandas as pd
import numpy as np

df = pd.read_csv('dataset/yelp-dataset.csv', index_col=False)

from sklearn.feature_extraction.text import TfidfVectorizer

tfv = TfidfVectorizer(min_df=3, max_features=None,
                      strip_accents='unicode', analyzer='word', token_pattern=r'\w{1,}',
                      ngram_range=(1, 3),
                      stop_words='english')
tfv_matrix = tfv.fit_transform(df['categories'])

from sklearn.metrics.pairwise import sigmoid_kernel
sig = sigmoid_kernel(tfv_matrix, tfv_matrix)

indices = pd.Series(df.index, index=df['categories']).drop_duplicates()

def give_rec(categories, sig=sig):
  idx = indices[categories]

  sig_scores = list(enumerate(sig[idx]))

  sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)

  sig_scores = sig_scores[1:11]

  restaurent_indices = [i[0] for i in sig_scores]

  return df.iloc[restaurent_indices]

  
lst = ["Seafood", "Wine", "Mexican"]
index_list = []
for i in lst:
  index_list += (list(df[df['categories'].str.contains(i)].index))

index_list = list(set(index_list))

index_list = sorted(index_list)


rec_df = df.iloc[index_list]
rec_df.sort_values(by=['stars', 'review_count'], ascending=False)