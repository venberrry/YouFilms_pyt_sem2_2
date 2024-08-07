CREATE TABLE serials
(
    sid SERIAL PRIMARY KEY,
    name CHARACTER VARYING(40) NOT NULL,
    engname CHARACTER VARYING(40),
    poster CHARACTER VARYING(150),
    genres CHARACTER VARYING(100),
    year_of_release CHARACTER VARYING(50),
    county CHARACTER VARYING(100),
    MPAA CHARACTER VARYING(5),
    time_duration CHARACTER VARYING(20),
    description CHARACTER VARYING(500) NOT NULL,
    director CHARACTER VARYING(200),
    average_rating FLOAT NOT NULL DEFAULT 0.0,
    amount_rating INTEGER DEFAULT 0
);

CREATE TABLE films
(
    fid SERIAL PRIMARY KEY,
    name CHARACTER VARYING(40) NOT NULL,
    engname CHARACTER VARYING(40),
    poster CHARACTER VARYING(150),
    genres CHARACTER VARYING(100),
    year_of_release CHARACTER VARYING(50),
    county CHARACTER VARYING(100),
    MPAA CHARACTER VARYING(5),
    time_duration CHARACTER VARYING(20),
    description CHARACTER VARYING(500) NOT NULL,
    director CHARACTER VARYING(50),
    average_rating FLOAT NOT NULL DEFAULT 0.0,
    amount_rating INTEGER DEFAULT 0
);

CREATE TABLE users
(
    uid SERIAL PRIMARY KEY,
    login CHARACTER VARYING(40),
    password CHARACTER VARYING(300)
);

--O:O
CREATE TABLE profile
(
    pid SERIAL PRIMARY KEY,
    user_id INT UNIQUE REFERENCES users(uid),
    avatar CHARACTER VARYING(150),
    email CHARACTER VARYING(40),
    bio CHARACTER VARYING(400)
);

--O:M
CREATE TABLE film_reviews
(
    frid SERIAL PRIMARY KEY,
    profile_id BIGINT NOT NULL REFERENCES profile(pid) ON DELETE CASCADE,
    film_id BIGINT NOT NULL REFERENCES films(fid) ON DELETE CASCADE,
    title CHARACTER VARYING(40),
    rating FLOAT NOT NULL DEFAULT 0.0,
    review_text CHARACTER VARYING(1000)
);

CREATE TABLE serial_reviews
(
    srid SERIAL PRIMARY KEY,
    profile_id BIGINT NOT NULL REFERENCES profile(pid) ON DELETE CASCADE,
    serial_id BIGINT NOT NULL REFERENCES serials(sid) ON DELETE CASCADE,
    title CHARACTER VARYING(40),
    rating FLOAT NOT NULL DEFAULT 0.0,
    review_text CHARACTER VARYING(1000)
);