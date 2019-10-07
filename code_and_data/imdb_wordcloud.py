'''
CAPP30122 W'19: imdb_wordcloud

Code writer: Tianxin Zheng
Team: Ellen Hsieh, Tianxin Zheng, Ruixi Li
'''

import numpy as np
import pandas as pd
from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")
imdb = pd.read_csv("imdb_reviews.csv")


# set stop words
stopwords = set(STOPWORDS)
stopwords.update(["movie", "film", "movie", "review", "helpful", "one", \
	              "character", "first", "make", "even", "think", "really",\
	              "will", "permalink", "time", "know", "people", "way", \
	              "found", "watch", "see", "juror", "say", "much", "scene",\
                  "many", "thing", "story", "sign", "vote", "made", "still",\
                   "character", "film"])


movies = imdb.groupby("movie Title")
for title, info in movies:
    text = ""
    for comment in info['Comment']:
        text += " " + comment
    wordcloud = WordCloud(stopwords=stopwords, max_words=100, \
        background_color="white", collocations=False, width=1000, \
        height=1000, mode="RGBA", contour_width=0.5).generate(text)
    #plt.imshow(wordcloud, interpolation='bilinear')
    #plt.axis("off")
    #plt.show()
    wordcloud.to_file("imdb_word_cloud_image/{}.png".format(title))

def generate_one_word_cloud(text):
    '''
    Generate English word cloud for IMDb reviews.
    Inputs:
        text: all the reviews for one moive.
    '''    
    wordcloud = WordCloud(stopwords=stopwords, max_words=100, \
        background_color="white", collocations=False, width=1000, 
        height=1000, mode="RGBA", contour_width=0.5).generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()
