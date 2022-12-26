import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from db_conn import *

"""
    id int auto_increment primary key,
    m_id int,
    point int, -- 평점 
    user_id varchar(20), -- 닉네임 * 포함
    short_review varchar(300), -- 한줄평 
    review_date datetime, -- 작성 날짜 

"""

def crawl_short_review(num, rows, m_id):
    num += 1

    m_id = int(m_id)
    print("m_id:", m_id)
    try:
        totalgradeNum = 0
        nowgradecnt = 0
        pageNum = 1
        
        while (True):
            movie_url = "https://movie.naver.com/movie/point/af/list.naver?st=mcode&sword=" + str(m_id) + "&target=after&page=" + str(pageNum)
            movieDetail = requests.get(movie_url)
            gradeDetailPage = BeautifulSoup(movieDetail.content, 'html.parser')

            print()

            short_reviews = gradeDetailPage.select_one("#old_content")

            # 총 평점 수
            if pageNum == 1:
                totalgradeNum = int(short_reviews.select_one("h5 > div > strong").string)
                print("totalgradeNum:", totalgradeNum)
                print()

                # 평점 없는 경우 생략
                if totalgradeNum == 0:
                    break
            

            short_reviewsList = short_reviews.find('table', {'class': "list_netizen"})
            short_reviewsList = short_reviewsList.select('tbody > tr')

        
            for gradeTemp in short_reviewsList:
                # 평점
                point = int(gradeTemp.select_one("td.title > div > em").string)
                print("point:", point)

                # 닉네임
                user_id = gradeTemp.select_one("td:nth-child(3) > a").string
                print("user_id:", user_id)

                # 내용
                short_review = list(gradeTemp.select_one("td.title"))[6].replace("\n", "").replace("\t", "").strip()
                if len(short_review) > 300:
                    short_review = short_review[:300]
                elif len(short_review.strip()) < 1:
                    print("too short to save")
                    print()
                    continue
                print("short_review:", short_review)

                # 작성일
                review_date = "20" + list(gradeTemp.select_one("td:nth-child(3)"))[2].strip().replace(".", "-")
                print("review_date:", review_date)

                nowgradecnt += 1
                print("nowgradecnt", nowgradecnt)
                print()

                row = (m_id, point, user_id, short_review, review_date)
                rows.append(row)
 
                if nowgradecnt >= totalgradeNum:
                    break
                if nowgradecnt >= 100:
                    break
            if nowgradecnt >= 100:
                break
            pageNum += 1
        
        

    except:
        print("data 가져올 수 없음. continue")
    

def get_movie_url_from_db():
    conn, cur = open_db()
    conn2, cur2 = open_db()

    truncate_sql = """truncate table movie_short_review;"""
    cur.execute(truncate_sql)
    conn.commit()
    
    getmcodesql = "select m_id from naver_top_ranked_movie_list order by m_rank"
    cur.execute(getmcodesql)

    # 결과 하나씩(tuple) 가져오기
    movie_id = cur.fetchone()

    num = 0
    rows = []

    insert_sql= "insert into movie_short_review(m_id, point, user_id, short_review, review_date) values (%s, %s, %s, %s, %s);"
    number=0

    while movie_id:
        num+=1

        number+=1
        print("number:", number)

        movie_id = movie_id['m_id']
        print("m_id:", movie_id)
        print()

        crawl_short_review(num, rows, str(movie_id))

        if num%10 == 0:
            print()
            print()
            print("--------------------------------------------------------------")
            print()
            print()
            print("DB에 데이터 넣기")

            cur2.executemany(insert_sql, rows)
            conn2.commit()

            rows = []
            num = 0
        
        movie_id = cur.fetchone()
        print()
        print()
        print("--------------------------------------------------------------")
        print()
        print()
        '''if number == 10:
            break/'''
        continue

    close_db(conn, cur)


if __name__ == '__main__':
    get_movie_url_from_db()
    print()
    print()
    print("============================== 영화 short_review 가져오기 완료 ==============================")



 