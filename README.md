# movielens extension for ml-100k and  ml-1m
---

## Background

Only [ml-100k](https://grouplens.org/datasets/movielens/100k/)  and [ml-1m](https://grouplens.org/datasets/movielens/1m/) include demographic information. But there is some missing information for movies, such as the IMDB id and TMDB id. To make my recommendation system perform well, I have to fetch the metadata for each movie. Movies may have the same title but only have one unique ID in TMDB or IMDB. Then the first step is to obtain the unique ID in those two different movie database.

First, I use the latest movielens dataset [MovieLens 25M Dataset](https://grouplens.org/datasets/movielens/latest/). From this dataset, I can get a part of these movies' id, but some are missing because some movie names are different in different datasets.

Second, I have to fill those missing value. The first method I tried to solve this problem is searching from [the IMDB website](https://www.imdb.com/), but the results are not always **right**, comparing to google search. Therefore, I decided to use google search to find those missing id.

Finally, scraping the posters from the IMDB links.


## Description for files

Except the origin item from [movielens](https://grouplens.org/datasets/movielens/), I build some files in './data/ml-100k' and './data/ml-1m'. (encoding='utf-8')

- **links_artificial.csv**: movie_id,title,imdbId,tmdbId
- **movie_urls.csv**: The movie_id to IMDB URL mapping.
- **movie_posters.csv**: The movie_id to poster URL mapping.

Only **links_artificial.csv** has the header.

The **img** folder in './data/ml-100k' and './data/ml-1m' is created by myself to store the scraped posters, named by movie_id. And the **log** folder is also created by myself, which is used to store the running log.

**Note:** Under the **log** folder, you could see the the file 'missing poster.log' which include the following error. Because this movie *Wallace & Gromit: The Best of Aardman Animation (1996)* is removed from IMDB, but I found the poster on the Internet. So, you can see this in the **movie_posters.csv**. The corresponding movie ID is 114 and 720 in dataset ml-100k and ml-1m respectively.

> HTTPError: 404 114 https://www.imdb.com/title/tt0118114/

**Update**: For dataset *ml-1m* and *ml-100k*, I fetch those movies metadata from OMDB. You could see some new files in the corresponding folder.

- **metadata.pkl**: ((movie_id, title, imdbId), json) tuple
- **metadata_removed_useless.pkl**: DataFrame without useless features.

Also, under the **log** folder, you could see the output of the script *get_movies_metadata.py*. Including useless features and why they are useless.

**Update2**: For dataset *ml-1m* and *ml-100k*, I obtain the genome score from *ml-25*. You could see some new files in the corresponding folder.

- **genome-scores.csv**: Same as *ml-25* but remove redundant data. (movieId not in origin dataset)
- **blackList.pkl**: Some movies' IMDB ID those can not be found in *ml-25*.
- **movieId_map.pkl**: Origin ID to ml-25 ID mapping.

## Description for Scripts

- **get_movies_imdburl.py**: Find IMDB from base-files(ml-25m) and google. This script will build two files, the first two items, as I mentioned before, in the corresponding folder of the dataset.
- **get_movies_poster.py**: Scraping posters from the IMDB URLs, which are stored in movie_urls.csv. This script will create the last CSV file, and fetch the posters which are available present. Some missing value would be printed at the console or output in a log file, which is up to yourself.
- **get_movies_metadata.py**: Fetching the metadata from OMDB API. You have to upgrade your plan as a Patrons. I use a basic plan 1$/month. I stored my results in the corresponding dataset folder. Of course, you can run it by your self.
- **get_genome_scores.py**: Find the genome score from *ml-25m*, to run this script, you should unzip the file *genome-scores.csv.zip* in the corresponding folder. This script will generate three files. *genome-scores.csv*, *blackList.pkl* and *movieId_map.pkl*. Also the corresponding tag file is same as *ml-25*. So, I copy this directly.

Since I remove all useless files but keep the README file for each dataset, so you can clone this repository and run these script without prepare any data.

The full data you can find in the following links.

- ml-100k: https://grouplens.org/datasets/movielens/100k/
- ml-1m: https://grouplens.org/datasets/movielens/1m/
- ml-25m: https://grouplens.org/datasets/movielens/latest/

## Run it by yourself

1. Run **get_movies_imdburl.py** on the dataset ml-100k. The last flag **1** means verbose=True (print running details).
    ```shell
    python get_movies_imdburl.py ml-100k 1
    ```
2. Run **get_movies_poster.py** on the dataset ml-100k output in a log file.
    ```shell
    python get_movies_poster.py ml-100k > ./data/ml-100k/log/missing\ posters.log 
    ```
3. Run **get_movies_metadata.py** on the dataset ml-100k output in a log file.
    ```shell
    python get_movies_metadata.py ml-100k 0 > ./data/ml-100k/log/useless_features.log
    ```
4. Run **get_genome_scores.py** on the dataset ml-100k output in a log file.
    ```shell
    python get_genome_scores.py ml-100k > ./data/ml-100k/log/missing_genome_scores.log
    ```
**Note:** The flag *0* in step *3* means fetching the data from OMDB by yourself. You must input your APIKEY in the correct location(line 19) in *get_movies_metadata.py*. If you are supposed to use the file I fetched before. But generate the *metadata_removed_useless.pkl* with a different threshold(default=0.6), you should change the threshold in line 144 and remove the flag *0* or change it to *1*.

Similarly, we can run these scripts on the dataset ml-1m by using the command below.

1. Run **get_movies_imdburl.py** on the dataset ml-1m.
    ```shell
    python get_movies_imdburl.py ml-1m 1
    ```
2. Run **get_movies_poster.py** on the dataset ml-1m output in a log file.
    ```shell
    python get_movies_poster.py ml-1m > ./data/ml-1m/log/missing\ posters.log 
    ```
3. Run **get_movies_metadata.py** on the dataset ml-1m output in a log file.
    ```shell
    python get_movies_metadata.py ml-1m 0 > ./data/ml-1m/log/useless_features.log
    ```
4. Run **get_genome_scores.py** on the dataset ml-1m output in a log file.
    ```shell
    python get_genome_scores.py ml-1m > ./data/ml-1m/log/missing_genome_scores.log
    ```

## Acknowledgement

Thanks for this repo [movielens-posters](https://github.com/babu-thomas/movielens-posters).

## To-Do

- [x] Scarping the metadata from TMDB or OMDB.
- [x] Adding genome-tag and genome-scores to each movie.