#!/usr/bin/env python

import sys
import glob
import os
import socket
import signal
import re


from nltk.model import NgramModel
from nltk.util import bigrams
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.probability import ConditionalFreqDist



class BigramDeamon():
	"""deamonized bigram"""
	def __init__(self, bigram, host, port):
		self.host = host
		self.port = port
		self.backlog = 10
		self.bigram = bigram
		self.pack_size = 1024
		
	def __del__(self):
		print("shutting down deamon...")
		self.sock.close()
		print("shuted down")

	def run(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		self.sock.bind((self.host, self.port))
		self.sock.listen(self.backlog)
		while True:
			client, address = self.sock.accept()
			data = client.recv(self.pack_size)
			if data:
				print(data.strip())
				resp = []
				for w,f in self.bigram.suggest(data.strip()).items():
					resp = resp + ["%s:%d" % (w,f)]
				client.send(' '.join(resp))
				client.close()




class Bigram():
	"""bigram model of given texts"""
	def __init__(self, dir_name):
		self.dir_name = dir_name
	
	def create_model(self):
		txt_file_list = glob.glob("%s/*.txt" % self.dir_name)
		total_txt = []
		for txt in txt_file_list:
			fn = open(txt)
			print("loading file: %s" % txt)
			txt_lines = [tl.lower().strip() for tl in fn.readlines()]
			# remove references
			ref_index = txt_lines.index("references")
			print("ref index is: %d" % ref_index)
			txt_lines = txt_lines[0:ref_index - 1]
			total_txt = total_txt + txt_lines

		# remove citations
		par_remove = re.compile(r'\([^)]*\)')
		full_txt = ' '.join(total_txt)
		full_txt = re.sub(par_remove, '', full_txt)
#		self.tokens = word_tokenize(full_txt)
		self.tokenizer = RegexpTokenizer(r'\w+')
		self.tokens = self.tokenizer.tokenize(full_txt)
		self.tokens_l = [t.lower() for t in self.tokens]
		self.bigrams = bigrams(self.tokens_l)
		self.cfd = ConditionalFreqDist(self.bigrams)
	
	
	def pdf2txt(self):
		pdf_file_list = glob.glob("%s/*.pdf" % self.dir_name)
		for pdf in pdf_file_list:
			txt_file = "%s.txt" % pdf[0:-4]
			try:
				open(txt_file)
			except IOError:
				pdf2txt_cmd = "java -jar ./lib/pdfbox-app-1.8.0.jar ExtractText \"%s\" \"%s\"" % (pdf, txt_file)
				os.system(pdf2txt_cmd)

	def suggest(self, word):
		return self.cfd[word.lower()]


def main():
	bigram = Bigram(sys.argv[1])
	bigram.pdf2txt()
	bigram.create_model()
	port = 1392
	host = 'localhost'
	bigramd = BigramDeamon(bigram, host, port)
	bigramd.run()


if __name__ == "__main__":
	main()
