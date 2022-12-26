from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from db_conn import *


def crawl_movie_list_page(conn, cur, driver, page):
    url = "https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel=pnt" + "&page=" + str(page)
    driver.get(url)

    movie_list_body_xpath = "/html/body/div/div[4]/div/div/div/div/div[1]/table/tbody"
    movie_list_element = driver.find_element(By.XPATH, movie_list_body_xpath)
    movies = movie_list_element.find_elements(By.TAG_NAME, 'tr')
    
    insert_sql = "insert into naver_top_ranked_movie_list(m_id, m_rank, url, title, point) values (%s, %s, %s, %s, %s);" 
    
    rows=[]

    for movie in movies:
        try: # page 1 에만 해당
            rank_element = movie.find_element(By.CLASS_NAME, 'ac')
            m_rank = int(rank_element.find_element(By.XPATH, 'img').get_attribute('alt'))
            print('m_rank=', m_rank)
        except:
            try: # page 2 부터 해당x    
                rank_element = movie.find_element(By.CLASS_NAME, 'order')
                m_rank = int(rank_element.text)
                print('m_rank=', m_rank)
            except: # tr 에서 빈칸에 해당하는 부분들이 있음 -> 넘어가기
                continue
        
        title_element = movie.find_element(By.CLASS_NAME, 'title')
        title = title_element.find_element(By.XPATH, 'div/a').text
        url = title_element.find_element(By.XPATH, 'div/a').get_attribute('href')
        m_id = int(url.split('=')[-1])
        print('title=', title)
        print('url=', url)
        print('m_id=', m_id)
        
        try:
            point = float(movie.find_element(By.CLASS_NAME, 'point').text)
            print('point=', point)
        except: # 평점이 존재하지 않는 경우 예외 처리 - 평점 순이기 때문에 존재 // 다른 영화를 생각해봤을 때, 없을 수도 있음.
            print('point error')
            point = 0
            
        row = (m_id, m_rank, url, title, point)
        rows.append(row)
    
        print('\n')

    cur.executemany(insert_sql, rows)
    conn.commit()



def crawl_movie_list():
    conn, cur = open_db()

    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    truncate_sql = """truncate table naver_top_ranked_movie_list;"""
    cur.execute(truncate_sql)
    conn.commit()

    import time
    for page in range(1, 41):
        print("page number:", page)
        crawl_movie_list_page(conn, cur, driver, page)
        time.sleep(2)
    
    close_db(conn, cur)
    driver.quit()


if __name__ == '__main__':
    crawl_movie_list()
    print("============================== 평점 순 2000개 영화 데이터 가져오기 완료 ==============================")



 