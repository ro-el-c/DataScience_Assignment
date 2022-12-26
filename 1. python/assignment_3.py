import pymysql as pms

conn = pms.connect(host='localhost', user='user', password='password', db='university')
cur = conn.cursor(pms.cursors.DictCursor)

# 중간, 기말 모두 20점 이상인 학생의 정보를 학번 순으로 추출
sql = "select sno, midterm, final from score where midterm >= 20 and final >= 20 order by sno;"
cur.execute(sql)
conn.commit()

row = cur.fetchone()
while row:
    print(row)
    row = cur.fetchone()

cur.close()
conn.close()