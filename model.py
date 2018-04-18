import numpy as np

def process_game_line(line):
	#change Field Goals to Two Pointers to avoid counting Three Pointers twice
	for i in xrange(2):
		line[i] = line[i] - line[i+3]
	#change TRB to DRB
	line[10] = line[10] - line[9]
	#remove shooting percentages
	for i in xrange(1,4):
		del line[2*i]
	return line

def model(team_stats, opp_stats):
	line = [t-o for t,o in zip(team_stats,opp_stats)]
	#square all shooting stats
	#for i in xrange(6):
	#	line[i] = line[i]**2
	return line

def least_squares(data):
	data = np.array(data)
	X = data[:,0:-1]
	y = data[:,-1].reshape(-1, 1)
	betaHat = np.linalg.solve(X.T.dot(X), X.T.dot(y))
	return betaHat