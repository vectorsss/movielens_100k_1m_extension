# movielens extension for ml-100k and  ml-1m
---

## Background

Only [ml-100k](https://grouplens.org/datasets/movielens/100k/)  and [ml-1m](https://grouplens.org/datasets/movielens/1m/) include demographic information. But there is some missing information for movies, such as the IMDB id and TMDB id. To make my recommendation system perform well, I have to fetch the metadata for each movie. Movies may have the same title but only have one unique ID in TMDB or IMDB. Then the first step is to obtain the unique ID in those two different movie database.

First, I use the latest movielens dataset [MovieLens 25M Dataset](https://grouplens.org/datasets/movielens/latest/). From this dataset, I can get a part of these movies' id, but some are missing because some movie names are different in different datasets.

Second, I have to fill those missing value. The first method I tried to solve this problem is searching from [the IMDB website](https://www.imdb.com/), but the results are not always **right**, comparing to google search. Therefore, I decided to use google search to find those missing id.

Finally, scraping the posters from the IMDB links.


## Description for files in datasets

Except the origin item from [movielens](https://grouplens.org/datasets/movielens/), I build three files in './data/ml-100k' and './data/ml-1m'. (encoding='utf-8')

- **links_artificial.csv**: movie_id,title,imdbId,tmdbId
- **movie_urls.csv**: The movie_id to IMDB URL mapping.
- **movie_posters.csv**: The movie_id to poster URL mapping.

Only **links_artificial.csv** has the header.

The **img** folder in './data/ml-100k' and './data/ml-1m' is created by myself to store the scraped posters, named by movie_id. And the **log** folder is also created by myself, which is used to store the running log.

## Description for Scripts

- **get_movies_imdburl.py**: Find IMDB from base-files(ml-25m) and google. This script will build two files, the first two items, as I mentioned before, in the corresponding folder of the dataset.
- **get_movies_poster.py**: Scraping posters from the IMDB URLs, which are stored in movie_urls.csv. This script will create the last CSV file, and fetch the posters which are available present. Some missing value would be printed at the console or output in a log file, which is up to yourself.

Since I remove all useless files but keep the README file for each dataset, so you can clone this repository and run these script without prepare any data.

The full data you can find in the following links.

- ml-100k: https://grouplens.org/datasets/movielens/100k/
- ml-1m: https://grouplens.org/datasets/movielens/1m/
- ml-25m: https://grouplens.org/datasets/movielens/latest/

## Run it by yourself

1. Run **get_movies_imdburl.py** on the dataset ml-100k. The last flag **1** means verbuse=True.
    ```shell
    python get_movies_imdburl.py ml-100k 1
    ```
2. Run **get_movies_poster.py** on the dataset ml-100k output in a log file.
    ```shell
    python get_movies_poster.py ml-100k > ./data/ml-100k/log/missing\ posters.log 
    ```
Similarly, we can run these scripts on the dataset ml-1m by using the command below.

1. Run **get_movies_imdburl.py** on the dataset ml-1m.
    ```shell
    python get_movies_imdburl.py ml-1m 1
    ```
2. Run **get_movies_poster.py** on the dataset ml-1m output in a log file.
    ```shell
    python get_movies_poster.py ml-1m > ./data/ml-1m/log/missing\ posters.log 
    ```
## Acknowledgement

Thanks for this repo [movielens-posters](https://github.com/babu-thomas/movielens-posters).

##To-Do

- [ ] Scarping the metadata from TMDB or OMDB.
- [ ] Adding genome-tag and genome-scores to each movie.