import pandas as pd
import numpy as np
from db_conn import *
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
from sklearn.svm import SVC
from sklearn.metrics import *

def load_score_data():
    conn, cur = open_db()

    sql = """select * from classification;"""
    cur.execute(sql)

    data = cur.fetchall()
    #print("data =", data)

    close_db(conn, cur)

    X = [(t['homework'], t['discussion'], t['midterm']) for t in data]
    X = np.array(X) # 2차원 numpy array 로 변환

    y = []
    for t in data:
        if t['grade'] == 'A':
            y.append(0)
        elif t['grade'] == 'B':
            y.append(1)
        else:
            y.append(2)

    y = np.array(y) # 2차원 numpy array 로 변환

    return X, y


def score_classification_logistic_regression(X, y): # Logistic Regression
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42) # train size : test size = 2 : 1로 나눔 // random_state는 42로 쓰는 관습

    logisticregression = LogisticRegression(C=0.1, multi_class='ovr', penalty='l1', solver='saga', max_iter=8000)
    logisticregression_model = logisticregression.fit(X_train, y_train)
    y_predict = logisticregression_model.predict(X_test)
    
    acc, pre, rec, f1 = classification_performance_eval(y_test, y_predict)
    print("Logistic Regression _ train_test_split:")
    print("accuracy = %f" %acc)
    print("precision = %f" %pre)
    print("recall = %f" %rec)
    print("f1_score = %f" %f1)

    print()

    kf = KFold(n_splits=5, random_state=42, shuffle=True)

    for train_index, test_index in kf.split(X):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

    logisticregression_model = logisticregression.fit(X_train, y_train)
    y_predict = logisticregression_model.predict(X_test)

    acc, pre, rec, f1 = classification_performance_eval(y_test, y_predict)
    print("Logistic Regression _ K-Fold cross validation:")
    print("accuracy = %f" %acc)
    print("precision = %f" %pre)
    print("recall = %f" %rec)
    print("f1_score = %f" %f1)


def score_classification_svm(X, y): # SVM
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

    svm = SVC(kernel = 'linear')
    svm_model = svm.fit(X_train, y_train) 
    y_predict = svm_model.predict(X_test)

    acc, pre, rec, f1 = classification_performance_eval(y_test, y_predict)
    print("SVM _ train_test_split:")
    print("accuracy = %f" %acc)
    print("precision = %f" %pre)
    print("recall = %f" %rec)
    print("f1_score = %f" %f1)

    print()

    kf = KFold(n_splits=5, random_state=42, shuffle=True)

    for train_index, test_index in kf.split(X):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

    svm_model = svm.fit(X_train, y_train) 
    y_predict = svm_model.predict(X_test)

    acc, pre, rec, f1 = classification_performance_eval(y_test, y_predict)
    print("SVM _ K-Fold cross validation:")
    print("accuracy = %f" %acc)
    print("precision = %f" %pre)
    print("recall = %f" %rec)
    print("f1_score = %f" %f1)


def classification_performance_eval(y_test, y_predict):
    accuracy = accuracy_score(y_test, y_predict)
    precision = precision_score(y_test, y_predict, average='macro', zero_division=False)
    recall = recall_score(y_test, y_predict, average='macro', zero_division=False)
    f1 = f1_score(y_test, y_predict, average='macro', zero_division=False)
    
    # 성능 지표 한 번에 확인할 수 있는 함수
    # report = classification_report(y_test, y_predict, zero_division=False)

    return accuracy, precision, recall, f1

if __name__ == "__main__":
    print("[multi-class classification]")
    print("----------------------------------------")
    print()

    X, y = load_score_data()
    score_classification_logistic_regression(X, y)
    print()
    print("----------------------------------------")
    print()
    score_classification_svm(X, y)