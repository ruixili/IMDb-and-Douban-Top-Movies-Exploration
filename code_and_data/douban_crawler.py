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

def find_top_100_comments(input_file):
    '''
    Find reviews for top 100 movies in IMDb.
    '''
    imdb_movie_info = pd.read_csv(input_file)
    movies_list = imdb_movie_info['Movie Title']
    movie_review_dict = {}
    douban_rating_dict = {}
    for i, m_title in enumerate(movies_list):
        row_num = i + 1
        print('crawling', row_num, 'movie')
        movie_url = get_url_in_douban(m_title)
        douban_rating_dict, single_movie_review = info_and_review(movie_url,\
                                                  douban_rating_dict, row_num)
        movie_review_dict[m_title] = single_movie_review
    write_rating_csv(input_file, douban_rating_dict)
    write_reviews_csv(movie_review_dict)


def find_one_review(movie_name):
    '''
    Generate reviews for single movie.
    '''
    douban_movie_url = get_url_in_douban(movie_name)
    douban_review_list = find_reviews(douban_movie_url)
    single_movie_review = ''
    for (rating, review) in douban_review_list:
        single_movie_review += ' ' + review
    return single_movie_review

def get_url_in_douban(movie_name):
    '''
    Search the movie name in douban and find the url.
    '''
    search_movie_name = '+'.join(movie_name.split())
    base_url = 'https://www.douban.com/search?cat=1002&q='
    search_url = base_url + search_movie_name
    soup = get_soup(search_url)
    tags = soup.find_all('div', class_='result')
    movie_url = tags[0].find_all('a')[1]['href']
    return movie_url


def info_and_review(movie_url, douban_rating_dict, row_num):
    '''
    Scrape the movie info(rating) and reviews.
    '''
    soup = get_soup(movie_url)

    #rating
    rating_tag = soup.find_all('div', class_='rating_self clearfix')
    rating = soup.find_all('strong', class_='ll rating_num')[0].text
    if not rating:
        rating = 'na'
    douban_rating_dict[row_num] = rating

    #review
    single_movie_review = find_reviews(r.url)

    return douban_rating_dict, single_movie_review


def find_reviews(movie_url):
    '''
    Find individual reviews and scores.
    '''
    comments_list = []
#   For top 100    
#    num_page_to_craw = 6
#   For single movie
    num_page_to_craw = 2
    page_crawled = 0
    while page_crawled < num_page_to_craw:
        time.sleep(2)
        if page_crawled == 0:
            review_url = movie_url + "comments?sort=new_score&status=P"
        else:
            page_str = 20 * (page_crawled - 1)
            review_url = movie_url + "comments?" + "start=" + str(page_str)\
                         + "&limit=20&" + "sort=new_score&status=P"
        soup = get_soup(review_url)
        tags = soup.find_all('div', class_='comment-item')
        for tag in tags:
            rating = re.findall(r'allstar*[0-9]*', str(tag))
            if rating:
                rating = rating[0][-2:-1]
            comment = tag.find_all('span', class_='short')
            if comment:
                comment = comment[0].text
            if rating or comment:
                comments_list.append((rating, comment))
        page_crawled += 1
        print('crawled', page_crawled, 'page in douban')
    return comments_list

def write_reviews_csv(movie_review_dict):
    '''
    Write the reviews csv for later usage.
    '''
    f = open('douban_movie_review.csv', "w")
    writer = csv.writer(f)

    for m_title, single_movie_review in movie_review_dict.items():
        for (rating, review) in single_movie_review:
            writer.writerow([m_title, rating, review])
    f.close()

def write_rating_csv(input_file, douban_rating_dict):
    '''
    Write the rating csv for later usage.
    '''
    with open(input_file, 'r') as input_csv:
        with open('imdb_douban_movie_info.csv', 'w') as output_csv:
            reader = csv.reader(input_csv)
            writer = csv.writer(output_csv)
            for i, row in enumerate(reader):
                if i == 0:
                    row.append('Douban Official Rating')
                    writer.writerow(row)
                else:
                    row.append(douban_rating_dict.get(i, 0))
                    writer.writerow(row)

def get_soup(url):
    '''
    Get the soup object of url.
    '''
    r = requests.get(url)
    text = r.text.encode('utf-8')
    soup = bs4.BeautifulSoup(text, 'html.parser')
    return soup

if __name__ == "__main__":
    usage = "python3 douban_crawler.py"
    input_file = "imdb_movie_info.csv"
    find_top_100_comments(input_file)

