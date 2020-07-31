import os

class data_model(object): 
    mode = 2 #1:train_evaluate
                         #2:music_style_transfer
                         #3:decisiontree
    train_data = 'Northern school'
    data_path = os.path.join('Dataset',train_data)
    model = 4 #1:crf
                         #2:bilstm
                         #3:bilstm_crf
                         #4:bilstm_rules

class style_transfer(object): 
    base = 'Northern school' 
    style = 'Northern school' 
    score_name = 'WuBangZi'
    base_path = os.path.join('Dataset', base, score_name+'.docx')
    #Comes from melody transfer
    input = [['A3', 1.5], ['B3', 0.5], ['A3', 1.0], ['G3', 1.0], ['E4', 2.0], ['E4', 2.0], ['G4', 1.5], ['C5', 0.5], ['C5', 1.0], ['C4', 1.0], ['D4', 2.0], ['D4', 2.0]]