from corpora import CorporaCreator
from helpers.classification import Classification
from helpers import Configuration

import tempfile, subprocess, sys

class Classifier:
	def __init__(self, corpus_symbols = None):
		self.corpora_creator = CorporaCreator(corpus_symbols)
		self.corpora = None
	
	def __getstate__(self):
		return self.corpora
	
	def __setstate__(self, state):
		self.corpora = state
	
	def train(self, data_reader):
		print 'Creating corpus...'
		for data, classification in data_reader:
			self.corpora_creator.feed_data(data, classification)
		
		self.corpora = self.corpora_creator.get_corpora()
		print '   DONE!'
		
		print 'Creating train data file...'
		train_data = open(Configuration.ModelDirectory+'/train-data.dat', 'w') 
		#train_data = tempfile.NamedTemporaryFile()
		
		for data, classification in data_reader:
			features = self.corpora.get_features_for_data(data)
			
			train_data.write(str(classification.to_int()))
			for i in range(len(features)):
				if features[i] != 0:
					train_data.write(' '+str(i+1)+':'+str(features[i]))
			train_data.write("\n")
		
		train_data.flush()
		train_data.close()
		print '   DONE!'
		
		print 'Scaling values...'
		scaled_data = open('train-data-scaled.dat', 'w')
		subprocess.check_call(['svm-scale', '-l', '0', '-s', Configuration.ModelDirectory+'/scale.params', train_data.name],
			stdout=scaled_data)
		scaled_data.flush()
		print '   DONE!'
		
		print 'Training...'
		result = subprocess.check_call(['svm-train', scaled_data.name, Configuration.ModelDirectory+'/train-results.dat'])
		print '   DONE!'
	
	def classify(self, data_reader):
		print 'Creating prediction data file...'
		classification_data = open('classification-data.dat', 'w')
		#classification_data = tempfile.NamedTemporaryFile()
		#classification_data.write(str(len(data_set)) + "\n")
		
		j = 1
		for x in data_reader:
			data = x[1]
			
			features = self.corpora.get_features_for_data(data)
			classification_data.write(str(j) + ' ')
			for i in range(len(features)):
				if features[i] != 0:
					value = str(i+1)+':'+str(features[i])+' '
					classification_data.write(value)
			classification_data.write("\n")
			j += 1
		
		classification_data.flush()
		classification_data.close()
		print '   DONE!'

		print 'Scaling values...'
		scaled_data = open('classification-data-scaled.dat', 'w')
		subprocess.check_call(['svm-scale', '-l', '0', '-r', Configuration.ModelDirectory+'/scale.params', classification_data.name],
			stdout=scaled_data)
		scaled_data.flush()
		print '   DONE!'

		print 'Predicting...'
		result_file = open('result.dat', 'w+')
		subprocess.check_call(['svm-predict', scaled_data.name, Configuration.ModelDirectory+'/train-results.dat', result_file.name])
		print '   DONE!'

		results = map(int, result_file.readlines())
		return [Classification.from_int(cls) for cls in results]
		
