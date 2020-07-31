from sklearn import tree

class TreeModel(object):
    def __init__(self,
                criterion = 'entropy'
                 ):

        self.model = tree.DecisionTreeClassifier(criterion = criterion)

    def train(self, x_train,y_train):
        self.model.fit(x_train,y_train)

    def test(self, x_test):
        pred_tag_lists = self.model.predict(x_test)
        return pred_tag_lists
    
    def score(self, x_test, y_test):
        s = self.model.score(x_test,y_test)
        return s
