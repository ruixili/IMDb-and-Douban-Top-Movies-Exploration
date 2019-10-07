'''
CAPP30122 W'19: Douban_wordcloud

Code writer: Ruixi Li
Team: Ellen Hsieh, Tianxin Zheng, Ruixi Li
'''

import sys
import json
import re
import bs4
import time
import requests
import pandas as pd
import csv
import douban_crawler 
import douban_wordcloud
import imdb_crawler
import imdb_wordcloud

#exe_xpath = '/home/student/geckodriver'

def go(movie_name, if_translate, exe_xpath):
    '''
    Generate word cloud for input movies.
    '''
    douban_review = douban_crawler.find_one_review(movie_name)
    douban_wordcloud.generate_single_wordcloud(douban_review, if_translate)
    

    imdb_review = imdb_crawler.find_one_review(movie_name, exe_xpath)
    imdb_wordcloud.generate_one_word_cloud(imdb_review)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python3 {} <movie_name> <if_eng(boolean)>".format(
            sys.argv[0]))
        sys.exit(1)

    go(sys.argv[1], sys.argv[2], sys.argv[3])
