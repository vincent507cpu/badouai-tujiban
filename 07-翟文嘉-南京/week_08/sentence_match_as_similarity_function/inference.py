from config import Config
from model import SentenceMatchNetwork
from loader import load_data, load_schema

import torch
from transformers import BertTokenizer

def main(config):
	model = SentenceMatchNetwork(config)
	model.load_state_dict(torch.load('model_output/best_model.pth', map_location=torch.device('cpu')))
	tokenizer = BertTokenizer.from_pretrained(config['vocab_path'])
	schema = load_schema(config['schema_path'])
	reversed_schema = dict((idx, q) for (q, idx) in schema.items())

	model.eval()

	while True:
		question = input('question: ')

		if question == 'exit':
			print('exit')
			break

		tokens = torch.LongTensor(tokenizer.encode(question)).unsqueeze(0)

		with torch.no_grad():
			pred = torch.argmax(model(tokens)).item()
		print(f'question: {reversed_schema[pred]}')

if __name__ == '__main__':
	main(Config)