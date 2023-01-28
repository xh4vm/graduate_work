
from pydantic import BaseSettings, Field


class Vertica(BaseSettings):
    """Class Vertica settings."""

    host: str = Field('127.0.0.1')
    port: int = Field(5433)
    user: str = Field('dbadmin')
    password: str = Field('')
    database: str = Field('docker')
    autocommit: bool = Field(True)

    class Config:
        env_prefix = 'VERTICA_'
        env_file = 'config/.env'


class Settings(BaseSettings):
    """Class main settings."""

    VERTICA = Vertica().parse_obj(Vertica().dict())
    DATASET_FOLDER: str
    DDL_FILE: str
    TRUNCATE_TABLE: bool = False
    CREATE_TABLE: bool = True
    BATCH_SIZE: int = 10
    DATASET_FILE_EXT: str = 'csv'
    DATASET_DATA_SKIP_ROW: int = 1
    DATASET_DATA_DELIVER: str = ','
    TABLES: dict = {
        'views_progress': {
            'names': ('user_id', 'movie_id', 'movie_frame', 'created'),
            'types': {0: str, 1: str, 2: float, 3: int},
        },
    }

    class Config:
        env_prefix = 'DATASET_'
        env_file = 'config/.env'


SETTINGS = Settings()

SQL_QUERY = {
    'top_20_movie_pop': """
    SELECT movie_id, COUNT(*) movie_count FROM views_progress GROUP BY movie_id ORDER BY movie_count DESC LIMIT 20;
    """,
    'movie_less_10_views': """
    SELECT COUNT(*) FROM 
    (SELECT movie_id, COUNT(*) movie_count FROM views_progress GROUP BY movie_id) as view_movie_counter
    WHERE movie_count<10;
    """,
    'top_20_movie_biggest_movies': """
    SELECT movie_id, sum(movie_frame) as sum_movie_frame 
    FROM views_progress GROUP BY movie_id ORDER BY sum_movie_frame DESC LIMIT 20;
    """,
    'top_20_users_watch_largest_movies': """
    SELECT user_id, count(*) as movies_count FROM 
    (SELECT DISTINCT user_id, movie_id FROM views_progress GROUP BY user_id, movie_id) as view_user_movie 
    GROUP BY user_id ORDER BY movies_count DESC LIMIT 20;
    """,
    'top_20_user_watch_movie_longest': """
    SELECT user_id, SUM(max_user_movie_frame) as total_user_movies_frame FROM 
    (SELECT DISTINCT user_id, movie_id, MAX(movie_frame) as max_user_movie_frame 
    FROM views_progress GROUP BY user_id, movie_id) as view_user_movie 
    GROUP BY user_id ORDER BY total_user_movies_frame DESC LIMIT 20;""",
}
