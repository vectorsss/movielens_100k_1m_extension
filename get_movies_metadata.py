#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 02.11.2020 21:01
# @Author  : Zhao Chi
# @Email   : dandanv5@hotmail.com
# @File    : get_movies_metadata.py
# @Software: PyCharm

import json
import sys
import pickle
import pandas as pd
import urllib.request
import urllib.parse
import numpy as np
from urllib.error import URLError

serviceUrl = 'http://www.omdbapi.com/?'
omdbApiKey = 'Your API Key'
apikey = '&apikey=' + omdbApiKey
DATA_DIR = './data/'


def load_links(fname):
    """
    Args:
        fname: str only from ['ml-100k', 'ml-1m']
    Returns:
        dataFrame: (movie_id, title, imdbId)
    """

    dtypes = {'movie_id': int, 'title': str, 'imdbId': str}
    ml100k_links_artificial = pd.read_csv(DATA_DIR + fname + '/links_artificial.csv', \
                                          converters=dtypes, usecols=[0, 1, 2])
    return ml100k_links_artificial


def search_movie(imdbId: str):
    """

    Args:
        imdbId: str, imdbId

    Returns:
        json obtained from OMDB api
    """
    try:
        url = serviceUrl + urllib.parse.urlencode({'i': imdbId}) + apikey
        uh = urllib.request.urlopen(url)
        data = uh.read()
        json_data = json.loads(data)

        if json_data['Response'] == 'False':
            print('Can not find this movie, corresponding imdbId is: ', imdbId)
        return json_data
    except URLError as e:
        print(f"ERROR: {e.reason}")
        return '<None>'


def fetch_metadata(fname, ml100k_links_artificial):
    """
    fetch metadata from omdb api
    Args:
        fname: str dataset name
        ml100k_links_artificial: dataFrame: (movie_id, title, imdbId)

    Returns:
        omdb_metadata: ((movie_id, title, imdbId), json) tuple
    """
    omdb_metadata = [((x[1]['movie_id'], x[1]['title'], x[1]['imdbId']), search_movie('tt' + x[1]['imdbId']))
                     for x in ml100k_links_artificial.iterrows()]
    with open(DATA_DIR + fname + '/metadata.pkl', 'wb') as f:
        pickle.dump(omdb_metadata, f)
    return omdb_metadata


def load_metadata(fname: str):
    with open(DATA_DIR + fname + '/metadata.pkl', 'rb') as f:
        omdb_metadata = pickle.load(f)
    return omdb_metadata


def json_dump(metadata: list):
    """
    Args:
        metadata: ((movie_id, title, imdbId), json) list

    Returns:
        dataFrame of metadata
    """
    json_list = [x[1] for x in metadata]
    df_metadata = pd.read_json(json.dumps(json_list))
    return df_metadata


def useless_detecter(df_metadata: pd.DataFrame, threshold=0.6):
    """
    Args:
        df_metadata: pd.DataFrame metadata for entire movies
        threshold: rate to dropout features

    Returns:
        list of useless feature

    """
    useless_count_df = df_metadata.replace('N/A', np.nan).isna().sum().to_frame(name='count')
    print(useless_count_df)
    length = len(df_metadata)
    threshold = length * threshold
    print('threshold:', int(threshold))
    # We would drop a feature in a threshold(default is 0.6)
    useless_features = [x[0] for x in useless_count_df.iterrows() if x[1]['count'] >= threshold]
    return useless_features


def run(fname, threshold=0.6, flag=1):
    """

    Args:
        fname: dataset name
        threshold: rate to dropout features
        flag: '1' load metadata from  'metadata.pkl', else fetch from OMDB api

    Returns:
        df_metadata: DataFrame metadata without useless features.

    """
    if flag:
        meta_data = load_metadata(fname)
    else:
        links = load_links(fname)
        meta_data = fetch_metadata(fname, links)

    df_metadata = json_dump(meta_data)
    useless_features = useless_detecter(df_metadata, threshold)
    print('useless_features: ', useless_features)
    df_metadata.drop(useless_features, axis=1, inplace=True)
    return df_metadata


if __name__ == '__main__':
    flag = 1
    threshold = 0.6
    try:
        fname = sys.argv[1]
    except IndexError:
        print('Please input the correct dataset name, only availiable for ml-1m and ml-100k.')
    try:
        flag = int(sys.argv[2])
    except IndexError:
        pass
    df_metadata = run(fname, threshold, flag)
    with open(DATA_DIR + fname + '/metadata_removed_useless.pkl', 'wb') as f:
        pickle.dump(df_metadata, f)
