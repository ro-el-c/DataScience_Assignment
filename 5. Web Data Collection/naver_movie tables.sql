create database naver_movie;

create table naver_top_ranked_movie_list (
    m_id int primary key,
    m_rank int,
    url varchar(300),
    title varchar(100),
    point float,
    crawl_flag int default 0,
    enter_date datetime default now()
);

create table movie (
    m_id int primary key,
    title varchar(200),
    second_title varchar(200),
    pic_url varchar(500),
    m_year int,
    user_point float default 0,
    reporter_point float default 0,
    netizen_point float,
    nationality varchar(30),
    running_time int,
    opening_date date,
    demestic_rate varchar(10),
    foreign_rate varchar(10),
    summary varchar(2000),
);

create table movie_genre (
    m_id int,
    genre varchar(30),
    enter_date datetime default now()
);


create table movie_short_review (
    id int auto_increment primary key,
    m_id int,
    point int,
    short_review varchar(300),
    user_id varchar(20),
    review_date datetime,
    enter_date datetime default now()
);

create table movie_person (
    m_id int,
    p_id int,
    role varchar(100),
    character varchar(100),
    enter_date datetime default now(),    
    index idx_mid_pid(m_id, p_id),
    index idx_mid(m_id),
    index idx_pid(p_id)
);

create table person (
    p_id int primary key,
    name varchar(50),
    eng_name varchar(100),
    photo_url varchar(500),
    birth_date date,
    birth_location varchar(50),
    award varchar(300),
    nickname varchar(50),
    height int,
    weight int,
    family varchar(100),
    education varchar(100),
    summary varchar(2000),
    enter_date datetime default now()
);


















