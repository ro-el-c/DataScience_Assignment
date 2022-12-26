# X= [homework, attendance, final], y=score

import numpy as np
from db_conn import *
import statsmodels.api as sm
import matplotlib.pyplot as plt

def load_dbscore_data():
    conn, cur = open_db()

    sql = "select * from score"
    cur.execute(sql)

    data = cur.fetchall()

    close_db(conn, cur)

    X = [(t['homework'], t['attendance'], t['final']) for t in data]
    X = np.array(X)
    X = sm.add_constant(X)


    y = [(t['score']) for t in data]
    y = np.array(y)

    return X, y

def least_square(X, y):
    # Least Square 메소드
    model = sm.OLS(y, X)
    results = model.fit() # fitting: data를 가지고 학습
    print(results.summary())

if __name__ == '__main__':
    X, y = load_dbscore_data()
    least_square(X, y)
    print("least square _ end")
    

"""

    score = 1.7178 * homework
            + 1.9348 * attendance
            + 1.4972 * final
            - 3.6583 (constant)

    Df Residuals(degree of freedom): 88 (= 92 - 4) ; 4 = X variable이 3개 + constant 1개
    R-squared(결정 계수): 0.825 ; 꽤 높은 수치

    F-statistic(Prob): 137.9 ; 식의 유의미한 정도를 나타냄
    ; 2개의 distribution을 비교할 때, F-statistic value가 x 좌표 상의 포인트이고, 그에 대한 확률 값을 나타내는 것
    - 귀무가설(데이터 분포와 만들어 놓은 linear regression이 전혀 관련이 없다.)에 대한 확률
    => 귀무가설 기각 == linear regression이 '유의미'하다

    Prob (F-statistic): 3.76e-33 (= 3.76 * 10^(-33)) = 귀무가설을 기각하지 않을 확률
    ; 아주 강력하게 귀무가설 기각 -> 유의미한 linear regression

    x1, x3 - 굉장히 정확하게 예측

    std err 값이 작을수록 variable에 대한 예측치가 높다 == 통계적으로 유의미하다.

    t-distribution 상에서 t 값이 클수록 귀무가설 기각 확률 높아짐
    -> p-value(95% 신뢰도 구간으로 귀무가설을 본다면 0.05가 기준)가 0 == 강하게 귀무가설 기각. -> coefficient 값 무조건 받아들여라 == 매우 유의미하다.

    => const는 0.815, x2는 0.389로 0.05보다 큰 값 -> 귀무가설 채택 => 0으로 봐도 크게 다르지 않다. 유의미하지 않다.
    
    == homework과 final 2개만 가지고 linear regression 설계한 것이
       homework, attendence, final 3개를 가지고 linear regression 설계한 것과 별반 다를 것이 없다.

              [0,025  0.975]
    const 값은 -34.697~27.380 사이에서 왔다갔다 할 수도 있음.
    x3의 경우 1.317~1.678로 범위가 굉장히 좁게(타이트하게), 즉, 정확하게 예측하고 있다.

"""
