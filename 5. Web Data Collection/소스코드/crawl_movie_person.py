import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from db_conn import *


""" 
ㅇ    m_id int,
ㅇ    p_id int,
ㅇ    role varchar(100), -- 감독, 주연, 조연, 등 
ㅇ    m_character varchar(100), -- 작품 내 역할명 
"""

def crawl_movie_person(num, rows, driver, m_id):
    num += 1

    m_id = int(m_id)
    p_id = None
    role = None
    m_character = None
    
    try:
        url = "https://movie.naver.com/movie/bi/mi/detail.naver?code=" + str(m_id)
        driver.get(url)
        try:
            driver.find_element(by=By.XPATH, value="//*[@id='actorMore']").click()
        except:
            pass

        movieActorPage = BeautifulSoup(driver.page_source, 'html.parser')
        
        # 주조연 배우
        actorMSList = movieActorPage.select("#content > div.article > div.section_group.section_group_frst > div.obj_section.noline > div > div.lst_people_area.height100 > ul > li")

        for actorTemp in actorMSList:
            # 배우 번호
            p_id = int(actorTemp.select_one("div.p_info > a")['href'].split("=")[1])
            print("p_id:", p_id)

            # 주조연
            roleData = actorTemp.select_one("div > div > p.in_prt > em")
            if roleData is not None:
                role = roleData.string
            print("role:", role)

            # 배역 이름
            role_nameData = actorTemp.select_one("div > div > p.pe_cmt > span")
            if role_nameData is not None:
                m_character = role_nameData.string[:-2]
            else:
                m_character = None
            print("m_character:", m_character)

            row = (m_id, p_id, role, m_character)
            rows.append(row)
            print(row)
            print()
       
        # 감독
        directorList = movieActorPage.select("#content > div.article > div.section_group.section_group_frst > div:nth-child(2) > div > div.dir_obj")

        for directorTemp in directorList:
            p_id = int(directorTemp.select_one("div > a")['href'].split("=")[1])
            print("p_id:", p_id)

            role = "감독"
            m_character = None

            row = (m_id, p_id, role, m_character)
            print(row)
            print()
            rows.append(row)
    except:
        print("data 가져올 수 없음. continue")

    

def get_movie_url_from_db():
    conn, cur = open_db()
    conn2, cur2 = open_db()

    #truncate_sql = """truncate table movie_person;"""
    #cur.execute(truncate_sql)
    #conn.commit()

    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    getmcodesql = "select m_id from naver_top_ranked_movie_list order by m_rank"
    cur.execute(getmcodesql)

    # 결과 하나씩(tuple) 가져오기
    movie_id = cur.fetchone()

    num = 0
    rows = []

    insert_sql= """insert into movie_person(m_id, p_id, role, m_character) values (%s, %s, %s, %s);"""
    #insert_sql_person = """insert into person(p_id, name, eng_name, photo_url, birth_date, birth_location, award, nickname, height, weight, family, education, summary) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    number=0

    while movie_id:
        num+=1

        number+=1
        print("number:", number)

        movie_id = movie_id['m_id']
        print("m_id:", movie_id)
        print()

        crawl_movie_person(num, rows, driver, str(movie_id))

        if num%20 == 0:
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
        """if number == 1:
            break"""
        continue

    close_db(conn, cur)
    driver.quit()


if __name__ == '__main__':
    get_movie_url_from_db()
    print()
    print()
    print("============================== 영화 데이터 movie_person table 가져오기 완료 ==============================")



 