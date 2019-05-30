import pandas as pd
import sqlite3
from collections import defaultdict

class DB:
    """Creates and manipulates a local sqlite database table"""

    def __init__(self, name='movie', source='movie_metadata.csv', database=":memory:"):
        """Initialize a new db in local memory from a csv and execute statements.
        If this were a larger, more-permanent project I would set this up in Postgres"""
        self.name = name
        self.source = source
        self.database = database
        self.connect()
        self.create()

    def connect(self):
        """Establish connection"""
        self.connection = sqlite3.connect(self.database)
        self.connected = True

    def create(self):
        """Uses a handy pandas shortcut to convert a database into a sql statement.
        Normally I would expect to declare column names and var types beforehand"""
        if not self.connected:
            self.connect()
        df = pd.read_csv(self.source)
        df.to_sql(self.name, self.connection, index=False, if_exists='replace')
        self.created = True

    def execute(self, statement = None):
        """Though I don't actually end up using this function, this how to execute
            statements on the instantiated class db"""
        if statement is None:
            """Get everything from the table created"""
            statement = "select * from {}".format(self.name)
        self.cursor = self.connection.cursor()
        return self.cursor.execute(statement)

    def __del__(self):
        """Closes connection when Class is deleted"""
        self.connection.close()
        self.connected = False


class IMDB:
    """A series of functions for analyzing IMDB movies, dataset available at
    https://www.kaggle.com/carolzhangdc/imdb-5000-movie-dataset/downloads/imdb-5000-movie-dataset.zip/1"""

    def __init__(self, conn, sql="SELECT * FROM movie;"):
        """With connection read sql statement into pandas dataframe"""
        self.conn = conn
        self.df = pd.read_sql(sql, self.conn)
        self.columns = list(self.df.columns)
        self.category = 'genre'

    def get_df(self, sql="SELECT * FROM movie;"):
        """Custom sql query statement on dataframe"""
        return pd.read_sql(sql, self.conn)

    def remove_null(self, cols_to_clean=['budget', 'gross']):
        """Since columns like budget and gross are only useful if not null
            this function removes all rows with null values in 'cols_to_clean'"""
        if self.category == 'pair':
            cols_to_clean = ['imdb_score','director_name','actor_1_name']
        return self.df.dropna(axis=0, subset=cols_to_clean)

    def split_vals(self, row):
        """Depending on aggregation category, this applies two custom splitting
            functions on row to make a list of values"""
        category = self.category
        if category == 'genre':
            return row.genres.split("|")
        elif category == 'actor':
            return filter(None, [row.director_name, row.actor_1_name, row.actor_2_name, row.actor_3_name])
        elif category == 'pair':
            l=[]
            l.append(str(row['director_name']+"|"+row['actor_1_name']))
            return l

    def aggregate(self, category='genre', metric_cols=None):
        """This function does two things while iterating row by row through dataset:
            1. Splits each row into separate dictionary keys
                (e.g. genre = 'Action|Comedy' => 'Action', 'Comedy')
            2. Aggregates metric columns by key

           Note: defaultdict is used in order to prevent looping through twice
            i.e. keys are created as they are updated
        """
        self.category = category
        if metric_cols is None:
            metric_cols = ['budget', 'gross']
        if self.category == 'pair':
            metric_cols = ['imdb_score']
        dd = defaultdict(lambda: defaultdict(int))
        profit_df = self.remove_null()
        for index, row in profit_df.iterrows():
            for item in self.split_vals(row):
                dd[item]['count'] += 1
                for metric in metric_cols:
                    dd[item][metric] += row[metric]
        self.aggregated_df = dd
        return dd

    def top_ten(self, category='genre'):
        """This function converts the defaultdict into a clean pandas dataframe"""
        dd = self.aggregate(category)
        df = pd.DataFrame.from_dict(dd, orient='index')
        cat = 'undefined_category'
        pt = 'undefined_profit'
        cols = [cat, 'count', 'budget', 'gross', pt]
        if self.category == 'genre':
            cat = 'genre'
            pt = 'profit_index'
            df[pt] = (df['gross'] - df['budget']) / df['budget']
            cols = [cat, 'count', 'budget', 'gross', pt]
            tt = df.sort_values(by=[pt], ascending=False).reset_index()
        elif self.category == 'actor':
            cat = 'actors_and_directors'
            pt = 'profit'
            df[pt] = df['gross'] - df['budget']
            cols = [cat, 'count', 'budget', 'gross', pt]
            tt = df.sort_values(by=[pt], ascending=False).reset_index()
        elif self.category == 'pair':
            cat = 'director_actor_pair'
            pt = 'avg_imdb_score'
            df[pt] = df['imdb_score']/df['count']
            cols = [cat, 'count', 'imdb_score', pt]
            df = df[df['count']>=3].sort_values(by=['avg_imdb_score'],ascending=False)
            tt = df.sort_values(by=[pt], ascending=False).reset_index()
        tt.columns = cols
        return tt.head(10)

    def metrics_by_year(self):
        """I was planning on this being a cool visual display of a few metrics by year,
            but decided just to leave it as a demonstration of a sql query not knowing
            in what format this code would be reviewed."""
        query = '''
            SELECT 
                title_year, 
                count(*) as count,
                avg(num_user_for_reviews) as avg_num_reviews,
                avg(imdb_score) as avg_imdb_score, 
                avg(gross) as avg_gross, 
                avg(budget) as avg_budget 
            FROM 
                movie
            WHERE
                title_year >= 1950
            GROUP BY
                title_year
            ORDER BY
                title_year
            ;'''
        return self.get_df(query)

