'''
CAPP30122 W'19: Douban_wordcloud

Code writer: Ruixi Li
Team: Ellen Hsieh, Tianxin Zheng, Ruixi Li
'''
import sys
import json
import time
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from googletrans import Translator
import pandas as pd
import jieba


def generate_all_wordcloud(reviews_file, eng=False, savefig=False):
    '''
    Generate Chinese and English wordclouds of reviews from douban website
    '''
    stopwords = read_stopword('ChineseStopwords.txt')
    reviews_df = pd.read_csv(reviews_file)
    reviews_df.columns = ['Movie Title', 'Score', 'Review']

    movie_reviews = reviews_df.groupby('Movie Title')
    for movie, info in movie_reviews:
        single_movie_review = ''
        for review in info['Review']:
            single_movie_review += ' ' + review
        single_movie_list = jieba.lcut(single_movie_review)
        single_movie_list = [word for word in single_movie_list\
                             if word not in stopwords and word != ' ']
        top100_tuple = find_top_k(single_movie_list)
        top100_dict = generate_topk_dict(top100_tuple, eng)
        generate_wordcloud(top100_dict, eng, savefig, movie)


def generate_single_wordcloud(douban_review, eng):
    '''
    Generate wordcloud for single movie.
    '''
    stopwords = read_stopword('ChineseStopwords.txt')
    single_movie_list = jieba.lcut(douban_review)
    single_movie_list = [word for word in single_movie_list\
                         if word not in stopwords and word != ' ']
    top100_tuple = find_top_k(single_movie_list)
    top100_dict = generate_topk_dict(top100_tuple, eng)
    generate_wordcloud(top100_dict, eng)


def read_stopword(file_path):
    '''
    Read the chinese stopword file.
    '''
    stopwords = pd.read_csv(file_path, header=None, delimiter="\t",
                    quoting=3, error_bad_lines=False).loc[:,0].tolist()
    return stopwords


def cmp_to_key(mycmp):
    '''
    Convert a cmp= function into a key= function
    From: https://docs.python.org/3/howto/sorting.html
    '''
    # Resource: CAPP30121 pa3 util.py
    class KeyComparison:
        '''
        Comparison key class
        '''
        def __init__(self, obj, *args):
            self.obj = obj

        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return KeyComparison

def cmp_count_tuples(t0, t1):
    '''
    Compare pairs using the second value as the primary key and the
    first value as the secondary key.  Order the primary key in
    non-increasing order and the secondary key in non-decreasing
    order.

    Inputs:
        t0: pair
        t1: pair

    Returns: -1, 0, 1

    Sample uses:
        cmp(("A", 3), ("B", 2)) => -1

        cmp(("A", 2), ("B", 3)) => 1

        cmp(("A", 3), ("B", 3)) => -1

        cmp(("A", 3), ("A", 3))
    '''
    # Resource: CAPP30121 pa3 util.py
    (key0, val0) = t0
    (key1, val1) = t1
    if val0 > val1:
        return -1
    elif val0 < val1:
        return 1
    elif key0 < key1:
        return -1
    elif key0 > key1:
        return 1
    return 0

def count_items(items):
    '''
    Counts each distinct item (entity) in a list of items

    Inputs:
        items: list of items (must be hashable/comparable)

    Returns: list (item, number of occurrences).
    '''
    # Resource: CAPP30121 pa3 util.py
    count_items ={}
    l = []
    for x in items:
        if x:
            count_items[x] = count_items.get(x, 0) + 1
    for key, val in  count_items.items():
        l.append((key, val))
    return l

def sort_count_pairs(l):
    '''
    Sort pairs using the second value as the primary sort key and the
    first value as the seconary sort key.

    Inputs:
       l: list of pairs.

    Returns: list of key/value pairs
    '''
    # Resource: CAPP30121 pa3 util.py
    return sorted(l, key=cmp_to_key(cmp_count_tuples))

def find_top_k(items, k=100):
    '''
    Find the K most frequently occurring items

    Inputs:
        items: list of items (must be hashable/comparable)
        k: a non-negative integer

    Returns: sorted list of the top K tuples

    '''
    # Resource: CAPP30121 pa3 util.py
    err_msg = "In find_top_k, k must be a non-negative integer"
    assert k >= 0, err_msg

    top100_tuples = sort_count_pairs(count_items(items))
    if len(items) >= k:
        top100_tuples = top100_tuples[:k]
    return top100_tuples


def generate_topk_dict(top100_tuples, eng):
    """
    Generate a dictionary which maps word to frequency.
    """
    top100_dict = {}
    translator = Translator()
    for (key, val) in top100_tuples:
        if eng:
            key = translator.translate(key).text
        top100_dict[key] = val
    return top100_dict


def generate_wordcloud(top100_dict, eng, savefig=False, figname='wordcloud'):
    """
    Generate a word cloud of the specified video category.
    """
    if eng:
        eng_stopwords = list(STOPWORDS)
        eng_stopwords.append(["movie", "film", "helpful", "character", "first",\
                "make", "even", "think", "really", "permalink", "time", "know",\
                "people", "way", "found", "see", "juror", "say", "much", "scene",\
                "many", "thing", "story", "sign", "vote", "made", "character",\
                'one', 'not', 'no', 'All', 'watch', 'will', 'review', 'still'])
        wc = WordCloud(font_path=None,
                       background_color="white",
                       width=1000, height=1000, mode='RGBA',
                       scale=.5, stopwords=eng_stopwords, contour_width=0).\
                       generate_from_frequencies(top100_dict)
    else:
        wc = WordCloud(font_path='simhei.ttf',
                       background_color="white",
                       width=1000, height=1000, mode='RGBA',
                       scale=.5, contour_width=0).\
                       generate_from_frequencies(top100_dict)
    plt.imshow(wc)
    plt.axis("off")
    if savefig:
        if eng:
            figname += '_English'
        plt.savefig("douban_word_cloud_image/{}.png".format(figname))
    plt.show()

