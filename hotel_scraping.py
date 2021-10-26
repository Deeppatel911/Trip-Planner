# -*- coding: utf-8 -*-
"""Hotel_scraping.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xt_e7ABxst_lgVqN4-1dRmuM6Bfrr0Aw
"""

import requests as req
from bs4 import BeautifulSoup as sp

html = req.get('https://www.tripadvisor.ca/Hotels-g153339-Canada-Hotels.html')

bsobj = sp(html.content, 'lxml')

hotel = []
for name in bsobj.findAll('div', {'class': 'listing_title'}):
  hotel.append(name.text.strip())

hotel

ratings = []
for rating in bsobj.findAll('a', {'class': 'ui_bubble_rating'}):
  ratings.append(rating['alt'])

ratings

reviews = []
for review in bsobj.findAll('a', {'class': 'review_count'}):
  reviews.append(review.text.strip())

reviews

price = []
for p in bsobj.findall('div', {'class': 'price-wrap'}):
  price.append(p.text.replace('₹', '').strip())

price

import pandas as pd

hotel_df = pd.DataFrame.from_dict({'Hotel': hotel, 'Ratings': ratings, 
                                   'No_Of_Reviews': reviews, 'Price': price})





