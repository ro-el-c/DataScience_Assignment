import pandas as pd

# excel file -> dataframe 으로 읽어들이기
xlfile = '1. python 과제/score.xlsx'
df = pd.read_excel(xlfile)

df.sort_values('sno') # 학번 순 출력

df = df.loc[(df['midterm'] >= 20) & (df['midterm'] >= 20), ['sno', 'midterm', 'final']]

print(df)


'''for i in range(len(df)):
    mid = df.iloc[i]['midterm']
    fin = df.iloc[i]['final']

    # 중간고사, 기말고사가 모두 20점 이상인 학생의
    # 학번, 중간고사, 기말고사 출력 (위에서 학번 순으로 정렬했기 때문에 차례대로 출력하면 됨)
    if mid >= 20 and fin >= 20:
        print("학번: {0}, 중간고사: {1}, 기말고사: {2}".format(df.iloc[i]['sno'], mid, fin))'''