import pandas as pd
from db_conn import *

def import_db_score_data():
    conn, cur = open_db()

    # classification table 생성
    sql = """create table classification(
                homework float(4,2),
                discussion int,
                midterm float(4,2),
                grade char(1)
            );"""

    cur.execute(sql)
    conn.commit()
    
    # db_score.xlsx 읽어 classification에 homework, discussion, midterm, grade 데이터 insert
    xlfile = '3. classification/db_score.xlsx'
    df = pd.read_excel(xlfile)
    df = df.loc[:, ['homework', 'discussion', 'midterm', 'grade']]
    
    rows = []

    insert_sql = """insert into classification(homework, discussion, midterm, grade)
             values(%s, %s, %s, %s);"""


    ''' grade는 아래와 같이 변환하여 입력
        A -> A,
        B, C -> B,
        D, F -> C
    '''
    for x in df.values:
        x_grade = x[3]

        if x_grade == 'C':
            print(x)
            x[3] = 'B'
        elif x_grade == 'D' or x_grade == 'F':
            print(x)
            x[3] = 'C'
        else:
            print(x)

        rows.append(tuple(x))
            
    cur.executemany(insert_sql, rows)
    conn.commit()

    close_db(conn, cur)

if __name__ == "__main__":
    import_db_score_data()