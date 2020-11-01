#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 31.10.2020 17:48
# @Author  : Zhao Chi
# @Email   : dandanv5@hotmail.com
# @File    : get_movies_poster.py
# @Software: PyCharm
import csv
import urllib.request
import sys
from bs4 import BeautifulSoup
from urllib.error import HTTPError

DATA_DIR = './data/'

if __name__ == '__main__':
    fname = sys.argv[1]
    dataSets = ['ml-100k', 'ml-1m']
    if fname not in dataSets:
        raise ValueError('Dataset name not recognized: ' + fname)
    row_names = ['movie_id', 'movie_url']
    with open(DATA_DIR + fname + '/movie_urls.csv', 'r', newline='') as in_csv:
        reader = csv.DictReader(in_csv, fieldnames=row_names, delimiter=',')
        for row in reader:
            movie_id = row['movie_id']
            movie_url = row['movie_url']
            try:
                with urllib.request.urlopen(movie_url) as response:
                    html = response.read()
                    soup = BeautifulSoup(html, 'html.parser')
                    # Get url of poster image
                    try:
                        image_url = soup.find('div', class_='poster').a.img['src']
                        extension = '.' + image_url.split('.')[-1]
                        image_url = ''.join(image_url.partition('_')[0]) + extension
                        filename = DATA_DIR + fname + '/img/' + movie_id + extension
                        with urllib.request.urlopen(image_url) as response:
                            with open(filename, 'wb') as out_image:
                                out_image.write(response.read())
                            with open(DATA_DIR + fname + '/movie_posters.csv', 'a', newline='') as out_csv:
                                writer = csv.writer(out_csv, delimiter=',')
                                writer.writerow([movie_id, image_url])
                    # Ignore cases where no poster image is present
                    except AttributeError:
                        print("Movie {} has no poster image is present. Imdb url: {}".format(movie_id, movie_url))
            except HTTPError as e:
                print("HTTPError:", e.getcode(), movie_id, movie_url)
