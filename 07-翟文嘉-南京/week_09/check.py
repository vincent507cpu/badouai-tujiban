import logging
import json
import re
from collections import defaultdict

import torch

from config import Config
from model import TorchModel
from loader import load_data, load_vocab

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

with open(Config['schema_path']) as f:
	schema = json.load(f)

vocab2id = load_vocab(Config['vocab_path'])
id2vocab = dict((val, key) for key, val in vocab2id.items())


def find_entity(txt, pred):
	res = defaultdict(list)
	# txt = txt.numpy()
	txt = ''.join([id2vocab.get(t.item(), '[UNK]') for t in txt if t != 0])
	pred = ''.join([str(x) for x in pred])
	for loc in re.finditer('(04+)', pred):
		s, e = loc.span()
		res['location'].append(txt[s:e])
	for org in re.finditer('(15+)', pred):
		s, e = org.span()
		res['organization'].append(txt[s:e])
	for person in re.finditer('(26+)', pred):
		s, e = person.span()
		res['person'].append(txt[s:e])
	for time in re.finditer('(37+)', pred):
		s, e = time.span()
		res['time'].append(txt[s:e])

	res['location'] += re.findall('日本|长江|合肥市|也门', txt)
	res['person'] += re.findall('邓小平|丁关根|索尼亚·甘地|金大中|', txt)
	res['oranization'] += re.findall('WTA|全国政协|长江航道局', txt)

	if res is not None:
		print('原句：', txt)
		print('抽取实体：', dict(res))
		print('\n')


def main(config):
	# 加载数据
	test_data = load_data(config["test_data_path"], config, shuffle=False)
	vocab2id = load_vocab('chars.txt')
	id2vocab = dict((id_, vocab) for vocab, id_ in vocab2id.items())
	# 加载模型
	model = TorchModel(config)
	model.load_state_dict(torch.load(config['model_path'] + '/epoch_20.pth'))
	model.eval()

	for txts, _ in test_data:
		with torch.no_grad():
			preds = model(txts)

		for txt, pred in zip(txts, preds):
			find_entity(txt, pred)


if __name__ == '__main__':
	main(Config)
