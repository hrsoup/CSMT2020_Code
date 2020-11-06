import pickle
import copy
from utils.data_pipeline import Note, high, X, Y
from config import data_model
from .data_pipeline import key,time

def merge_maps(dict1, dict2):
    for key in dict2.keys():
        if key not in dict1:
            dict1[key] = len(dict1)
    return dict1


def save_model(model, file_name):
    with open(file_name, "wb") as f:
        pickle.dump(model, f)


def load_model(file_name):
    with open(file_name, "rb") as f:
        model = pickle.load(f)
    return model


def extend_maps(word2id, tag2id, for_crf=True):
    word2id['<unk>'] = len(word2id)
    word2id['<pad>'] = len(word2id)
    tag2id['<unk>'] = len(tag2id)
    tag2id['<pad>'] = len(tag2id)
    if for_crf:
        word2id['<start>'] = len(word2id)
        word2id['<end>'] = len(word2id)
        tag2id['<start>'] = len(tag2id)
        tag2id['<end>'] = len(tag2id)

    return word2id, tag2id


def prepocess_data_for_lstmcrf(word_lists, tag_lists, test=False):
    assert len(word_lists) == len(tag_lists)
    for i in range(len(word_lists)):
        word_lists[i].append("<end>")
        if not test: 
            tag_lists[i].append("<end>")

    return word_lists, tag_lists


def flatten_lists(lists):
    flatten_list = []
    for l in lists:
        if type(l) == list:
            flatten_list += l
        else:
            flatten_list.append(l)
    return flatten_list

def platlist(l):
    li = []
    for i in l:
        for j in i:
            li.append(j)
    return li   

def yinchen(distance, x,y):
    temp = distance.index(y) - distance.index(x) 
    return temp

def fortree(X ,Y):
    X_new = []
    Y_new = []
    for i in range(len(Y)):
        for j in range(len([i])):
            if ('Y' in Y[i][j]) == True:
                X_new.append(X[i][j])
                Y_new.append(Y[i][j])

    X = copy.deepcopy(X_new)

    Y = []
    for i in range(len(Y_new)):
        r = []
        for j in range(len(Y_new[i])):
            if ((Y_new[i][j] in high) == True) or ((Y_new[i][j] in Note) == True):
                r.append(Y_new[i][j])
        Y_new[i] = ''.join(r)

    for i in range(len(Y_new)):
        if Y_new[i][0] == '*':
            Y_new[i] = str(4) + str(Y_new[i][1]) 
        elif Y_new[i][0] == '8':
            Y_new[i] = str(6) + str(Y_new[i][1]) 
        else:
            Y_new[i] = str(5) + str(Y_new[i][0]) 
            
    distance = []
    for i in range(3,7):
        for j in Note:
            distance.append(str(i) + str(j))
            
    def yinchen(x,y):
        temp = distance.index(y) - distance.index(x) 
        return temp

    Y = []
    for i in range(len(X_new)):
        X_new[i] = ''.join(X_new[i])
        Y.append(yinchen(X_new[i][0:2][::-1],Y_new[i]))
        
    count = 0 
    c = []
    for item in Y:
        if (str(item) in c)== False:
            c.append(str(item))
            count += 1


    return X, Y
