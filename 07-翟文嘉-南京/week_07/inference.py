
import torch
import os
import numpy as np
import logging
from model import TorchModel
from loader import DataGenerator
import pandas as pd
from transformers import BertTokenizer

logging.basicConfig(level=logging.INFO, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

result = pd.read_csv('output/result.csv')
index = np.argmax(np.array(result['acc'].to_list()))
config = dict((key, result[key][index]) for key in result.keys())

dl = DataGenerator(config['train_data_path'], config)
tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')

model_ = TorchModel(config)
model_.load_state_dict(torch.load(os.path.join(config["model_path"], f"{config['model_type']}_lr{config['learning_rate']}_hs{config['hidden_size']}_pooling{config['pooling_style']}_op{config['optimizer']}.pth")))

if __name__ == '__main__':
    while True:
        condidate = input('type some words: ')
        
        if condidate == 'exit':
            print('exit')
            break
        
        tokens = tokenizer.encode(condidate)
        tokens = torch.LongTensor([dl.padding(tokens)])
        
        if torch.cuda.is_available():
            tokens = tokens.to('cuda')
            model_ = model_.to('cuda')

        output = model_(tokens).squeeze()
        
        pred = torch.argmax(output).item()
        print(f'prediction for "{condidate}": {dl.index_to_label[pred]}')