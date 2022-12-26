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
ㅇ    title varchar(200), -- 제목 
ㅇ    second_title varchar(200), -- 부제목 
ㅇ    m_year int, -- 제작 년도 (부제목, 년도) 형식으로 저장되어 있음
ㅇ    pic_url varchar(500), -- 대표 이미지 url 

ㅇ    user_point float default 0, -- 관람객 평점 
ㅇ    reporter_point float default 0, -- 기자, 평론가 평점 
ㅇ    netizen_point float, -- 네티즌 평점

ㅇ    nationality varchar(30),   -- 나라 
ㅇ    running_time int, -- 상영 시간 
ㅇ    opening_date date, -- 개봉 일자 
ㅇ    demestic_rate varchar(10), -- 국내 등급 (연령 제한) 
ㅇ    foreign_rate varchar(10), -- 국외 등급 ---- 등급 없을 수 있음 주의

ㅇ    summary varchar(2000) -- 주요 정보 - 줄거리 
"""

def crawl_movie(num, rows, movie_url):
    num += 1

    m_id = movie_url.split("=")[1]
    print("m_id:", m_id)

    # 19세 - 생략
    title = None
    second_title = None
    m_year = None
    pic_url = None
    user_point = None
    reporter_point = None
    netizen_point = None
    nationality = None
    running_time = None
    demestic_rate = None
    foreign_rate = None
    opening_date = None
    summary = None
    
    try:
        movieDetail = requests.get(movie_url)
        movieDetailPage = BeautifulSoup(movieDetail.content, 'html.parser')

        basicData = movieDetailPage.select_one("#content > div.article > div.mv_info_area > div.mv_info")

        # title
        title = basicData.select_one("h3 > a").string
        print("title:", title)

        # 영화 부제목, 년도
        subtitle_year = basicData.select_one("strong")['title']

        second_title = subtitle_year[:-6]
        print("second_title:", second_title)

        m_year = subtitle_year[-4:]
        print("m_year:", m_year)

        # 대표 이미지
        pic_url = movieDetailPage.select_one("#content > div.article > div.mv_info_area > div.poster > a > img")['src']
        print("pic_url:", pic_url)
        
        print()

        # 관람객 평점
        user_rateData = movieDetailPage.select("#actualPointPersentBasic > div > em")
        if user_rateData is None or len(user_rateData) < 1:
            user_point = None
        else:
            user_point = ""
            for tempData in user_rateData:
                user_point += tempData.string
        print("user_point:", user_point)

        # 네티즌 평점
        netizen_rateData = movieDetailPage.select("#pointNetizenPersentBasic > em")
        if netizen_rateData is None or len(netizen_rateData) < 1:
            netizen_point = None
        else:
            netizen_point = ""
            for tempData in netizen_rateData:
                netizen_point += tempData.string
        print("netizen_point:", netizen_point)

        # 평론가 평점
        reporter_rateData = movieDetailPage.select("#content > div.article > div.mv_info_area > div.mv_info > div.main_score > div:nth-child(2) > div > a > div > em")
        if reporter_rateData is None or len(reporter_rateData) < 1:
            reporter_point = None
        else:
            reporter_point = ""
            for tempData in reporter_rateData:
                reporter_point += tempData.string
        print("reporter_point:", reporter_point)

        print()
        # 나라, 상영 시간, 개봉 일자, 국내/해외 상영 등급
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

                    temp = basicData.select("dd > p > span")
                    rateDataList = list(temp)
                    
                    if len(rateDataList) != 4:
                        continue

                    # 나라
                    nationData = basicData.select("dd > p > span:nth-child(2) > a")
                    #print(nationData)
                    nationality = ""
                    if nationData is not None:
                        for tempNation in nationData:
                            nationality += tempNation.string + " "
                    else:
                        nationality = None 

                    if len(nationality) > 30:
                        nationality = nationality[:30]
                    nationality = nationality.strip()

                    # 상영 시간
                    running_timeData = basicData.select_one("dd > p > span:nth-child(3)")
                    if running_timeData is None or len(running_timeData) < 1:
                        running_time = None
                    else:
                        running_time = int(running_timeData.string.strip()[:-1])

                    # 개봉 날짜
                    opening_dateData = basicData.select("dd > p > span:nth-child(4)")
                    if opening_dateData is None or len(opening_dateData) < 1:
                        opening_date = None
                    else:
                        opening_dateData = list(opening_dateData)
                        waitdata = ""
                        opening_dateVal = ""

                        for yearandday in opening_dateData:
                            yearandday = list(yearandday)
                            k = 0
                            for tempData in yearandday:
                                yndDataToStr = tempData.string.replace("[", "").replace("]", "")
                                yndDataToStr = yndDataToStr.replace("\r", "").replace("\n", "").replace("\t", "")
                                yndDataToStr = yndDataToStr.replace(",", "").replace(" ", "").replace(".", "-")

                                if yndDataToStr[:4] == "N=a:" or yndDataToStr == "":
                                    continue
                                if k % 3 == 0:
                                    waitdata = yndDataToStr
                                elif k % 3 == 1:
                                    opening_dateVal = waitdata + yndDataToStr
                                else:
                                    if yndDataToStr != "개봉":
                                        continue
                                    else:
                                        opening_date = opening_dateVal
                                k+=1
                        
                        dateFormat = re.compile("^(19[0-9][0-9]|20[0-9][0-9])-([1-9]|0[0-9]|1[0-2])-([1-9]|0[1-9]|[1-2][0-9]|3[0-1])$")
                        if dateFormat.match(opening_date) is None:
                            opening_date = None
                            print("opening_date format match fail")


                # step 4
                # : 관람가 등급
                if tempDataStr == "step4":
                    infolist.pop(0)
                    basicData = infolist.pop(0)
                    # print(basicData)

                    movie_rate=[]
                    rateData = basicData.select_one("dd > p")

                    if rateData is None or len(rateData) < 1:
                        demestic_rate = foreign_rate =  None
                    else:
                        rateDataList = list(rateData)
                        k = 0
                        rate_nation = ""
                        rate = ""
                        
                        for tempData in rateDataList:
                            rateDataToStr = tempData.string.replace("[", "").replace("]", "")
                            rateDataToStr = rateDataToStr.replace("\r", "").replace("\n", "").replace("\t",
                                                                                                          "").strip()
                            #print(rateDataToStr)
                            if rateDataToStr[:4] == "N=a:" or rateDataToStr == "도움말" or rateDataToStr == "":
                                continue

                            if k % 2 == 0:
                                rate_nation = rateDataToStr
                            else:
                                rate = rateDataToStr
                                rateOne = (rate_nation, rate)
                                movie_rate.append(rateOne)
                            k += 1
                    
                        demesticNum=0
                        foreignNum=0
                        
                        for tempData in movie_rate:
                            if tempData[0]=="국내":
                                demesticNum += 1
                                demestic_rate = tempData[1]
                            else:
                                foreignNum += 1
                                foreign_rate = tempData[1]
                        
                        if demesticNum < 1:
                            demestic_rate = None
                        if foreignNum < 1:
                            foreign_rate = None
                            
            except:
                continue
        
        print()

        print("nationality:", nationality)
        print("running_time:", running_time)
        print("opening_date:", opening_date)
        print("demestic_rate:", demestic_rate)
        print("foreign_rate:", foreign_rate) 

        # 줄거리
        summary = ""
        summaryData = movieDetailPage.select_one("#content > div.article > div.section_group.section_group_frst > div:nth-child(1) > div > div.story_area")
        
        summaryTitleData = summaryData.select_one("h5")
        summaryContentData = summaryData.select_one("p")
        
        if summaryTitleData is None and summaryContentData is None:
            summary = None

        #print(summaryData)
        if summaryTitleData is not None:
            for temp in summaryTitleData:
                titleTemp = temp.text.strip()
                if len(titleTemp) < 1:
                    continue
                summary += titleTemp + "\n "

        #print(summaryData)
        if summaryContentData is not None:
            for temp in summaryContentData:
                contentTemp = temp.text.strip()
                if len(contentTemp) < 1:
                    continue
                summary += contentTemp + "\n "
    
        summary = summary.strip()
        if len(summary) > 2000:
            summary = summary[:2000]
        print("summary:", summary)

    except:
        print("data 가져올 수 없음. continue")
    
    row = (m_id, title, second_title, pic_url, m_year, user_point, reporter_point, netizen_point, nationality, running_time, opening_date, demestic_rate, foreign_rate, summary)
    rows.append(row)

def get_movie_url_from_db():
    conn, cur = open_db()
    conn2, cur2 = open_db()

    #truncate_sql = """truncate table movie;"""
    #cur.execute(truncate_sql)
    #conn.commit()

    getmcodesql = "select url from naver_top_ranked_movie_list order by m_rank"
    cur.execute(getmcodesql)

    # 결과 하나씩(tuple) 가져오기
    movie_url = cur.fetchone()

    num = 0
    rows=[]

    insert_sql = """insert into movie(m_id, title, second_title, pic_url, m_year, user_point, reporter_point, netizen_point,\
        nationality, running_time, opening_date, demestic_rate, foreign_rate, summary) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    number=0

    while movie_url:
        num+=1
        number+=1
        print("number:", number)
        movie_url = movie_url['url']
        print("movie_url:", movie_url)
        crawl_movie(num, rows, str(movie_url))

        if num%20 == 0:
            print()
            print()
            print("--------------------------------------------------------------")
            print()
            print()
            print("DB에 데이터 넣기")
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
        continue

    close_db(conn, cur)


if __name__ == '__main__':
    get_movie_url_from_db()
    print()
    print()
    print("============================== 영화 데이터 movie table 가져오기 완료 ==============================")



 