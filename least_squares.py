import numpy as np

def adj(data):
	data = np.array(data)
	X = data[:,0:-1]
	y = data[:,-1].reshape(-1, 1)
	betaHat = np.linalg.solve(X.T.dot(X), X.T.dot(y))
	return betaHat