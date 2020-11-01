#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 31.10.2020 22:42
# @Author  : Zhao Chi
# @Email   : dandanv5@hotmail.com
# @File    : find_movies_imdburl.py
# @Software: PyCharm
import pandas as pd
import numpy as np
import re
import urllib.parse
import urllib.request
import sys
from bs4 import BeautifulSoup

DATA_DIR = './data/'
BASE_FILES_DIR = './data/ml-25m/'


def find_imdbId_from_net(movieId, movieTitle, verbose=True):
    """
    Args:
        movieId: int
        title: string
    Returns: movie_url
    """
    # comparing to the result of imdb and google search,
    # I found google search is more accuracy than imdb.
    # So I scrape the missing imdbId from google search.
    domain = 'https://google.com/'
    movie_url = None
    search_url = domain + '/search?q=' + urllib.parse.quote_plus(movieTitle + ' imdb')
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 \
                                (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
    headers = {'user-agent': USER_AGENT}
    req = urllib.request.Request(search_url, headers=headers)
    with urllib.request.urlopen(req) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        try:
            movie_url = soup.find('div', class_='yuRUbf').a['href']
            if verbose:
                print(movieId, movieTitle, movie_url)
        except AttributeError:
            pass
    return movie_url


def find_imdbId_from_baseFiles(targetDataset, verbose=True):
    # use ml-25m - the lastest dataset as base dataset, 2020.10.31. the latest dataset is ml-25m
    ml_20m_movies = pd.read_csv(BASE_FILES_DIR + 'movies.csv', usecols=['movieId', 'title'])
    dtypes_link = {'id': np.int32, 'imdbId': str, 'tmdbId': str}
    ml_20m_links = pd.read_csv(BASE_FILES_DIR + 'links.csv', converters=dtypes_link)

    if targetDataset == 'ml-1m':
        movies_headers = ['movie_id', 'title']
        df = pd.read_csv(DATA_DIR + targetDataset + '/movies.dat', delimiter='::', header=None,
                         names=movies_headers, usecols=[0, 1], engine='python', encoding='latin1')
    elif targetDataset == 'ml-100k':
        movies_headers = ['movie_id', 'title']
        df = pd.read_csv(DATA_DIR + targetDataset + '/u.item', delimiter='|', header=None,
                         names=movies_headers, usecols=[0, 1], engine='python', encoding='latin1')
    else:
        raise ValueError('Dataset name not recognized: ' + targetDataset)

    # prepare to add imdb and tmdb id to origin movies
    df['imdbId'] = pd.NA
    df['tmdbId'] = pd.NA

    missing_id2title_dic = {}

    for i, t in enumerate(df['title']):
        if t in list(ml_20m_movies['title']):
            idx = np.where(ml_20m_movies['title'] == t)
            df['imdbId'][i], df['tmdbId'][i] = ml_20m_links['imdbId'][idx[0][0]], \
                                               ml_20m_links['tmdbId'][idx[0][0]]
        else:
            movie_url = find_imdbId_from_net(i + 1, t, verbose)
            if not movie_url or len(re.findall(r'https://www.imdb.com/', movie_url)) == 0:
                missing_id2title_dic[i] = t
                continue
            movie_url = re.findall(r'\S+tt\d+/', movie_url)[0]
            imdbId = re.findall(r'\d+', movie_url)
            # print(imdbId)
            df['imdbId'][i] = imdbId[0]
            idx = np.where(ml_20m_links['imdbId'] == imdbId[0])
            if len(idx[0]) > 0:
                df['tmdbId'][i] = ml_20m_links['tmdbId'][idx[0][0]]
    return df, missing_id2title_dic


if __name__ == '__main__':
    dataSet = sys.argv[1]
    verbose = sys.argv[2]
    df, missing_id2title_dic = find_imdbId_from_baseFiles(dataSet, verbose)
    print(len(missing_id2title_dic), missing_id2title_dic)
    df.to_csv(DATA_DIR + dataSet + '/links_artificial.csv', index=False)

    dtypes_link = {'movie_id': np.int32, 'title': str, 'imdbId': str, 'tmdbId': str}
    df = pd.read_csv(DATA_DIR + dataSet + '/links_artificial.csv', converters=dtypes_link,
                     usecols=['movie_id', 'imdbId'])
    df['imdbId'] = 'https://www.imdb.com/title/tt' + df['imdbId'] + '/'
    df.to_csv(DATA_DIR + dataSet + '/movie_urls.csv', index=False, header=None)
