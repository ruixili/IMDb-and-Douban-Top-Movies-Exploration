import pandas as pd
import numpy as np
import csv
from ast import literal_eval
import seaborn as sns
import matplotlib.pyplot as plt

def write_rating_csv(input_file):
    '''
    Write the rating csv for later usage.
    '''
    movie_info = pd.read_csv('imdb_douban_movie_info.csv')
    with open('movie_attributes.csv', 'w') as output_csv:
        writer = csv.writer(output_csv)
        writer.writerow(['No.', 'Movie Title', 'IMDb Rating', 'Douban Rating',\
                        'IMDb - Douban Rating', 'Release Date', 'Genre',\
                        'Director', 'Star']) 
        for i, row in movie_info.iterrows():
            print(i)
            genres = row[3]
            if ',' in genres:
                genres = literal_eval(genres)
            else:
                genres = [genres]
                print(genres)
            directors = row[5]
            if ',' in directors:
                directors = literal_eval(directors)
            else:
                directors = [directors]            
            stars = row[6]
            if ',' in stars:
                stars = literal_eval(stars)
            else:
                stars = [stars]

            rating_difference = row[2] - row[7]

            for genre in genres:
                for director in directors:
                    for star in stars:
                        new_row = ([row[0], row[1], row[2], row[7], round(rating_difference,1),
                                    row[4], genre, director, star])
                        writer.writerow(new_row)

def generate_movie_attributes(attributes):
    info = pd.read_csv('movie_attributes.csv')
    for attr in attributes:  
        attr_df = pd.DataFrame({'count': info.groupby(attr).size()}).reset_index()
        sort_attr_df = attr_df.sort_values(by='count', ascending=False)[:10]
        sns.factorplot(x='count', y=attr, data=sort_attr_df, kind='bar',\
                       size=5, aspect=5, palette='coolwarm')
        plt.show()
#        plt.savefig("movie_attributes/{}.png".format(attr))


