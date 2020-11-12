#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 06.11.2020 14:30
# @Author  : zhaochi
# @Email   : dandanv5@hotmail.com
# @File    : remove_duplicate.py
# @Software: PyCharm

import pickle
import sys
import pandas as pd
import numpy as np
from get_movies_metadata import load_links
from get_movies_metadata import json_dump, useless_detecter

DATA_DIR = './data/'


def dup_detecteor(fname):
    """
    Args:
        fname:

    Returns:
        dupDataDic: index-movieId from origin data
    """
    links = load_links(fname)
    dupIdx = np.where(links.duplicated('imdbId') == True)[0]
    dupDataDic = {i: links['movie_id'][i] for i in dupIdx}
    return dupDataDic


def load_data_as_df(fname: str):
    """
    Args:
        fname: dataset name

    Returns:
        ratings, movies, users: DataFrame
    """
    if fname == 'ml-100k':
        files = ['/u.data', '/u.item', '/u.user']
        # ratings data
        sep = '\t'
        rating_headers = ["user_id", "movie_id", "rating", "timestamp"]
        dtypes = {
            'user_id': np.int32, 'movie_id': np.int32,
            'rating': np.float32, 'timestamp': np.float64}
        ratings = pd.read_csv(DATA_DIR + fname + files[0], header=None, sep=sep, names=rating_headers,
                              converters=dtypes)
        # movies data
        sep = r'|'
        movies_headers = ['movie_id', 'title', 'release date', 'video release date',
                          'IMDb URL', 'unknown', 'Action', 'Adventure', 'Animation',
                          'Childrens', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy',
                          'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi',
                          'Thriller', 'War', 'Western']
        movies = pd.read_csv(DATA_DIR + fname + files[1], sep=sep, encoding='latin1', header=None,
                             names=movies_headers, engine='python')
        # users data
        sep = r'|'
        user_headers = ['user_id', 'age', 'gender', 'occupation', 'zip_code']
        users = pd.read_csv(DATA_DIR + fname + files[2], header=None, delimiter=sep,
                            names=user_headers, engine='python')
    elif fname == 'ml-1m':

        files = ['/ratings.dat', '/movies.dat', '/users.dat']
        # ratings data
        sep = r'\:\:'
        rating_headers = ["user_id", "movie_id", "rating", "timestamp"]
        dtypes = {
            'user_id': np.int32, 'movie_id': np.int32,
            'rating': np.float32, 'timestamp': np.float64}
        ratings = pd.read_csv(DATA_DIR + fname + files[0], header=None, delimiter=sep, names=rating_headers,
                              converters=dtypes, engine='python')
        # movies data
        sep = r'\:\:'
        movies_headers = ['movie_id', 'title', 'genre']
        movies = pd.read_csv(DATA_DIR + fname + files[1], sep=sep, header=None,
                             names=movies_headers, encoding='latin1', engine='python')

        # users data
        sep = r'\:\:'
        users_headers = ['user_id', 'gender', 'age', 'occupation', 'zip-code']
        users = pd.read_csv(DATA_DIR + fname + files[2], sep=sep, header=None,
                            names=users_headers, engine='python')

    return ratings, movies, users


def remover_from_origin_data(fname: str, dupDataDic: dict):
    ratings, movies, users = load_data_as_df(fname)
    # if fname == 'ml-100k':
    # remove duplicate from ratings
    print('Length of origin rating data', len(ratings))
    indices = pd.Index([])
    for i in dupDataDic.values():
        indices = indices.append(ratings[ratings['movie_id'] == i].index)
    ratings = ratings.drop(index=indices, axis=0)
    print('Length of no duplicate rating data', len(ratings))
    # remove duplicate from movies
    print('Length of origin movies data', len(movies))
    idx = list(dupDataDic.keys())
    movies.drop(index=idx, axis=0, inplace=True)
    print('Length of no duplicate rating data', len(movies))
    # remove duplicate from users
    print('Length of origin users data', len(users))
    users.drop_duplicates(subset=['user_id'], inplace=True)
    print('Length of no duplicate users data', len(users))
    return ratings, movies, users


