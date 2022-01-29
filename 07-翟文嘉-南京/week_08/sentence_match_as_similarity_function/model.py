# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
from torch.optim import Adam, SGD
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
from transformers import BertModel, BertConfig

"""
建立网络模型结构
"""


class SentenceMatchNetwork(nn.Module):
    def __init__(self, config):
        super(SentenceMatchNetwork, self).__init__()
        pretrain_model_path = config["pretrain_model_path"]
        self.bert_encoder = BertModel.from_pretrained(pretrain_model_path)
        hidden_size = self.bert_encoder.pooler.dense.out_features
        self.classify_layer = nn.Linear(hidden_size, 2)
        self.loss = nn.CrossEntropyLoss()

    # 计算余弦距离
    # 0.5 * (1 + cosine)的目的是把-1到1的余弦值转化到0-1，这样可以直接作为得分
    # def cosine_distance(self, tensor1, tensor2):
    #     tensor1 = torch.nn.functional.normalize(tensor1, dim=-1)
    #     tensor2 = torch.nn.functional.normalize(tensor2, dim=-1)
    #     cosine = torch.sum(torch.mul(tensor1, tensor2), axis=-1)
    #     return 0.5 * (1 + cosine)
    def cosine_diatance(self, query, library):
        result = torch.empty(len(library))
        for i in range(len(library)):
            result[i] = self.calc_similarity(query, library[i])
        return result

    def calc_similarity(self, tensor1, tensor2):
        return sum(tensor1 * tensor2) / (torch.sqrt(sum([s**2 for s in tensor1])) * torch.sqrt(sum([s**2 for s in tensor2])))

    # 同时传入两个句子的拼接编码
    # 输出一个相似度预测，不匹配的概率
    def forward(self, input_ids, target=None):
        x = self.bert_encoder(input_ids)[1]
        x = self.classify_layer(x)
        #如果有标签，则计算loss
        if target is not None:
            return self.loss(x, target.squeeze())
        #如果无标签，预测相似度
        else:
            return torch.softmax(x, dim=-1)#[:, 1] #如果改为x[:,0]则是两句话不匹配的概率

    #输入一个句子和一组备选，输出最高分命中的index
    def most_similar(self, input_id, target_ids):
        input_ids = torch.stack([input_id] * len(target_ids))
        res = self.forward(input_ids, target_ids)
        return int(torch.argmin(res))



def choose_optimizer(config, model):
    optimizer = config["optimizer"]
    learning_rate = config["learning_rate"]
    if optimizer == "adam":
        return Adam(model.parameters(), lr=learning_rate)
    elif optimizer == "sgd":
        return SGD(model.parameters(), lr=learning_rate)


if __name__ == "__main__":
    from config import Config
    Config["vocab_size"] = 10
    Config["max_length"] = 4
    model = SentenceMatchNetwork(Config)
    # s1 = torch.LongTensor([[1,2,3,0], [2,2,0,0]])
    # s2 = torch.LongTensor([[1,2,3,4], [3,2,3,4]])
    # l = torch.LongTensor([[1],[0]])
    # y = model(s1, l)
    # print(y)
    # print(model.state_dict())
    # s1 = torch.LongTensor([1,2,3,4])
    # s2 = torch.LongTensor([[2,2,3,4], [1,2,3,4]])
    # print(model.most_similar(s2, s1))
    query = torch.LongTensor([1, 2, 3, 4])
    library = torch.LongTensor([[1, 2, 3, 4], [4, 3, 2, 1]])
    print(model.cosine_diatance(query, library))