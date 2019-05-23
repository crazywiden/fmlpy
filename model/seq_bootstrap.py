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
	matrix = np.zeros(shape=(len(label_start), label_end[-1]))
	i = 0
	for s, e in zip(label_start, label_end):
		matrix[i, s:e] = 1
		i += 1
	return matrix


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

	result = []
	for i in range(n_classifier):
		first = np.random.randint(0, len(occ_matrix))
		benchmark = occ_matrix[first]
		sample = [first]

		for j in range(n_sample):
			overlap_prob = []

			for k in range(len(occ_matrix)):
				overlap = np.sum([1/(1+a+b) for a,b in zip(occ_matrix[k], benchmark)])
				overlap_prob.append(overlap)
			overlap_prob = overlap_prob / np.sum(overlap_prob)
			choice = np.random.choice(range(len(occ_matrix)), prob=overlap_prob)
			sample.append(choice)
			benchmark += occ_matrix[benchmark]

		result.append(sample)
	return result