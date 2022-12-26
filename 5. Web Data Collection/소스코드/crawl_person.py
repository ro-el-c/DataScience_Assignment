import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from db_conn import *


"""
ㅇ    p_id int primary key,
ㅇ    name varchar(50), -- 이름 
ㅇ    eng_name varchar(100), -- 영화 이름 - 영화에서 부제목 자리에 
ㅇ    photo_url varchar(500), -- 대표 인물 이미지 genre
ㅇ    birth_date date, -- 생년월일 parsing해서 넣기 
ㅇ    birth_location varchar(50), -- 태어난 나라  
ㅇ    award varchar(300),-- 수상 
ㅇ    nickname varchar(50), -- 다른 이름 - 주요정보-프로필-다른이름 
ㅇ    height int, -- 주요정보-프로필-신체 에서 키 
ㅇ    weight int, -- 주요정보-프로필-신체 에서 몸무게 
ㅇ    family varchar(100), -- 가족 
ㅇ    education varchar(100), -- 학력 
ㅇ    summary varchar(2000), -- 요약 - 주요정보-프로필 아래부분 
    enter_date datetime default now()
"""
    
def crawl_movie_person(num, rows, driver, p_id):
    num += 1

    p_id = int(p_id)
    name = None
    eng_name = None
    photo_url = None
    birth_date = None
    birth_location = None
    award = None
    nickname = None
    height = None
    weight = None
    family = None
    education = None
    summary = None

    url = "https://movie.naver.com/movie/bi/pi/basic.naver?code=" + str(p_id)

    personDetail = requests.get(url)
    personDetailPage = BeautifulSoup(personDetail.content, 'html.parser')
    
    infoSpecData = personDetailPage.select_one("#content > div.article > div.mv_info_area > div.mv_info.character > dl")
    infolist = list(infoSpecData)
    # print(infolist)

    while len(infolist) > 0:
        infolistpop = infolist.pop(0)
        try:
            tempDataStr = str(infolistpop['class']).replace("\n", "").replace("\t", "").replace("\r","").strip()[2:-2]
            #print(tempDataStr)

            # step 5
            # 출생
            if tempDataStr == "step5":
                #print("step5: 출생")

                infolist.pop(0)
                basicData = infolist.pop(0)
                #print(basicData)
                try:
                    birthData = basicData.string.strip().replace("\t","").replace("\r", "").replace("\n","").split("/")
                    #print(birthData)
                    
                    # 출생
                    if birthData is not None and len(birthData) > 1:
                        birth_date = birthData[0].strip().replace(" ", "")
                        birth_date = birth_date.replace("년", "-").replace("월", "-").replace("일", "")
                        #print(birth_date)

                        birthFormat = re.compile(
                            "^(19[0-9][0-9]|20[0-9][0-9])-([1-9]|0[0-9]|1[0-2])-([1-9]|0[1-9]|[1-2][0-9]|3[0-1])$")

                        if birthFormat.match(birth_date) is None:
                            birth_date = None
                            print("birth format match fail")
                        

                        birth_location = birthData[1].strip().replace(" ", "")
                        if len(birth_location) > 50:
                            birth_location = birth_location[:50]
           
                    else:  # 생일 data 존재 X
                        birth_date = None
                        birth_location = None
                except:
                    print("pass")    
                
            # step 8
            # 수상
            if tempDataStr == "step8":
                #print("step8: 수상")

                infolist.pop(0)
                basicData = infolist.pop(0)
                #print(basicData)
                
                # 수상
                try:
                    awardData = str(basicData)
                    #print(awardData)
                    if awardData is not None or len(awardData) > 1:
                        award = awardData.strip().replace("<dd>", "").replace("\t","").replace("\r", "").replace("\n","").split("<!--")[0]
                        award = award.strip()
                        if len(award) > 300:
                            award = award[:300]
                    else:
                        award = None
                except:
                    print("pass")
        except:
            pass

    print("birth_date:", birth_date)
    print("birth_location:", birth_location)
    print("award:", award)
    print()

    # 배우 이름, 영어 이름
    try:
        # 배우 이름
        name = personDetailPage.select_one("div.mv_info.character > h3 > a").string
        print("name:", name)

        # 배우 이름 eng
        aname_engData = personDetailPage.select_one("div.mv_info.character > strong")
        if aname_engData is not None and len(aname_engData.string.strip()) != 0:
            eng_name = aname_engData.string.strip().replace("\r\n\t\t\t\r\n\t\t\t", " ")
        else:
            eng_name = None
        print("eng_name:", eng_name)
    except:
        print("data 가져올 수 없음. continue")


        
    # 배우 사진 url
    try:
        photo_url = personDetailPage.select_one("div.poster > img")['src']
        print("photo_url:", photo_url)        
    except:
        print("data 가져올 수 없음. continue")
    
    print()

    # nickname, height, weight, family, education
    try:
        profileData = personDetailPage.select_one("#content > div.article > div.section_group.section_group_frst > div:nth-child(1) > div")
        try:
            categ=""
            profileDetailData = profileData.select("table > tbody > tr")
            for tempData in profileDetailData:
                categList = tempData.select("th")
                #print(categList)
                realDataList = tempData.select("td")
                #print(realDataList)
                c_num = 0
                for temp in categList:
                    if "img" in str(temp):
                        c_num += 1
                        categ = temp.select_one("img")["alt"]
                        if categ == "다른이름":
                            nickname = realDataList[c_num-1].string.strip()
                            if len(nickname) > 50:
                                nickname = nickname[:50]
                            print("nickname:", nickname)
                        elif categ == "신체":
                            height = realDataList[c_num-1].string.strip()
                            try:
                                if "," in height:
                                    tempList = height.split(",")
                                    height = tempList[0].replace("cm", "").strip()
                                    weight = tempList[1].replace("kg", "").strip()
                                if "kg" in height:
                                    weight = height.replace("kg", "").strip()
                                    height = None
                                height = height.replace("cm", "")
                            except:
                                height = None
                                weight = None
                            print("height:", height)
                            print("weight:", weight)
                        elif categ == "가족":
                            family =  realDataList[c_num-1].select_one("a").string.strip()
                            if len(family) > 100:
                                family = family[:100]
                            print("family:", family)
                        elif categ == "학력":
                            education = realDataList[c_num-1].string.strip()
                            if len(education) > 100:
                                education = education[:100]
                            print("education:", education)
                        else:
                            continue

                    
                        
                
        except:
            print("pass")
    except:
        print("data 가져올 수 없음. continue")


    driver.get(url)
    try:
        driver.find_element(by=By.XPATH, value="//*[@id='peopleInfoButton']").click()
    except:
        pass

    personDetailPage = BeautifulSoup(driver.page_source, 'html.parser')

    # 줄거리
    personSummaryData = personDetailPage.select_one("#content > div.article > div.section_group.section_group_frst > div:nth-child(1) > div > div.pf_intro.height100 > div")
    if personSummaryData is not None:
        summary = personSummaryData.text.strip()
        if len(summary) > 2000:
            summary = summary[:2000]
    else:
        summary = None
    print("summary:", summary)

    row = (p_id, name, eng_name, photo_url, birth_date, birth_location, award, nickname, height, weight, family, education, summary)
    #print(row)
    rows.append(row)
    

