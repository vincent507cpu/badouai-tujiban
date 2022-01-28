# -*- coding: utf-8 -*-

import torch
import os
import random
import numpy as np
import logging
from config import Config
from model import TorchModel, choose_optimizer
from evaluate import Evaluator
from loader import load_data
import pandas as pd
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

"""
模型训练主程序
"""


seed = Config["seed"]
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed_all(seed)

def main(config):
    #创建保存模型的目录
    if not os.path.isdir(config["model_path"]):
        os.mkdir(config["model_path"])
    #加载训练数据
    train_data = load_data(config["train_data_path"], config)
    #加载模型
    model = TorchModel(config)
    # 标识是否使用gpu
    cuda_flag = torch.cuda.is_available()
    if cuda_flag:
        logger.info("gpu可以使用，迁移模型至gpu")
        model = model.cuda()
    #加载优化器
    optimizer = choose_optimizer(config, model)
    #加载效果测试类
    evaluator = Evaluator(config, model, logger)
    #训练
    max_acc = 0
    for epoch in range(config["epoch"]):
        epoch += 1
        model.train()
        logger.info("epoch %d begin" % epoch)
        train_loss = []
        for index, batch_data in enumerate(train_data):
            if cuda_flag:
                batch_data = [d.cuda() for d in batch_data]

            optimizer.zero_grad()
            input_ids, labels = batch_data   #输入变化时这里需要修改，比如多输入，多输出的情况
            loss = model(input_ids, labels)
            loss.backward()
            optimizer.step()

            train_loss.append(loss.item())
            if index % int(len(train_data) / 2) == 0:
                logger.info("batch loss %f" % loss)
        logger.info("epoch average loss: %f" % np.mean(train_loss))
        acc = evaluator.eval(epoch)
        
        if acc >= max_acc:
            model_path = os.path.join(config["model_path"], f"{config['model_type']}_lr{config['learning_rate']}_hs{config['hidden_size']}_pooling{config['pooling_style']}_op{config['optimizer']}.pth")
            torch.save(model.state_dict(), model_path)  #保存模型权重
            max_acc = acc
    return max_acc

if __name__ == "__main__":
    # main(Config)
    res = defaultdict(list)
    
    #对比所有模型
    #中间日志可以关掉，避免输出过多信息
    # 超参数的网格搜索
    # for model in 'fast_text', ["cnn", 'gru', 'bert']:
    for model in ['fast_text', 'cnn',  'gru', 'bert']:
        Config["model_type"] = model
        for lr in [1e-2, 1e-3, 1e-4]:
            Config["learning_rate"] = lr
            for hidden_size in [64, 128, 256]:
                Config["hidden_size"] = hidden_size
                for optimizer in ['adam', 'sgd']:
                    Config["optimizer"] = optimizer
                    for pooling_style in ["max", "avg"]:
                        Config["pooling_style"] = pooling_style
                        acc = main(Config)
                        # print("最后一轮准确率：", main(Config), "当前配置：", Config)
                        for key in Config.keys():
                            res[key].append(Config[key])
                        res['acc'].append(acc)

    df = pd.DataFrame(res)
    df.to_csv('output/result.csv', header=True, index=False)