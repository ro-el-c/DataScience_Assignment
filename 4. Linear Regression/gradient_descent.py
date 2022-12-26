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

    y = [(t['score']) for t in data]
    y = np.array(y)
    
    return X, y

def least_square(X, y):
    X_const = sm.add_constant(X)

    model = sm.OLS(y, X_const)
    ls = model.fit() # ls = least square

    ls_c = ls.params[0]
    ls_m1 = ls.params[1]
    ls_m2 = ls.params[2]
    ls_m3 = ls.params[3]

    return ls_m1, ls_m2, ls_m3, ls_c

def gradient_descent(X, y):
    epochs = 200000
    min_grad = 0.00001
    learning_rate = 0.001
    
    m1 = 0.0
    m2 = 0.0
    m3 = 0.0
    c = 0.0
    n = len(y) # data의 개수

    for epoch in range(epochs):
        m1_partial = 0.0 # m에 대한 편미분 값
        m2_partial = 0.0 # m에 대한 편미분 값
        m3_partial = 0.0 # m에 대한 편미분 값
        c_partial = 0.0 # c에 대한 편미분 값

        for i in range(n):
            y_pred = m1 * X[i][0] + m2 * X[i][1] + m3 * X[i][2] + c
            m1_partial += (y_pred - y[i])*X[i][0]
            m2_partial += (y_pred - y[i])*X[i][1]
            m3_partial += (y_pred - y[i])*X[i][2]
            c_partial += (y_pred - y[i])
        
        m1_partial *= 2/n
        m2_partial *= 2/n
        m3_partial *= 2/n
        c_partial *= 2/n

        delta_m1 = -learning_rate * m1_partial
        delta_m2 = -learning_rate * m2_partial
        delta_m3 = -learning_rate * m3_partial
        delta_c = -learning_rate * c_partial

        if abs(delta_m1) < min_grad and abs(delta_m2) < min_grad and abs(delta_m3) < min_grad and abs(delta_c) < min_grad:
            print("some value is under min_grad")
            break

        m1 += delta_m1
        m2 += delta_m2
        m3 += delta_m3
        c += delta_c

        if epoch % 5000 == 0:
            print("epoch %d: delta_m1= %f, delta_m2= %f, delta_m3= %f, delta_c= %f, m1= %f, m2= %f, m3= %f, c= %f" %(epoch, delta_m1, delta_m2, delta_m3, delta_c, m1, m2, m3, c))
    
    return m1, m2, m3, c
    

if __name__ == '__main__':
    X, y = load_dbscore_data()

    print("least square:")
    ls_m1, ls_m2, ls_m3, ls_c = least_square(X, y)
    print("ls_m1 = %f, ls_m2 = %f, ls_m3 = %f, ls_c = %f" %(ls_m1, ls_m2, ls_m3, ls_c))
    
    print()
    print("gradient descent:")
    gd_m1, gd_m2, gd_m3, gd_c = gradient_descent(X, y)
    print()
    print("gd_m1 = %f, gd_m2 = %f, gd_m3 = %f, gd_c = %f" %(gd_m1, gd_m2, gd_m3, gd_c))