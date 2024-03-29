# coding=utf-8
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold
from sklearn.datasets import load_iris

class DecisionTreeClassifier:
    def __init__(self, max_depth = 5, max_leafsize = 2):
        self._depth_ = max_depth
        self._leafsize_ = max_leafsize
        self._list_size_ = int(pow(2, self._depth_ + 1) - 1) * 2

    def _init_list_of_arrs_(self, size):
        list_of_arrs = list()
        for i in range(0, size):
            list_of_arrs.append(np.zeros((1, 1)))
        return list_of_arrs

    def _criteria_entropy_(self, x):
        def get_h(x):
            if x[0] and x[1] != 0:
                hl = -x[0] * np.log2(x[0])
                hr = -x[1] * np.log2(x[1])
            elif x[0] == 0 and x[1] == 0:
                hl = 0
                hr = 0
            elif x[0] == 0:
                hl = 0
                hr = -x[1] * np.log2(x[1])
            elif x[1] == 0:
                hl = -x[0] * np.log2(x[0])
                hr =  0
            return hl, hr

        h_l_r = np.apply_along_axis(get_h, 1, x)
        h_L = h_l_r.T[0].sum()
        h_R = h_l_r.T[1].sum()
        return h_L, h_R

    def _criteria_gini_(self, x):
        h_L = x.prod(axis=0)[0]
        h_R = x.prod(axis=0)[1]
        return h_L, h_R

    def _get_split_(self, y_vec, inp_vec):
        w_vec = inp_vec
        y_class = np.unique(y_vec)
        y_class_num = y_class.shape[0]

        p_l_r = np.zeros((y_class_num, 2))

        if w_vec.shape[0] > 500:
            btch_sz = 200
        else:
            # perc = 1
            btch_sz = w_vec.shape[0]
        # btch_sz = int(w_vec.shape[0] * perc)
        arr_of_numbs = np.linspace(0, w_vec.shape[0] - 1, btch_sz, dtype=int)
        item_beta_g_arr = np.zeros((btch_sz, 3))
        iter_c = 0
        for item in arr_of_numbs:
            beta = w_vec[item]
            x_L_len = (w_vec[arr_of_numbs] <= beta).sum()
            x_H_len = btch_sz - x_L_len
            if x_L_len != 0 and x_H_len != 0:
                mask_L = w_vec[arr_of_numbs] <= beta
                mask_H = w_vec[arr_of_numbs] > beta

                for k in range(y_class_num):
                    mask_y = y_vec[arr_of_numbs] == y_class[k]
                    p_l_r[k][0] = (mask_y * mask_L).sum() / x_L_len
                    p_l_r[k][1] = (mask_y * mask_H).sum() / x_H_len

                # h_L, h_R = self._criteria_gini_(p_l_r)
                h_L, h_R = self._criteria_entropy_(p_l_r)
                item_beta_g_arr[iter_c][0] = item
                item_beta_g_arr[iter_c][1] = beta

                # G_l = (x_L_len / btch_sz) * h_L
                # G_r = (x_H_len / btch_sz) * h_R
                G = (x_L_len / btch_sz) * h_L + (x_H_len / btch_sz) * h_R
                item_beta_g_arr[iter_c][2] = G
            else:
                item_beta_g_arr[iter_c][2] = 10
            iter_c += 1
        bestG = item_beta_g_arr.T[2].argmin()
        out = np.array([item_beta_g_arr[bestG][1], item_beta_g_arr[bestG][2]])
        return out

    def get_with_sort(self, y_vec, inp_vec):
        srtd_ind = inp_vec[:,0].argsort()
        x_vec = inp_vec[srtd_ind]
        y_vec = y_vec[srtd_ind]


    def fit(self, X_train, y_train):
        self.x_arrList = self._init_list_of_arrs_(self._list_size_)
        self.y_arrList = self._init_list_of_arrs_(self._list_size_)
        best_features_beta = np.zeros((self._list_size_, 2))

        features = X_train.shape[1]
        features_list = [i for i in range(features)]
        leaf_list = []
        leaf_size_list = []
        b_g_arr = np.zeros((features, 2))

        self.x_arrList[0] = X_train
        self.y_arrList[0]= y_train
        print("max_depth = ", self._depth_, "\t", "list_size = ", self._list_size_)
        print(0, self.x_arrList[0].shape)
        print("-------------------------")
        iter = 0
        max_dict = []
        for i in range(int(pow(2, self._depth_ + 1) - 2)):
            # if self.x_arrList[i].shape[0] > 1:
            if np.unique(self.y_arrList[i]).shape[0] > 1:
                # choose best feature
                # starto = time.time()
                for feature in features_list:
                    b_g_arr[feature] = self._get_split_(self.y_arrList[i], self.x_arrList[i].T[feature])
                bst_feat = b_g_arr.T[1].argmin()
                # print(time.time() - starto)

                beta = b_g_arr[bst_feat][0]
                best_features_beta[i][0] = bst_feat
                best_features_beta[i][1] = beta
                mask = self.x_arrList[i].T[bst_feat] > beta

                self.y_arrList[i * 2 + 1] = np.copy(self.y_arrList[i][mask])
                self.y_arrList[i * 2 + 2] = np.copy(self.y_arrList[i][~mask])
                self.x_arrList[i * 2 + 1] = np.copy(self.x_arrList[i][mask])
                self.x_arrList[i * 2 + 2] = np.copy(self.x_arrList[i][~mask])


                # print("%8.f" % (i * 2 + 1), "%7.f" % bst_feat, "%7.f" % self.x_arrList[i * 2 + 1].shape[0])
                # print("%8.f" % (i * 2 + 2), "%7.f" % bst_feat, "%7.f" % self.x_arrList[i * 2 + 2].shape[0])
                # print((i * 2 + 1), "\t", bst_feat, "\t", self.x_arrList[i * 2 + 1].shape[0],  "\t\t",
                #         np.unique(self.y_arrList[i * 2 + 1]).shape[0])
                # print((i * 2 + 2), "\t", bst_feat, "\t", self.x_arrList[i * 2 + 2].shape[0],  "\t\t",
                #         np.unique(self.y_arrList[i * 2 + 2]).shape[0])
            else:
                if self.x_arrList[i].shape > np.zeros((1, 1)).shape:
                    leaf_list.append(i)
                    leaf_size_list.append(self.x_arrList[i].shape[0])
                # print((i * 2 + 1),  "\t\t", self.x_arrList[i * 2 + 1].shape[0],  "\t\t",
                #         np.unique(self.y_arrList[i * 2 + 1]).shape[0])
                # print((i * 2 + 2),  "\t\t", self.x_arrList[i * 2 + 2].shape[0],  "\t\t",
                #         np.unique(self.y_arrList[i * 2 + 2]).shape[0])

            max_dict.append(np.maximum(self.x_arrList[i * 2 + 1].shape[0], self.x_arrList[i * 2 + 2].shape[0]))
            # lvl separators
            if (i // (pow(2, iter + 2) - 2)) or i == 0:
                iter += 1
                print("-------------", iter,"------------")
                if max(max_dict) == self._leafsize_:
                    break
                else:
                    max_dict.clear()
        for i in range(int(pow(2, self._depth_ + 1) - 2), int(pow(2, self._depth_ + 2) - 2)):
            if (np.unique(self.y_arrList[i]).shape[0] > 1) and (self.x_arrList[i].shape > np.zeros((1, 1)).shape):
                leaf_list.append(i)
                leaf_size_list.append(self.x_arrList[i].shape[0])
        print(len(leaf_list), sum(leaf_size_list))

    def predict(self, X_test):
        pass

    def fit_predict(self):
        pass


class RandomForestClassifier:
    def __init__(self):
        pass

    def fit(self, X_train, y_train):
        pass

    def predict(self, X_test):
        pass

    def fit_predict(self):
        pass

df = pd.read_csv('./data/cs-training.csv', sep=',')
df = df.dropna()
X = df.as_matrix(columns=df.columns[1:])
y = df.as_matrix(columns=df.columns[:1])
y = y.reshape(y.shape[0])

ind_list = list()
sortoo = X[:,0].argsort()
a1 = X[sortoo]
y1 = y[sortoo]
u = np.unique(y1)
olo = np.where(y1 == u[0])
for i in range(1, olo[0].shape[0]-1):
    if olo[0][i]+1 != olo[0][i+1]:
        ind_list.append(i)

#
# iris = load_iris()
# X = iris.data
# y = iris.target

tree = DecisionTreeClassifier(max_depth=10, max_leafsize = 1)
start_t = time.time()
tree.fit(X, y)
print(time.time() - start_t)