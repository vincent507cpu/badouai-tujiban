from transformers import BertTokenizer
import os

tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')

files = os.listdir('corpus/')
outfile = open('corpus/tokenized_pairs.txt', 'w', encoding='utf8')
corpus = set()
for file in files:
	if file.endswith('txt'):
		f = open('corpus/' + file, encoding='utf8')
		for line in f.readlines():
			if len(line) > 512:
				line = line[:510]
			tokens = tokenizer.encode(line)[1:-1]
			for i in range(len(tokens) - 3):
				words = tokens[i:i + 3]
				words = ' '.join([str(s) for s in words])
				label = str(tokens[i + 3])
				if words not in corpus:
					corpus.add(words)
					outfile.write(words + '\t' + label + '\n')
outfile.close()

with open('tongyin.txt', encoding='utf8') as f:
	outfile = open('corpus/tokenized_tongyin.txt', 'w', encoding='utf8')
	for line in f.readlines():
		char, chars = line.strip().split()
		char = tokenizer.encode(char)[1]
		tokens = tokenizer.encode(chars)[1:-1]
		char, tokens = str(char), [str(s) for s in tokens]
		outfile.write(char + '\t' + ' '.join(tokens) + '\n')
