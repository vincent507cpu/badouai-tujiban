import logging
import json
import re
from collections import defaultdict

from flask import Flask, request
app = Flask(__name__)

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
Config["vocab_size"] = len(vocab2id)


def find_entity(txt, pred):
	res = defaultdict(list)
	tmp = []
	# txt = ''.join([id2vocab.get(t.item(), '[UNK]') for t in txt if t != 0])

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

	if res is not None:
		before = '<p>正则表达式处理前：' + str(dict(res)) + '</p>'
		# print('正则表达式处理前：', dict(res))
		tmp.append(before)

		if re.findall('巴黎|日本|张家港市|美国', txt):
			entity = [s for s in re.findall('巴黎|日本|张家港市|美国', txt) if s]
			res['location'] += entity
		if re.findall('邓小平|丁关根|索尼亚·甘地|金大中', txt):
			entity = [s for s in re.findall('邓小平|丁关根|索尼亚·甘地|金大中|', txt) if s]
			res['person'] += entity
		if re.findall('WTA|全国政协|长江航道局|国大党|国务院', txt):
			entity = [s for s in re.findall('WTA|全国政协|长江航道局|国大党|国务院', txt) if s]
			res['oranization'] += entity

		for key, val in res.items():
			res[key] = list(set(val))
		after = '<p>正则表达式处理后：' + str(dict(res)) + '</p>'
		# print('正则表达式处理后：', dict(res))
		# print('\n')
		tmp.append(after)

	return tmp

@app.route('/ner', methods=['GET'])
def main():
	# test_data = load_data(config['test_data_path'], config)
	# 加载模型
	model = TorchModel(Config)
	model.load_state_dict(torch.load(Config['model_path'] + '/epoch_20.pth'))
	model.eval()

	# for txts, _ in test_data:
	# 	with torch.no_grad():
	# 		preds = model(txts)
	#
	# 	for txt, pred in zip(txts, preds):
	# 		find_entity(txt, pred)
	# while True:
	# 	input_txt = input('输入句子：')
	# 	if input_txt != 'exit':
	output = []
	input_txt = request.args.get('sentence')
	output.append('<h1>原句：' + input_txt + '</h1>')
	new = [vocab2id.get(t, 0) for t in input_txt]
	new = new[:Config['max_length']]
	new += [0] * (Config['max_length'] - len(new))
	new = torch.LongTensor(new).unsqueeze(0)

	with torch.no_grad():
		pred = model(new)

	processed = find_entity(input_txt, pred)
		# else:
		# 	break
	output += processed
	return '\n'.join(output)


if __name__ == '__main__':
	app.run(port=1988, debug=True)
	# main(Config)
