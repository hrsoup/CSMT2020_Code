from utils.util import load_model, extend_maps, prepocess_data_for_lstmcrf
from utils.data_pipeline import X, Y, X2, Y2, Note, p
from utils.dictionary_build import bu_dic
from config import style_transfer, data_model
from utils.data_pipeline import key, time, Note,pitch_list
from utils.util import fortree
from music21 import *
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import os
import copy

def music_style_transfer(style, model_name, no_se,f,score):

    no_se2 = copy.deepcopy(no_se)
    no_se3 = copy.deepcopy(no_se)

    for i in range(len(no_se)):
        no_se[i][1] = str(no_se[i][1])
        no_se[i] = ''.join(no_se[i])

    test_tag_lists = []
    test_word_lists = []
    test_word_lists.append(no_se)
    test_tag_lists.append(np.zeros((len(no_se),)))


    if model_name == 1:#crf
        style_path = os.path.join("./ckpts/"+'crf'+style+".pkl")
        crf_model = load_model(style_path)
        pred = crf_model.test(test_word_lists)

    elif model_name == 2:#bilstm
        style_path = os.path.join("./ckpts/"+'bilstm'+style+".pkl")
        note2id , tec2id = bu_dic()
        bilstm_word2id, bilstm_tag2id = extend_maps(note2id, tec2id, for_crf=False)
        bilstm_model = load_model(style_path)
        bilstm_model.model.bilstm.flatten_parameters()  
        pred, target_tag_list = bilstm_model.test(test_word_lists, test_tag_lists,
                                                    bilstm_word2id, bilstm_tag2id)

    elif model_name == 3: #bilstm_crf
        style_path = os.path.join("./ckpts/"+'bilstm_crf'+style+".pkl")
        note2id , tec2id = bu_dic()
        crf_word2id, crf_tag2id = extend_maps(note2id, tec2id, for_crf=True)
        bilstm_model = load_model(style_path)
        bilstm_model.model.bilstm.bilstm.flatten_parameters()
        test_word_lists, test_tag_lists = prepocess_data_for_lstmcrf(
            test_word_lists, test_tag_lists, test=True
        )
        pred, target_tag_list = bilstm_model.test(test_word_lists, test_tag_lists,
                                                        crf_word2id, crf_tag2id)

    elif model_name == 4: #bilstm_rules
        style_path = os.path.join("./ckpts/"+'bilstm_rules'+style+".pkl")
        note2id , tec2id = bu_dic()
        bilstm_word2id, bilstm_tag2id = extend_maps(note2id, tec2id, for_crf=False)
        bilstm_model = load_model(style_path)
        bilstm_model.model.bilstm.flatten_parameters()  
        pred, target_tag_list = bilstm_model.test(test_word_lists, test_tag_lists,
                                                    bilstm_word2id, bilstm_tag2id)


    path = os.path.join("./ckpts/"+'tree'+style+".pkl")
    tree_model = load_model(path)

    print(pred)
    N = ['1','q','2','w','3','4','r','5','T','6','y','7']

    distance = []
    for i in range(3,7):
        for j in Note:
            distance.append(str(i) + str(j))

    for j in range(len(no_se3)):
        if ('Y' in pred[0][j]) == True:
            t = []   
            no_se3[j][0] = str(no_se3[j][0][1])+N[p.index(no_se3[j][0][0])][::-1]       
            t.append(no_se3[j])
            temp = int(tree_model.model.predict(t).item())
            temp = distance[distance.index(no_se3[j][0]) + temp]
            print(temp)
            if temp[0] == '4':
                temp = '*' + temp[1]
            elif temp[0] == '5':
                temp = temp[1]
            elif temp[0] == '6':
                temp = '8' + temp[1]
            pred[0][j] = str(pred[0][j])+str(temp)

    stream1 = stream.Stream()
    i = 0
    for item in no_se2:
        n = note.Note(item[0],quarterLength=float(item[1]))
        n.addLyric(pred[0][i])
        stream1.append(n)
        i+=1  

    part = stream.Part()
    part.partName = str(f)
    part.append(stream1)
    score.insert(f,part)
                
    return pred



        
