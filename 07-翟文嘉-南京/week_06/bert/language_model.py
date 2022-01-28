import torch
from torch import nn
from torch.nn import functional as F
from transformers import BertModel, AdamW
import os

from torch.utils.data import DataLoader
from time import time
from tqdm import tqdm

torch.cuda.empty_cache()
# tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
device = 'cuda' if torch.cuda.is_available() else 'cpu'

if not os.path.exists('model'):
	os.mkdir('model')


class LanguageModel(nn.Module):
	def __init__(self):
		super().__init__()

		if device == 'cpu':
			with torch.no_grad():
				self.bert = BertModel.from_pretrained('bert-base-chinese', return_dict=False)
		elif device == 'cuda':
			self.bert = BertModel.from_pretrained('bert-base-chinese', return_dict=False)
  
		# with torch.no_grad():
		# 	self.bert = BertModel.from_pretrained('bert-base-chinese', return_dict=False)

		self.dropout = nn.Dropout(0.5)
		self.linear = nn.Linear(
			self.bert.state_dict()['embeddings.word_embeddings.weight'].shape[1],
			self.bert.state_dict()['embeddings.word_embeddings.weight'].shape[0]
		)

	def forward(self, X, y=None):
		_, X = self.bert(X, return_dict=False)
		X = self.dropout(X)
		pred = self.linear(X)

		if y is not None:
			return F.cross_entropy(pred, y)
		else:
			return F.softmax(pred, dim=-1)


class Dataset:
	def __init__(self, path):
		self.tokens, self.labels = [], []
		with open(path) as f:
			for line in f.readlines():
				tokens, label = line.split('\t')
				tokens = tokens.split()
				tokens = [int(t) for t in tokens]
				self.tokens.append(tokens)
				self.labels.append(int(label))
		self.tokens = torch.LongTensor(self.tokens)
		self.labels = torch.LongTensor(self.labels)

	def __getitem__(self, idx):
		return self.tokens[idx], self.labels[idx]

	def __len__(self):
		return len(self.tokens)


def train(model, dataloader, epochs=10, lr=1e-4, verbose=True):
	model = model.to(device)
	model.train()
	optimizer = AdamW(params=model.parameters(), lr=lr)
 
	min_loss = float('inf')
	# epoch, breakeven = 0, 0
	for epoch in range(epoch):
		# epoch += 1
		start = time()
		loss = 0
		for tokens, labels in tqdm(dataloader):
			optimizer.zero_grad()
			tokens = tokens.to(device)
			labels = labels.to(device)
			loss_ = model(tokens, labels)
			loss_.backward()
			optimizer.step()
			loss += loss_.item()
			# batch += len(tokens)
		if loss < min_loss:
			print(f'{epoch}th epoch model saved.')
			torch.save(model.state_dict(), f'model/best_model_{epoch}.pth')
			min_loss = loss
		# else:
		# 	breakeven += 1
		# 	torch.save(model.state_dict(), f'model/bemodel.pth')
		# 	if breakeven > 2:
		# 		return
		# torch.save(model.state_dict(), 'model/best_model.pth')
		# avg_loss /= batch
		used_time = time() - start
  
		# if not epoch:
		# 	print(f'{epoch} epoch done, used {int(used_time / 60)} min {used_time % 60:.2f} s.')
   
		if verbose:
			print(f'{epoch} round loss: {min_loss:.2f}.')


if __name__ == '__main__':
	# with open('corpus/reversed_pairs.json', 'r', encoding='utf8') as f:
	# 	data = json.load(f)
	# print(type(data[0]))
	# labels, tokens = data.items()
	dataset = Dataset('corpus/tokenized_pairs.txt')
	dataloader = DataLoader(dataset, batch_size=1024, shuffle=True, drop_last=False)
	model = LanguageModel()
	print('ready. start training...')
	start = time()
	train(model, dataloader)
	# torch.save(model.state_dict(), 'model/checkpoint.pth')
	print(f'training done, used {time() - start:.2f} s.')