if __name__ == '__main__':
    fname = 'ml-100k'
    try:
        fname = sys.argv[1]
    except IndexError:
        pass
    dupDataDic = dup_detecteor(fname)
    ratings, movies, users = remover_from_origin_data(fname, dupDataDic)

    # remapping data
    # fname movies id to new movies id mapping
    moviesIdMapping = {movie_id: i for i, movie_id in enumerate(movies['movie_id'])}
    with open(DATA_DIR + fname + '/oldMovieId_to_remappedId.pkl', 'wb') as f:
        pickle.dump(moviesIdMapping, f)
    movies['movie_id'] = list(map(lambda x: moviesIdMapping[x], movies['movie_id']))
    ratings['movie_id'] = list(map(lambda x: moviesIdMapping[x], ratings['movie_id']))
    # dic_reversed: ml-25m id to fname movie id mapping
    with open(DATA_DIR + fname + '/reversed_movieId_map.pkl', 'rb') as f:
        dic_reversed = pickle.load(f)
    genome_scores = pd.read_csv(DATA_DIR + fname + '/genome-scores.csv')
    genome_scores['movieId'] = list(map(lambda x: moviesIdMapping[dic_reversed[x]], genome_scores['movieId']))

    # Old user id to new user id mapping
    usersIdMapping = {user_id: i for i, user_id in enumerate(users['user_id'])}
    with open(DATA_DIR + fname + '/oldUserId_to_remappedId.pkl', 'wb') as f:
        pickle.dump(usersIdMapping, f)
    users['user_id'] = list(map(lambda x: usersIdMapping[x], users['user_id']))
    ratings['user_id'] = list(map(lambda x: usersIdMapping[x], ratings['user_id']))

    # remapping links_artificial.csv, movie_urls.csv and movie_posters.csv
    url_header = ['movieId', 'url']
    url_df = pd.read_csv(DATA_DIR + fname + '/movie_urls.csv', header=None, names=url_header)
    url_df.drop_duplicates('url', inplace=True)
    url_df['movieId'] = list(map(lambda x: moviesIdMapping[x], url_df['movieId']))

    poster_header = ['movieId', 'poster_url']
    poster_df = pd.read_csv(DATA_DIR + fname + '/movie_posters.csv', header=None, names=poster_header)
    poster_df.drop_duplicates('poster_url', inplace=True)
    poster_df['movieId'] = list(map(lambda x: moviesIdMapping[x], poster_df['movieId']))

    links = load_links(fname)
    links.drop_duplicates('imdbId', inplace=True)
    links['movie_id'] = list(map(lambda x: moviesIdMapping[x], links['movie_id']))

    # save as csv
    ratings.to_csv(DATA_DIR + fname + '/Dropped_ratings.csv', index=False)
    movies.to_csv(DATA_DIR + fname + '/Dropped_movies.csv', index=False)
    users.to_csv(DATA_DIR + fname + '/Dropped_users.csv', index=False)

    genome_scores.to_csv(DATA_DIR + fname + '/remapped-genome-scores.csv', index=False)
    url_df.to_csv(DATA_DIR + fname + '/remapped_movie_urls.csv', index=False, header=False)
    poster_df.to_csv(DATA_DIR + fname + '/remapped_movie_posters.csv', index=False, header=False)
    links.to_csv(DATA_DIR + fname + '/remapped_links_artificial.csv', index=False)

    # remapping metadata
    with open(DATA_DIR + fname + '/metadata.pkl', 'rb') as f:
        metadatas = pickle.load(f)
    metadatas = [[list(x), y] for x, y in metadatas]
    print(len(metadatas))
    remapped_metadatas = []
    for item in metadatas:
        try:
            item[0][0] = moviesIdMapping[item[0][0]]
            item[0] = tuple(item[0])
            remapped_metadatas.append(item)
        except KeyError:
            pass
    with open(DATA_DIR + fname + '/remapped_metadata.pkl', 'wb') as f:
        pickle.dump(remapped_metadatas, f)
    metadatas_df = json_dump(remapped_metadatas)
    useless_features = useless_detecter(metadatas_df)
    metadatas_df.drop(useless_features, axis=1, inplace=True)
    with open(DATA_DIR + fname + '/remapped_metadata_removed_useless.pkl', 'wb') as f:
        pickle.dump(metadatas_df, f)