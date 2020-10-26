import torch
import torch.nn as nn
from torch.nn.utils.rnn import pad_packed_sequence, pack_padded_sequence
from config import data_model

class BiLSTM_RULES(nn.Module):
    def __init__(self, vocab_size, emb_size, hidden_size, out_size):
        super(BiLSTM_RULES, self).__init__()
        self.embedding = nn.Embedding(vocab_size, emb_size)
        self.bilstm = nn.LSTM(emb_size, hidden_size,
                              batch_first=True,
                              bidirectional=True)

        self.lin = nn.Linear(2*hidden_size, out_size)

    def forward(self, sents_tensor, lengths):
        emb = self.embedding(sents_tensor)  # [B, L, emb_size]

        packed = pack_padded_sequence(emb, lengths, batch_first=True)
        rnn_out, _ = self.bilstm(packed)
        # rnn_out:[B, L, hidden_size*2]
        rnn_out, _ = pad_packed_sequence(rnn_out, batch_first=True)

        scores = self.lin(rnn_out)  # [B, L, out_size]

        return scores

    def test(self, word_lists, sents_tensor, lengths, id2tag):
        logits = self.forward(sents_tensor, lengths)  # [B, L, out_size]
        tuyin = id2tag['T']
        huashe = id2tag['S']
        dieyin = id2tag['d']
        dayin = id2tag['D']
        zengyin = id2tag['y']
        chanyin = id2tag['t']
        duoyin = id2tag['m']
        xialiyin = id2tag['l']
        xiahuayin = id2tag['h']
        xia = [duoyin,xialiyin,xiahuayin]
        shangliyin = id2tag['L']
        shanghuayin = id2tag['H']
        wujiqiao = id2tag['0']
        if data_model.mode == 1 and data_model.train_data == 'Northern school':
            h1 = 1.1
            h2 = 1.08 
            shang = [shangliyin,shanghuayin]
            for i in range(logits.size(0)): 
                if torch.cuda.is_available():
                    P1 = torch.ones((logits.size(1),logits.size(2))).cuda()
                else:
                    P1 = torch.ones((logits.size(1),logits.size(2)))
                for j in range(0,logits.size(1)):
                    P1[j][tuyin] = h1*P1[j][tuyin]
                    P1[j][huashe] = h1*P1[j][huashe]
                    P1[j][duoyin] = h1*P1[j][duoyin]
                    P1[j][shanghuayin] = h1*P1[j][shanghuayin]
                    P1[j][xiahuayin] = h1*P1[j][xiahuayin]
                    P1[j][chanyin] = P1[j][chanyin] / h1
                    P1[j][dieyin] = P1[j][dieyin] / h1
                    P1[j][dayin] = P1[j][dayin] / h1
                    P1[j][zengyin] = P1[j][zengyin] / h1
                    if (j <= logits.size(1)-1) and (torch.max(logits[i][j]) in xia) == True:
                        P1[j+1][shangliyin] = h2*P1[j+1][shangliyin]
                        P1[j+1][shanghuayin] = h2*P1[j+1][shangliyin]
                logits[i] = P1*logits[i]
        elif data_model.mode == 1 and data_model.train_data == 'Southern school':
            k1 = 1.1
            k2 = 1.08
            k3 = 1.05
            k4 = 1.04
            logits = self.forward(sents_tensor, lengths)  # [B, L, out_size]
            for i in range(logits.size(0)): 
                P1 = torch.ones((logits.size(1),logits.size(2))).cuda()
                for j in range(1,lengths[i]):
                    if word_lists[i][j][0:2] > word_lists[i][j-1][0:2]:
                        P1[j][dieyin] = P1[j][dieyin] * k3
                        P1[j][dayin] = P1[j][dayin] / k3
                    elif word_lists[i][j][0:2] < word_lists[i][j-1][0:2]:
                        P1[j][dieyin] = P1[j][dieyin] / k4
                        P1[j][dayin] = P1[j][dayin] * k4
                for j in range(0,lengths[i]):
                    P1[j][tuyin] = P1[j][tuyin] /k1
                    P1[j][huashe] = P1[j][huashe] / k1
                    P1[j][duoyin] = P1[j][duoyin] /k1
                    P1[j][shanghuayin] = P1[j][shanghuayin] /k1
                    P1[j][xiahuayin] = P1[j][xiahuayin] / k1
                    P1[j][chanyin] = P1[j][chanyin] * k1
                    P1[j][dieyin] = P1[j][dieyin] * k1
                    P1[j][dayin] = P1[j][dayin] * k1
                    P1[j][zengyin] = P1[j][zengyin] * k1
                    print(word_lists[i][j])
                    if word_lists[i][j][0] != '0' and (word_lists[i][j][1] == '3' or word_lists[i][j][1] =='4' or word_lists[i][j][1]=='5'):
                        if word_lists[i][j][1] != '#' or word_lists[i][j] !='b':
                            if int(word_lists[i][j][2]) >= 2:
                                P1[j][wujiqiao] = P1[j][wujiqiao] / k2
                        else:
                            if int(word_lists[i][j][3]) >= 2:
                                P1[j][wujiqiao] = P1[j][wujiqiao] / k2                        
                logits[i] = P1*logits[i]
        _, batch_tagids = torch.max(logits, dim=2)  

        return batch_tagids