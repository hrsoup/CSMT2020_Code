from models.crf import CRFModel
from models.bilstm_crf import BILSTM_Model
from models.tree import TreeModel
from utils.util import platlist, save_model, flatten_lists
from config import data_model

from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd

def crf_train_eval(train_data, test_data, remove_O=False):

    train_word_lists, train_tag_lists = train_data
    test_word_lists, test_tag_lists = test_data

    crf_model = CRFModel()
    crf_model.train(train_word_lists, train_tag_lists)
    save_model(crf_model, "./ckpts/"+"crf"+data_model.train_data+".pkl")

    pred_tag_lists = crf_model.test(test_word_lists)

    pred_tag_lists = platlist(pred_tag_lists)
    test_tag_lists = platlist(test_tag_lists)
    
    train_word_lists = platlist(train_word_lists)
    test_word_lists = platlist(test_word_lists)
    
    oov_list = []
    for i in range(len(test_word_lists)):
        if (test_word_lists[i] in train_word_lists) == False:
            oov_list.append(i)
            
    count1 = 0
    count3 = 0
    for i in range(len(pred_tag_lists)):
        if (pred_tag_lists[i] == test_tag_lists[i]) and (i in oov_list) == False :
            count1 += 1
        if (pred_tag_lists[i] == test_tag_lists[i]):
            count3 += 1
    accuracy1 = count1 / (len(pred_tag_lists) - len(oov_list))
    accuracy3 = count3 / len(pred_tag_lists)

    count2 = 0
    for i in range(len(pred_tag_lists)):
        if (pred_tag_lists[i] == test_tag_lists[i]) and (i in oov_list) == True :
            count2 += 1
    if len(oov_list) != 0:
        accuracy2 = count2 / len(oov_list)
    else:
        accuracy2 = -1

    return accuracy1,accuracy2,accuracy3

def bilstm_train_and_eval(train_data, dev_data, test_data,
                          word2id, tag2id, crf=True, rules =True):
    train_word_lists, train_tag_lists = train_data
    dev_word_lists, dev_tag_lists = dev_data
    test_word_lists, test_tag_lists = test_data

    vocab_size = len(word2id)
    out_size = len(tag2id)
    bilstm_model = BILSTM_Model(vocab_size, out_size, crf=crf, rules=rules)
    bilstm_model.train(train_word_lists, train_tag_lists,
                       dev_word_lists, dev_tag_lists, word2id, tag2id)

    if crf == True:
        model_name = "bilstm_crf"
    else:
        if rules == True:
            model_name = "bilstm_rules"
        else:
            model_name = "bilstm"
    save_model(bilstm_model, "./ckpts/"+model_name+data_model.train_data+".pkl")

    pred_tag_lists, test_tag_lists = bilstm_model.test(
        test_word_lists, test_tag_lists, word2id, tag2id)

    pred_tag_lists = platlist(pred_tag_lists)
    test_tag_lists = platlist(test_tag_lists)    

    oov_list = []
    for i in range(len(test_word_lists)):
        if (test_word_lists[i] in train_word_lists) == False:
            oov_list.append(i)
        
    count1 = 0
    count3 = 0
    if crf == True:
        for i in range(len(pred_tag_lists)):
            if (pred_tag_lists[i] == test_tag_lists[i]) and (i in oov_list) == False:
                count1 += 1
            if (pred_tag_lists[i] == test_tag_lists[i]):
                count3 += 1
        accuracy1 = count1 / (len(test_tag_lists) - len(test_word_lists) - len(oov_list))
        accuracy3 = count3 / (len(test_tag_lists) - len(test_word_lists))
           
    else:
        for i in range(len( pred_tag_lists)):
            if ( pred_tag_lists[i] == test_tag_lists[i]) and (i in oov_list) == False:
                count1 += 1
            if ( pred_tag_lists[i] == test_tag_lists[i]):
                count3 += 1
        accuracy1 = count1 / (len(test_tag_lists ) - len(oov_list))
        accuracy3 = count3 / len(test_tag_lists )
        
    count2 = 0
    for i in range(len( pred_tag_lists)):
        if ( pred_tag_lists[i] == test_tag_lists[i]) and (i in oov_list) == True:
            count2 += 1
    if len(oov_list) == 0:
        accuracy = -1 
    else:
        accuracy2 = count2 / len(oov_list)

    return accuracy1, accuracy2,accuracy3

def tree_train_and_eval(x, y):
    x_train,x_test,y_train,y_test = train_test_split(x, y ,test_size = 0.2)
    tree_model = TreeModel()
    tree_model.train(x_train,y_train)
    save_model(tree_model, "./ckpts/"+"tree"+data_model.train_data+".pkl")
    pred = tree_model.test(x_test)
    count = 0
    for i in range(len(pred)):
        if (pred[i] == y_test[i]).all() == True:
            count += 1
    accuracy = tree_model.score(x_test,y_test)
    return accuracy
