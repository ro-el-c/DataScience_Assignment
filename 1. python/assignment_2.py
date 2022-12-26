import pandas as pd
import pymysql as pms

conn = pms.connect(host='localhost', user='user', password='password', db='university')
cur = conn.cursor(pms.cursors.DictCursor)

# score table 생성
sql = "create table score(sno int primary key, attendance float(3,2), homework float(4,2), discussion int, midterm float(4,2), final float(4,2), score float(4,2), grade char(1));"
cur.execute(sql)
conn.commit()

# excel file 읽고, database에 삽입하기 전
sql = "select * from score;"
cur.execute(sql)
conn.commit()

print("데이터 삽입 전: ")
row = cur.fetchone()
while row:
    print(row)
    row = cur.fetchone()

# excel file 읽어서 score table에 삽입
xlfile = '1. python 과제/score.xlsx'
df = pd.read_excel(xlfile)

sql = "insert into score(sno, attendance, homework, discussion, midterm, final, score, grade) values(%s, %s, %s, %s, %s, %s, %s, %s)"

tuples = [tuple(x) for x in df.to_numpy()]
cur.executemany(sql, tuples)
conn.commit()

print() # 구분을 위한 공백

# data 삽입 후
sql = "select * from score;"
cur.execute(sql)
conn.commit()

print("데이터 삽입 후:")
row = cur.fetchone()
while row:
    print(row)
    row = cur.fetchone()

cur.close()
conn.close()
    
