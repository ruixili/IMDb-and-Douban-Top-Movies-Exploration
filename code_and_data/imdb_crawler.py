'''
CAPP30122 W'19: imdb_crawler

Code writer: Ellen Hsieh
Team: Ellen Hsieh, Tianxin Zheng, Ruixi Li
'''
import json
import csv
import re
import time
from urllib import request
from urllib.parse import urljoin, urlparse
from selenium import webdriver
import urllib3
import certifi
import bs4

# xpath of geckodriver: 
# exe_xpath = '/home/student/geckodriver'

def find_top_100_comments(exe_xpath, info_filename, comment_filename):
    '''
    Find the user comments of the top 100 movies on IMDb

    Inputs:
        exe_path: xpath of the webdriver
        info_filename: (str) a name of the movie info csv file
        comment_filename: (str) a name of comment csv file
    '''    
    starting_url = 'https://www.imdb.com/chart/top?ref_=nv_mv_250'    
    movies = get_top_movies(starting_url)[:100]
    
    movie_info_file = open(info_filename, "w")
    info_writer = csv.writer(movie_info_file)
    info_writer.writerow(['No.', 'Movie Title', 'Official Rating', 
                          'Type', 'Release Date', 'Director', 'Star'])
    
    comments_dict = {}
    for i, movie in enumerate(movies):
        link = movie.find_all('a')[0]['href']
        if not is_absolute(link):
            link = convert_relative_url_to_absolute(starting_url, link)
        movie_title, info, soup = get_movie_info(link)
        get_movie_image(soup, movie_title)
        review_page = find_review_page(link, soup)
        info_row = [str(i + 1)] + info
        info_writer.writerow(info_row)
        comments = find_reviews(review_page, exe_xpath)
        comments_dict[movie_title] = comments
    
    write_reviews_csv(comment_filename, comments_dict)
    
    movie_info_file.close()


def find_one_review(movie_title, exe_xpath):
    '''
    Get user comments by given movie title

    Inputs:
        movie_title: (str) a movie title
        exe_xpath: xpath of the webdriver 
    
    Returns: a str of all user comments
    '''
    starting_url = 'https://www.imdb.com/chart/top?ref_=nv_mv_250'  
    movies = get_top_movies(starting_url)

    movie_url = None
    for movie in movies:
        m_title = movie.find_all('img')[0]['alt']
        if movie_title == m_title:
            movie_url = movie.find_all('a')[0]['href']
            if not is_absolute(movie_url):
                movie_url = convert_relative_url_to_absolute(
                                        starting_url, movie_url)
            break

    if movie_url is None:
        return None

    _, _, soup = get_movie_info(movie_url)
    review_page = find_review_page(movie_url, soup)
    comments = find_reviews(review_page, exe_xpath)

    comments_str = ''
    for _, comment in comments:
        comments_str += '/n' + comment

    return comments_str


def convert_relative_url_to_absolute(current_url, relative_url):
    '''
    Convert a given relative url to an absolute url

    Inputs:
        current_url: a url of the given current page
        relative_url: a given relative url

    Returns: an absolute url
    '''
    return urljoin(current_url, relative_url)


def is_absolute(url):
    '''
    Judge whether the given url is an absolute url (boolean)
    '''
    return bool(urlparse(url).netloc)


def get_top_movies(starting_url):
    '''
    Get the top 100 movies on IMDb

    Input:
        starting_url: the url of IMDb webpage

    Returns: top 100 movies on IMDb
    '''
    pm = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                             ca_certs=certifi.where())

    html = pm.urlopen(url=starting_url, method="GET").data
    soup = bs4.BeautifulSoup(html, "lxml")
    movies = soup.find_all('td', class_="posterColumn")
    
    return movies


def get_movie_image(soup, movie_title):
    '''
    Get the image of the movie from the given BeautifulSoup object

    Inputs:
        soup: a BeautifulSoup object of a movie
        movie_title: a movie title
    '''
    img_url = soup.find_all('link', rel='image_src')[0]['href']
    f = open('{}.jpg'.format(movie_title), 'wb')
    f.write(request.urlopen(img_url).read())
    f.close()


def get_movie_info(movie_url):
    '''
    Get the movie information from the given url

    Inputs:
        movie_url: a url of a movie page

    Return: 
        (str)a movie title, a list of movie information, 
        and a BeautifulSoup objectof a movie
    '''    
    pm = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                             ca_certs=certifi.where())
    
    html = pm.urlopen(url=movie_url, method="GET").data
    soup = bs4.BeautifulSoup(html)
    json_ld = soup.find_all('script', type="application/ld+json")[0]
    t = json_ld.text
    json_acceptable_string = t.replace("'", "\"")
    movie_data = json.loads(json_acceptable_string)

    
    movie_title = movie_data['name']
    rating = movie_data['aggregateRating']['ratingValue']
    movie_type = movie_data["genre"]
    release_date = movie_data['datePublished']
    movie_actors = [a['name'] for a in movie_data['actor']]
    
    if isinstance(movie_data['director'], list):
        movie_director = [d['name'] for d in movie_data['director']]
    else:
        movie_director = movie_data['director']['name']
        
    movie_info = [movie_title, rating, movie_type, release_date, 
                    movie_director, movie_actors]
    
    return movie_title, movie_info, soup 


def find_review_page(movie_url, soup):
    '''
    Find the webpage for movie review

    Inputs:
        movie_url: a url of a movie page
        soup: a BeautifulSoup objectof a movie

    Returns: a url of user reviews webpage
    '''
    reviews = soup.find_all('div', class_="user-comments")
    links = reviews[0].find_all('a')
    
    for tag in links:
        if tag.has_attr('href'):
            if re.search('review', tag['href']):
                user_reviews = tag['href']
    
    if not is_absolute(user_reviews):
        user_reviews = convert_relative_url_to_absolute(
                                    movie_url, user_reviews)
    
    return user_reviews


def find_reviews(user_reviews, exe_path):
    '''
    Find out all the review comments on the reivew page

    Inputs:
        user_reviews: a url of user reviews webpage
        exe_path: xpath of the webdriver
    
    Returns: a list of comments with user rating
    '''
    browser = webdriver.Firefox(executable_path=exe_path)
    browser.get(user_reviews)
    time.sleep(1)
    
    no_of_loadmore = 4
    while no_of_loadmore:
        load_more_button = "//button[contains(@id, 'load-more-trigger')]"
        time.sleep(1)
        browser.find_element_by_xpath(load_more_button).click()
        time.sleep(1)
        no_of_loadmore -= 1
    
    soup = bs4.BeautifulSoup(browser.page_source)
    review_container = soup.find_all('div', class_="review-container")
    
    comments = []
    for review in review_container:
        comment = review.find_all('div', class_="content")[0]. \
                                            text.replace('\n', '')
        find_span = review.find_all('span')
        r = []
        for s in find_span:
            if re.search('rating-other-user-rating', str(s)):
                rating = find_span[0].text.strip()
                r = re.search('\\d+', rating).group()
        comments.append([r, comment])
        
    return comments


def write_reviews_csv(comment_filename, comments_dict):
    '''
    Write the given comments dictionary into csv file

    Inputs:
        comment_filename: (str) a name of comment csv file
        comments_dict: a dictionary of comments 
    '''   
    comments_file = open(comment_filename, "w")
    comments_writer = csv.writer(comments_file)
    
    comments_writer.writerow(['movie Title', 'User Rating', 'Comment'])

    for m_title, comments in comments_dict.items():
        for c in comments:
            row = [m_title] + c
            comments_writer.writerow(row)
    
    comments_file.close()
