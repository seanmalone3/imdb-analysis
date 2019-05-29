import pytest
from main import *

"""This file tests the functions in main.py using pytest
cd into directory then run:
$ pytest test.py -v -s
"""

def test_DB_init():
    db = DB()
    assert db.connected, "Could not connect to database"
    assert db.created, "Did not successfully create table"

def test_IMDB_init():
    conn = sqlite3.connect(":memory:")
    df = pd.read_csv('movie_metadata.csv')
    df.to_sql('movie', conn, index=False, if_exists='replace')
    imdb = IMDB(conn)
    assert imdb.columns == ['color',
                         'director_name',
                         'num_critic_for_reviews',
                         'duration',
                         'director_facebook_likes',
                         'actor_3_facebook_likes',
                         'actor_2_name',
                         'actor_1_facebook_likes',
                         'gross',
                         'genres',
                         'actor_1_name',
                         'movie_title',
                         'num_voted_users',
                         'cast_total_facebook_likes',
                         'actor_3_name',
                         'facenumber_in_poster',
                         'plot_keywords',
                         'movie_imdb_link',
                         'num_user_for_reviews',
                         'language',
                         'country',
                         'content_rating',
                         'budget',
                         'title_year',
                         'actor_2_facebook_likes',
                         'imdb_score',
                         'aspect_ratio',
                         'movie_facebook_likes'], "Database columns not as expected"

@pytest.fixture(scope='session')
def setup_IMDB():
    conn = sqlite3.connect(":memory:")
    df = pd.read_csv('movie_metadata.csv')
    df.to_sql('movie', conn, index=False, if_exists='replace')
    imdb = IMDB(conn)
    yield imdb

def test_IMDB_remove_null(setup_IMDB):
    clean_df = setup_IMDB.remove_null()
    assert clean_df.budget.count() == len(clean_df)
    assert clean_df.gross.count() == len(clean_df)

def test_IMDB_split_vals(setup_IMDB):
    for index, row in setup_IMDB.df.head(1).iterrows():
        assert setup_IMDB.split_vals(row,'genre') == row.genres.split("|"), "Failed genre split"
        assert list(setup_IMDB.split_vals(row,'actor')) == list(filter(None, [row.director_name, row.actor_1_name, row.actor_2_name, row.actor_3_name])), "Failed actor and director split"

def test_IMDB_aggregate(setup_IMDB):
    dd = setup_IMDB.aggregate('genre',['budget','gross'])
    assert list(dict(dict(dd)['Action']).keys()) == ['count', 'budget', 'gross'], "Dictionary keys not as expected"

def test_IMDB_top_ten_genre(setup_IMDB):
    tt = setup_IMDB.top_ten()
    assert list(tt) == ['genre', 'count', 'budget', 'gross', 'profit_index'], 'Output of columns not as expected'
    assert list(tt.genre) == ['Documentary',
                             'Music',
                             'Sport',
                             'Musical',
                             'Family',
                             'Short',
                             'Mystery',
                             'Romance',
                             'Biography',
                             'Fantasy'], "Order/name of genres not as expected"
    assert round(tt.profit_index.mean(),3) == 0.418

def test_IMDB_top_ten_actor(setup_IMDB):
    tt = setup_IMDB.top_ten('actor')
    assert list(tt) == ['actors_and_directors', 'count', 'budget', 'gross', 'profit'], 'Output of columns not as expected'
    assert list(tt.actors_and_directors) == ['Steven Spielberg',
                                             'Harrison Ford',
                                             'Scarlett Johansson',
                                             'Robert Downey Jr.',
                                             'Tom Hanks',
                                             'Jon Favreau',
                                             'Morgan Freeman',
                                             'George Lucas',
                                             'Bradley Cooper',
                                             'James Cameron'], "Order/name of actors and directors not as expected"
    assert round(tt.profit.sum(),-5) == 16695500000, "Profit for actors and directors not as expected"

def test_IMDB_metrics_by_year(setup_IMDB):
    mby = setup_IMDB.metrics_by_year()
    assert mby.title_year[:1].values[0] == 1950, "First year should be 1950"
    assert mby.title_year[-1:].values[0] == 2016, "Last year should be 2016"
    assert round(mby.avg_imdb_score.mean(),2) == 6.89, "IMDB Scores not accurate for 1950 - 2016"