from transformers import BertTokenizer
import torch
import math
from language_model import LanguageModel

tongyin = {}
with open('corpus/tokenized_tongyin.txt') as f:
	for line in f.readlines():
		word, words = line.split('\t')
		words = torch.LongTensor([int(s) for s in words.split()])
		# word = torch.LongTensor(word)
		tongyin[int(word)] = words


class Corrector:
	def __init__(self, model):
		self.model = model
		self.tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')

	def __call__(self, threshold, sentence):
		self.model.eval()
		print('\n\n')
		
		sentence = self.tokenizer.encode(sentence)[1:-1]
		for i in range(len(sentence) - 3):
			tokens = sentence[i:i+3]
			nxt = sentence[i+3]
			for replacement in tongyin[nxt]:
				diff = self._calc_ppl(tokens, nxt, replacement)
				if diff < threshold:
					# print(i, self.tokenizer.convert_ids_to_tokens([nxt]), '->', self.tokenizer.convert_ids_to_tokens([replacement]), ':', diff)
					# print(f'原句：{self.tokenizer.convert_ids_to_tokens(sentence)}，',
					# 	  f'第 {i} 个词被替换，替换后原句变为：{self.tokenizer.convert_ids_to_tokens(sentence.replace(nxt, replacement))}',
					# 	  sep='')
					print("第%d个字建议修改：%s -> %s, 概率提升： %f" %(i, self.tokenizer.convert_ids_to_tokens([nxt]), 
																	self.tokenizer.convert_ids_to_tokens([replacement]), -diff))
					return self.tokenizer.convert_ids_to_tokens(sentence.replace(nxt, replacement))
    
	def _calc_ppl(self, tokens, nxt, replacement):
		with torch.no_grad():
			tokens = torch.LongTensor(tokens).unsqueeze(0)
			pred = self.model(tokens)
			old_ppl = -math.log(pred[0][nxt], 10)
			new_ppl = -math.log(pred[0][replacement])
		return new_ppl - old_ppl

if __name__ == '__main__':
    model = LanguageModel()
    model.load_state_dict(torch.load('model/best_model.pth'))
    
    corrector = Corrector(model)
    
    while True:
        sentence = input('输入一句话：')
        new = corrector(0, sentence)
        print("修改前：", sentence)
        print("修改后：", ''.join(new))
        if sentence == 'exit':
            break