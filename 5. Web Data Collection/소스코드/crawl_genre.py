import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from db_conn import *

"""
ㅇ    m_id int primary key,
ㅇ    genre varchar(30)

"""

def crawl_genre(num, rows, movie_url):
    num += 1

    m_id = movie_url.split("=")[1]
    print("m_id:", m_id)
    
    try:
        movieDetail = requests.get(movie_url)
        movieDetailPage = BeautifulSoup(movieDetail.content, 'html.parser')

        basicData = movieDetailPage.select_one("#content > div.article > div.mv_info_area > div.mv_info")

        # 장르
        infoSpecData = basicData.select_one("dl.info_spec")
        infolist = list(infoSpecData)
        #print(infolist)
        while len(infolist) > 0:
            infolistpop = infolist.pop(0)
            try:
                tempDataStr = str(infolistpop['class']).replace("\n", "").replace("\t", "").replace("\r", "").strip()[
                              2:-2]
                #print(tempDataStr)

                # step 1
                # : 장르, 나라, 상영 시간, 개봉 일자
                if tempDataStr == "step1":
                    infolist.pop(0)
                    basicData = infolist.pop(0)
                    # 장르
                    genreData = basicData.select("dd > p > span:nth-child(1) > a")
                    if genreData is not None:
                        for tempGenre in genreData:
                            genreToStr = tempGenre.string
                            genreOne = (m_id, genreToStr)
                            print(genreOne)
                            rows.append(genreOne)
                            
            except:
                continue

    except:
        print("data 가져올 수 없음. continue")
    

def get_movie_url_from_db():
    conn, cur = open_db()
    conn2, cur2 = open_db()

    #truncate_sql = """truncate table movie_genre;"""
    #cur.execute(truncate_sql)
    #conn.commit()

    getmcodesql = "select url from naver_top_ranked_movie_list order by m_rank"
    cur.execute(getmcodesql)

    # 결과 하나씩(tuple) 가져오기
    movie_url = cur.fetchone()

    num = 0
    rows=[]

    insert_sql = """insert into movie_genre(m_id, genre) values (%s, %s);"""
    number=0

    while movie_url:
        num+=1
        number+=1
        print("number:", number)
        movie_url = movie_url['url']
        print("movie_url:", movie_url)
        crawl_genre(num, rows, str(movie_url))

        if num%20 == 0:
            print()
            print()
            print("--------------------------------------------------------------")
            print()
            print()
            print("DB에 데이터 넣기")

            print("{0}개 genre:".format(len(rows)))
            for tempData in rows:
                print(tempData)

            cur2.executemany(insert_sql, rows)
            conn2.commit()
            rows=[]
            num = 0
        
        movie_url = cur.fetchone()
        print()
        print()
        print("--------------------------------------------------------------")
        print()
        print()
        """if number == 1:
            break"""
        continue

    close_db(conn, cur)


if __name__ == '__main__':
    get_movie_url_from_db()
    print()
    print()
    print("============================== 영화 genre 가져오기 완료 ==============================")



 