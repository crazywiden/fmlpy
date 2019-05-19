import pandas as pd 
import numpy as np 

def _occurance_matrix(label_start,label_end):
	"""
	generate a matrix shows which bar used info of data at which time
	e.g.
	>>> label_start = [2,3,5]
	>>> label_end = [6,7,12]
	>>> _occurance_matrix(label_start, label_end)
	[
	[0,0,1,1,1,1,1,0,0,0,0,0,0],
	[0,0,0,1,1,1,1,1,0,0,0,0,0],
	[0,0,0,0,0,1,1,1,1,1,1,1,1]
	]

	@parameters:
	label_start -- 1d vector
	label_end -- 1d vector
		note that label_start[i] < label_end[i] for all i
	@returns:
	occ_matrix -- m by n matrix
		m is number of bars (len(label_start))
		n is maximum time length (max(label_end))
	"""
	pass

def seq_bootstrap(occ_matrix, n_classifier=1, n_sample=None, verbose=True):
	"""
	implement sequential bootstrap algorithm
	@parameters:
	occ_matrix -- m by n matrix
		output of _occurance_matrix()
	n_classifier -- int
		how many weak classifiers needed to be trained
	n_sample -- int
		number of samples that need to draw
		default should be number of bars, i.e. occ_matrix.shape[0]
	verbose -- boolean
		whether print time eclapse for each round
		default is True
	@returns:
	sample_idx -- m by n matrix
		m is number of classifiers
		n is number of samples
	"""
	pass