use navermovie;
select * from rate order by mcode;

use naver_movie;
show tables;

drop table naver_top_ranked_movie_list;

create database naver_movie;

-- 완료
create table naver_top_ranked_movie_list (
    m_id int primary key,
    m_rank int,
    url varchar(300),
    title varchar(100),
    point float,
    crawl_flag int default 0,
    enter_date datetime default now()
);
select * from naver_top_ranked_movie_list where m_rank >= 1001 order by m_rank;

create table movie (
    m_id int primary key,
    title varchar(200), -- 제목 
    second_title varchar(200), -- 부제목 
    pic_url varchar(500), -- 대표 이미지 url 
    m_year int, -- 제작 년도 (부제목, 년도) 형식으로 저장되어 있음
    user_point float default 0, -- 관람객 평점 
    reporter_point float default 0, -- 기자, 평론가 평점 
    netizen_point float, -- 네티즌 평점 
    nationality varchar(30), -- 나라 
    running_time int, -- 상영 시간 
    opening_date date, -- 개봉 일자 
    demestic_rate varchar(10), -- 국내 등급 (연령 제한) 
    foreign_rate varchar(10), -- 국외 등급 ---- ₩등급 없을 수 있음 주의
    summary varchar(2000) -- 주요 정보 - 줄거리 
);
select * from movie order by m_id;
select count(*) from movie where nationality is null and running_time is null and opening_date is null;
select * from movie where m_id=176354;

create table movie_genre ( -- 영화:장르 - 1:n 관계 
    m_id int,
    genre varchar(30),
    enter_date datetime default now()
);
select * from movie_genre order by enter_date;



drop table movie_short_review;
create table movie_short_review ( -- 평점 (한줄평) ; 최대 100개 
    id int auto_increment primary key,
    m_id int,
    point int, -- 평점 
    user_id varchar(20), -- 닉네임 * 포함
    short_review varchar(300), -- 한줄평 
    review_date datetime, -- 작성 날짜 
    enter_date datetime default now()
);
select count(*) from movie_short_review order by enter_date;
-- user_id varchar(20), -- 알아서..?  -> 빼기 

drop table movie_person;
create table movie_person ( -- 영화:출연 = 1:n 
    m_id int,
    p_id int,
    role varchar(100), -- 감독, 주연, 조연, 등 
    m_character varchar(100), -- 작품 내 역할명 
    enter_date datetime default now(),
    index idx_mid_pid(m_id, p_id),
    index idx_mid(m_id),
    index idx_pid(p_id)
);
-- character -> m_character ; 오류
select * from movie_person order by enter_date;
select count(distinct p_id) from movie_person where p_id is not null order by p_id;

create table person ( -- 배우 상세 정보 
    p_id int primary key,
    name varchar(50), -- 이름 
    eng_name varchar(100), -- 영어 이름 
    photo_url varchar(500), -- 대표 인물 이미지 genre
    birth_date date, -- 생년월일 parsing해서 넣기 
    birth_location varchar(50), -- 태어난 나라  
    award varchar(300),-- 수상 
    nickname varchar(50), -- 다른actor 이름 - 주요정보-프로필-다른이름 
    height int, -- 주요정보-프로필-신체 에서 키 
	weight int, -- 주요정보-프로필-신체 에서 몸무게 
    family varchar(100), -- 가족 
    education varchar(100), -- 학력 
    summary varchar(2000), -- 요약 - 주요정보-프로필 아래부분 
    enter_date datetime default now()
);
select * from person order by p_id desc;
select * from person where p_id is null;

select * from naver_top_ranked_movie_list order by m_rank;