def get_movie_url_from_db():
    conn, cur = open_db()
    conn2, cur2 = open_db()
    
    #truncate_sql = """truncate table person;"""
    #cur.execute(truncate_sql)
    #conn.commit()

    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    getmcodesql = "select distinct p_id from movie_person where p_id is not null and p_id > 460117 order by p_id;"
    cur.execute(getmcodesql)

    # 결과 하나씩(tuple) 가져오기
    person_id = cur.fetchone()

    num = 0
    rows = []

    insert_sql = """insert into person(p_id, name, eng_name, photo_url, birth_date, birth_location, award, nickname, height, weight, family, education, summary) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    number=0

    while person_id:
        num+=1

        number+=1
        print("number:", number)

        person_id = person_id['p_id']
        print("person_id:", person_id)
        print()

        crawl_movie_person(num, rows, driver, str(person_id))

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
        
        person_id = cur.fetchone()
        print()
        print()
        print("--------------------------------------------------------------")
        print()
        print()
        """if number == 10:
            break"""
        continue
    

    cur2.executemany(insert_sql, rows)
    conn2.commit()

    close_db(conn, cur)
    close_db(conn2, cur2)
    driver.quit()


if __name__ == '__main__':
    get_movie_url_from_db()
    print()
    print()
    print("============================== 영화 데이터 person table 가져오기 완료 ==============================")



 