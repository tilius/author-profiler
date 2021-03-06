#!/usr/bin/env python

import argparse

parser = argparse.ArgumentParser(description='Creates model for author profiling using given corpus.')
parser.add_argument('-i', metavar='corpus_dir', required=True, help='path to dir containing *.xml files')
parser.add_argument('-m', metavar='model_dir', required=True, help='path to dir containg model files')
parser.add_argument('-o', metavar='output_dir', required=True, help='path to dir where results will be saved')
parser.add_argument('--truth', metavar='truth_file', help='path to the truth file')
parser.add_argument('--accuracy', metavar='accuracy_output_file', help='path to the output accuracy file')
args = parser.parse_args()

from helpers import Configuration
Configuration.CorpusDirectory = args.i
Configuration.ModelDirectory = args.m
Configuration.OutputDirectory = args.o

from helpers.reader import ClassifyDataReader
from helpers.writer import PredictionWriter

import pickle
import sys

file = open(Configuration.ModelDirectory + '/classifier.dat', 'r')
classifier = pickle.load(file)
file.close()

reader = ClassifyDataReader(Configuration.CorpusDirectory + '/*.xml')
predictions = classifier.classify(reader, args.truth, args.accuracy)

for authorspec, cls in predictions:
	PredictionWriter.output_prediction(Configuration.OutputDirectory, authorspec, cls)

