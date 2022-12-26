import pandas as pd
import numpy as np
from db_conn import *
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
from sklearn.svm import SVC

def load_score_data():
    conn, cur = open_db()

    sql = """select * from classification;"""
    cur.execute(sql)

    data = cur.fetchall()
    #print("data =", data)

    close_db(conn, cur)

    X = [(t['homework'], t['discussion'], t['midterm']) for t in data]
    X = np.array(X) # 2차원 numpy array 로 변환

    y = [1 if t['grade'] == 'B' else -1 for t in data]
    y = np.array(y) # 2차원 numpy array 로 변환

    return X, y


def score_classification_logistic_regression(X, y): # Logistic Regression
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42) # train size : test size = 2 : 1로 나눔 // random_state는 42로 쓰는 관습

    logisticregression = LogisticRegression(C=0.1, penalty='l1', solver='saga', max_iter=10000)
    logisticregression_model = logisticregression.fit(X_train, y_train)
    y_predict = logisticregression_model.predict(X_test)
    #print("y_predict =", y_predict)

    acc, pre, rec, f1 = classification_performance_eval(y_test, y_predict)
    print("Logistic Regressioin _ train_test_split:")
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
    print("Logistic Regressioin _ K-Fold cross validation:")
    print("accuracy = %f" %acc)
    print("precision = %f" %pre)
    print("recall = %f" %rec)
    print("f1_score = %f" %f1)


def score_classification_svm(X, y): # SVM
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

    svm = SVC(kernel = 'rbf')
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
    tp, tn, fp, fn = 0, 0, 0, 0

    for y, yp in zip(y_test, y_predict): # zip: 2개의 array에서 동시 하나씩 가져옴
        if y == 1 and yp == 1:
            tp += 1
        elif y == 1 and yp == -1:
            fn += 1
        elif y == -1 and yp == 1:
            fp += 1
        else:
            tn += 1
    
    accuracy = (tp+tn)/(tp+tn+fp+fn)
    precision = tp/(tp+fp)
    recall = tp/(tp+fn)
    f1_score  = 2*precision*recall/(precision+recall)

    return accuracy, precision, recall, f1_score


if __name__ == "__main__":
    print("[binary classification]")
    print("----------------------------------------")
    print()

    X, y = load_score_data()
    score_classification_logistic_regression(X, y)
    print()
    print("----------------------------------------")
    print()
    score_classification_svm(X, y)