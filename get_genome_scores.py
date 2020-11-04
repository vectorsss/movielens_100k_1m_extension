#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 04.11.2020 02:08
# @Author  : Zhao Chi
# @Email   : dandanv5@hotmail.com
# @File    : get_genome_scores.py
# @Software: PyCharm
import sys
import pandas as pd
import numpy as np
import pickle
from get_movies_metadata import load_links

DATA_DIR = './data/'
BASE_DATA_DIR = './data/ml-25m/'


def load_base_data():
    """
    Load Base data from BASE DATA, ml-25 and ml-20m are both available. Change BASE_DATA_DIR to choose different DATA.
    Returns:
        genome_scores: DataFrame ['movieId', 'tagId', 'relevance']
        links: DataFrame ('movieId': int, 'imdbId': str, 'tmdbId': str)
    """
    genome_scores = pd.read_csv(BASE_DATA_DIR + 'genome-scores.csv')
    dtypes_links = {'movieId': int, 'imdbId': str, 'tmdbId': str}
    links = pd.read_csv(BASE_DATA_DIR + 'links.csv', converters=dtypes_links)
    return genome_scores, links


def id_map(links_origin, links_base):
    """
    mapping movie_id from target data to movieId from base data
    Returns:
        dict: origin movie Id to base movie Id mapping
        blackList: no mapping movie imdbId list
    """
    dic = {}
    blackList = []
    for i, imdbId in enumerate(links_origin['imdbId']):
        idx = np.where(links_base['imdbId'] == imdbId)
        try:
            dic[links_origin['movie_id'][i]] = links_base['movieId'][idx[0][0]]
        except IndexError:
            print('Can not mapping this movie, imdbId is:', imdbId)
            blackList.append(imdbId)
    return dic, blackList


def dropper(dic: dict, score: pd.DataFrame):
    """
    Drop from score['movieId'] not in dic.values()
    Args:
        dic: origin Id to base Id mapping
        score: DataFrame, ['movieId', 'tagId', 'relevance']

    Returns:
        dropped score
    """
    indices = pd.Int64Index([])
    for i in list(dic.values()):
        indices = indices.append(score[score['movieId'] == i].index)
    score = score.iloc[indices]
    return score


if __name__ == '__main__':
    fname = 'ml-100k'
    genome_scores, links_baseData = load_base_data()
    try:
        fname = sys.argv[1]
        if fname not in ['ml-100k', 'ml-1m']:
            raise ValueError('Dataset name not recognized: ' + fname)
    except IndexError:
        pass
    links = load_links(fname)
    dic, blackList = id_map(links, links_baseData)
    with open(DATA_DIR + fname + '/movieId_map.pkl', 'wb') as f:
        pickle.dump(dic, f)
    with open(DATA_DIR + fname + '/blackList.pkl', 'wb') as f:
        pickle.dump(blackList, f)
    genome_scores = dropper(dic, genome_scores)
    genome_scores.to_csv(DATA_DIR + fname + '/genome_scores.csv', index=None)