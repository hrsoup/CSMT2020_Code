from sklearn.model_selection import KFold
import numpy as np
from music21 import *
import warnings
import argparse
warnings.filterwarnings("ignore")

from train_test import crf_train_eval, bilstm_train_and_eval, tree_train_and_eval
from utils.data_pipeline import X_base, X, Y, X2, Y2
from utils.util import extend_maps, prepocess_data_for_lstmcrf, fortree
from utils.dictionary_build import bu_dic
from config import data_model, style_transfer
from style_transfer import music_style_transfer
from utils.word2staff import w2staff

def main():
    global X,Y
    if data_model.mode == 1: #Train and evaluate
        note2id , tec2id = bu_dic()
        cv = KFold(n_splits=10, shuffle=True, random_state=1) #10-fold cross-validation
        accuracy_1 = []
        accuracy_2 = []
        accuracy_3 = []
        forcount = 0
        for train_ids, valid_ids in cv.split(X):
            print("The {}th:".format(forcount))
            X = np.array(X)
            Y = np.array(Y)
            train_word_lists, train_tag_lists = X[train_ids], Y[train_ids]
            test_word_lists, test_tag_lists = X[valid_ids],Y[valid_ids]
            dev_word_lists, dev_tag_lists = X[valid_ids],Y[valid_ids]

            #----------------------crf----------------------------------------------#
            if data_model.model == 1:
                accuracy1,accuracy2,accuracy3 = crf_train_eval(
                    (train_word_lists, train_tag_lists),
                    (test_word_lists, test_tag_lists)
                )    
            #------------------------------------------------------------------------#

            #----------------------bi-lstm-----------------------------------------#
            elif data_model.model == 2:
                if forcount == 0:
                    bilstm_word2id, bilstm_tag2id = extend_maps(note2id, tec2id, for_crf=False)
                accuracy1,accuracy2,accuracy3 = bilstm_train_and_eval(
                    (train_word_lists, train_tag_lists),
                    (dev_word_lists, dev_tag_lists),
                    (test_word_lists, test_tag_lists),
                    bilstm_word2id, bilstm_tag2id,
                    crf=False,
                    rules = False
                )
            #-------------------------------------------------------------------------#


            #----------------------bi-lstm+crf-------------------------------------#
            elif data_model.model == 3:
                if forcount == 0:
                    crf_word2id, crf_tag2id = extend_maps(note2id, tec2id, for_crf=True)
                    train_word_lists1, train_tag_lists1 = prepocess_data_for_lstmcrf(
                        train_word_lists, train_tag_lists
                    )
                    dev_word_lists1, dev_tag_lists1 = prepocess_data_for_lstmcrf(
                        dev_word_lists, dev_tag_lists
                    )
                    test_word_lists1, test_tag_lists1 = prepocess_data_for_lstmcrf(
                        test_word_lists, test_tag_lists, test=True
                    )
                
                accuracy1, accuracy2,accuracy3 = bilstm_train_and_eval(
                    (train_word_lists1, train_tag_lists1),
                    (dev_word_lists1, dev_tag_lists1),
                    (test_word_lists1, test_tag_lists1),
                    crf_word2id, crf_tag2id,
                    crf = True,
                    rules = False
                )
            #--------------------------------------------------------------------------#

            #----------------------bi-lstm+rules----------------------------------#
            elif data_model.model == 4:
                if forcount == 0:
                    bilstm_word2id, bilstm_tag2id = extend_maps(note2id, tec2id, for_crf=False)
                accuracy1,accuracy2,accuracy3 = bilstm_train_and_eval(
                    (train_word_lists, train_tag_lists),
                    (dev_word_lists, dev_tag_lists),
                    (test_word_lists, test_tag_lists),
                    bilstm_word2id, bilstm_tag2id,
                    crf=False,
                    rules = True
                )
            #-------------------------------------------------------------------------#


            accuracy_1.append(accuracy1)
            print(accuracy1)
            if accuracy2 != -1:
                accuracy_2.append(accuracy2)
                print(accuracy2)
            else:
                print("No OOV occur.")
            accuracy_3.append(accuracy3)
            print(accuracy3)
            
            forcount += 1

        print(np.mean(accuracy_1))
        print(np.mean(accuracy_2))
        print(np.mean(accuracy_3))

    elif data_model.mode == 2: #Music style Transfer
        score = stream.Score()
        if style_transfer.base == 'Southern school':
            pred_skills2 = music_style_transfer('Northern school',3,style_transfer.input,3,score)
            pred_skills2 = music_style_transfer('Northern school',4,style_transfer.input,4,score)
        elif style_transfer.base == 'Northern school':
            pred_skills1 = music_style_transfer('Southern school',3,style_transfer.input,3,score)
            pred_skills2 = music_style_transfer('Southern school',4,style_transfer.input,4,score)
        elif style_transfer.base == 'Other school' and style_transfer.style == 'Northern school':
            pred_skills2 = music_style_transfer('Northern school',3,style_transfer.input,3,score)
            pred_skills2 = music_style_transfer('Northern school',4,style_transfer.input,4,score)
        elif style_transfer.base == 'Other school' and style_transfer.style == 'Southern school':
            pred_skills1 = music_style_transfer('Southern school',3,style_transfer.input,3,score)
            pred_skills2 = music_style_transfer('Southern school',4,style_transfer.input,4,score)

        score.write('xml',fp='transfer results.xml') 
        # w2staff(pred_skills1, pred_skills2)
        # print(pred_skills1, pred_skills2)

    elif data_model.mode == 3: #appoggaiture tagging
        accuracy = []
        x, y = fortree(X2, Y2)
        print(x,y)
        for i in range(10):
            acc = tree_train_and_eval(x, y)
            accuracy.append(acc)
        print(np.mean(accuracy))     

if __name__ == "__main__":
    main()