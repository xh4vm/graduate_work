CREATE TABLE IF NOT EXISTS views_progress (
            id IDENTITY,
            user_id VARCHAR(256) NOT NULL,
            movie_id VARCHAR(256) NOT NULL,
            movie_frame INTEGER NOT NULL,
            created TIMESTAMP WITH TIMEZONE NOT NULL
        );