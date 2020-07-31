from .data_pipeline import X_dic

def bu_dic():
    techset = ['Y', 'y', 't', 'Ylt', 'l', 'T','m', 'Yt', 'TT',
            'X', 'XY', 'h', 'q', 'Q', 'H', 'Xx', 'L', 'SY',
            'Yl', 'S', 'St', 'QY', 'd', 'B', 'Yq', 'BQ',
            'Tq', 'Bq', 'D', 'DYq', 'Ql', 'Sh', 'F', 'Xy',
            'ly', 'SXY', 'Ly', 'TY', 'SX', 'QT', 'QSY', 'Sy', 
            'Sqy', 'BY', 'SYq', 'qy', 'LY', 'By', 'Ylq',
            'HYl', 'Sq', 'Yqy', 'TYlq', 'Qh', 'Yh', 'Yx',
            'qt', 'Yy', 'Bh', 'QYq', 'Bqy', 'Qd', 'KY', 'K', 
            'BX', 'Sly', 'Xq', 'Kq', 'Qlq', 'Qq', 'BQqy', 'Kh', 'hq',
            'Tt', 'LSt', 'Bt', 'BYq', 'XYq', 'LQY', 'ty', 'BS', 'FS', 'SYt',
            'SYqy', 'Yqty', 'Dqy', 'Dq', 'Xt', 'Ty', 'Slqy', 'SYl', 'Qt', 'Ft', 'qty',
            'TYl', 'HY', 'BL', 'HSY', 'LYt', 'Yqt', 'dq', 'BYqt', 'SYy','0']

    number_list1 = []
    noteset = []
    for item in X_dic:
        it = item
        if (it in noteset) == False:
            noteset.append(it)
    for i in range(len(noteset)):
        number_list1.append(i)
    noteset.sort()
    note2id = dict(zip(noteset,number_list1))

    number_list2 = []
    for i in range(len(techset)):
        number_list2.append(i)
    techset.sort()
    tec2id = dict(zip(techset,number_list2))
    return note2id, tec2id
