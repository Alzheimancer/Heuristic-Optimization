from __future__ import division
import os
import sys
import csv
import random
import numpy as np
from deap import tools
from operator import itemgetter

COV_CSV = None
RET_CSV = None
UPDATE_H = 0
DONT_UPDATE_H = 1
FINAL_SAMPLE = 2

epsilon = []
delta = []
number_of_lambdas = 2001														#number of lambda values we wish to examine
number_of_assets = 98																#given assets
population_size = 4*number_of_assets												#population size 
population = [[[0,0] for x in range(number_of_assets)] for x in range(population_size)]			#population
population_obj_func_vals = [0 for x in range(population_size)]						#objective function values
iterations = 500																	#number of iterations
H = []																				#all improved solutions for different lambdas
ind_prob = 0.5																		#Independent probability for each attribute to be exchanged
K = 10																				#constraint on number of assets


def myRandom(a, b):
    candidate = random.uniform(a, b + sys.float_info.epsilon)
    while candidate > b:
       candidate = random.uniform(a, b + sys.float_info.epsilon)
    return candidate

def getEpDel(fileName, epsilon, delta):
	with open(fileName,"r") as f:
		for line in f:
			line = line.strip()
			tok = line.split()
			if(len(tok)==1):
				n = int(line)
				for i in range(0, n):
					epsilon.append(0.001)
					delta.append(1)
				return

def readCovCSV(fileName):
	cov = []
	with open(fileName,'r') as csvfile:
		freader = csv.reader(csvfile, delimiter=',')
		for row in freader:
			cov.append(map(float, row[:-1]))
	return cov

def readReturns(fileName):
	returns = []
	with open(fileName,'r') as csvfile:
		freader = csv.reader(csvfile, delimiter=',')
		for row in freader:
			returns.append(map(float, row[:])[0])
	return returns

def evaluateF(K, w, cov, returns, lda):

	risk = 0
	_return = 0

	for i in range(0,len(K)):
		for j in range(i,len(K)):
			risk += cov[K[i]][K[j]]*w[i]*w[j]
		_return += returns[K[i]]*w[i]

	f = lda*risk-(1-lda)*_return

	return [f, risk, _return]

def evaluate(SET, lda, f, V_lda, improved, H, flag):
	global epsilon
	global delta
	global COV_CSV
	global RET_CSV
	global DONT_UPDATE_H

	improved = False
	S = []
	si = []

	for i in range(0,len(SET)):
		if(SET[i][0]==1):
			S.append(i)
			si.append(SET[i][1])



	f = float("inf")
	checkL = 0
	checkU = 0
	for i in range(0, len(S)):
		checkL += epsilon[S[i]]
		checkU += delta[S[i]]

	if(checkL>1 or checkU<1):
		print("Not feasible")
		return

	L = 0
	for i in range(0, len(si)):
		L += si[i]

	F = 1 - checkL

	w = [0]*len(SET)

	for i in range(0, len(S)):
		w[S[i]] = epsilon[S[i]] + (si[i]*F)/L

	R = set()
	Q = []
	for i in range(0,len(S)):
		Q.append(S[i])

	Q = set(Q)

	Q_R = list(Q.difference(R))

	for x in Q_R:
		if(w[x]>delta[x]):
			R = R.union(set([x]))

	Q_R = list(Q.difference(R))

	L = 0
	F = 0
	ff = 0

	for i in Q_R:
		L += SET[i][1]
		ff += epsilon[i]

	for i in R:
		F += delta[i]

	F = 1 - (ff + F)

	for i in Q_R:
		w[i] = epsilon[i] + (SET[i][1]*F)/L

	for i in R:
		w[i] = delta[i]


	K = S
	evW = []
	for i in S:
		evW.append(w[i])

	temp = evaluateF(K, evW, COV_CSV, RET_CSV, lda)
	f = temp[0]
	risk = temp[1]
	ret = temp[2]

	for i in Q:
		SET[i][1] = w[i]-epsilon[i]

	if(flag == FINAL_SAMPLE):
		return w + [ret, risk, f]

	if(flag == DONT_UPDATE_H):
		return [f, V_lda, improved]
	
	if(f<V_lda):
		improved = True
		V_lda = f
		H.append(SET)

	return [f, V_lda, improved]

def main(epsilon, delta):
	global lambda_values
	global population_size
	global population
	global population_obj_func_vals
	global iterations

	outputs = []

	for lambda_index in range(1, number_of_lambdas+1):
		_lambda = float(lambda_index-1)/(number_of_lambdas-1)

		improved_solutions = []							#improved solutions for a particular lambda
		v_lambda = float('Inf')

		for i in range(1 , population_size+1):
			sample = [[0,0] for x in range(number_of_assets)]
			Q = random.sample([x for x in range(1, number_of_assets+1)],10)

			for asset in Q:
				sample[asset-1] = [1, myRandom(0,1)]
			
			population[i-1] = list(sample)

		for ind,S in enumerate(population):
			[population_obj_func_vals[ind], v_lambda, improved] = evaluate(S, _lambda, 0, v_lambda, False, improved_solutions, UPDATE_H)

		for itr in range(iterations):
			#binary tournament for selecting parents S_star and S_double_star
			chosen = []
			for i in xrange(2):
				aspirants = tools.selRandom(population, 40)
				for i,aspirant in enumerate(aspirants):
					h = []
					f_aspirant = 0
					v = float('Inf')
					imp = False
					[f_aspirant, v, imp] = evaluate(aspirant, _lambda, 0, v, False, h, DONT_UPDATE_H)
					aspirants[i] = [aspirant, f_aspirant]
					
				chosen.append(min(aspirants, key=lambda x: x[1])[0])
			
			S_star = list(chosen[0])
			S_double_star = list(chosen[1])
			
			#Uniform crossover to find child C
			C = []
			[C1, C2] = tools.cxUniform(S_star, S_double_star, ind_prob)
			f1 = f2 = 0
			v = float('Inf')
			imp = False
			h = []
			[f1, v, imp] = evaluate(C1, _lambda, 0, v, False, h, DONT_UPDATE_H)
			[f2, v, imp] = evaluate(C2, _lambda, 0, v, False, h, DONT_UPDATE_H)

			if f1<f2:
				C = C1
			else:
				C = C2

			#find assets in parents but not in child
			A_star = []
			for i in range(number_of_assets):
				if S_star[i][0]==1 and S_double_star[i][0]==0 and C[i][0]==0:
					A_star.append([i+1, S_star[i][1]])
				elif S_star[i][0]==0 and S_double_star[i][0]==1 and C[i][0]==0:
					A_star.append([i+1, S_double_star[i][1]])

			#Mutation
			mutation_index = random.randint(0, number_of_assets-1)
			while C[mutation_index][0]==0:
				mutation_index = random.randint(0, number_of_assets-1)
			m = random.randint(0,1)

			if m == 0:
				# C_i = 0.9*(epsilon + C[mutation_index][1]) - epsilon
				C_i = 0.9*(epsilon[mutation_index] + C[mutation_index][1]) - epsilon[mutation_index]
			else:
				# C_i = 1.1*(epsilon + C[mutation_index][1]) - epsilon
				C_i = 1.1*(epsilon[mutation_index] + C[mutation_index][1]) - epsilon[mutation_index]

			if C_i<0:
				C[mutation_index][0] = 0
				C[mutation_index][1] = 0

			#check if child contains more or less than K assets and fix it
			total_assets_in_child = 0
			child_copy = list(C)
			sorted_child_copy = sorted(child_copy, key=itemgetter(1))
			
			for item in sorted_child_copy:
				if item[0]==1:
					total_assets_in_child += 1
			if total_assets_in_child > K:
				for item in sorted_child_copy[:-K]:
					# C.index(item) = [0,0]
					C[C.index(item)] = [0,0]
			elif total_assets_in_child < K:
				while total_assets_in_child < K:
					if len(A_star) > 0:
						random_index = random.randint(0,len(A_star)-1)
						random_element = A_star.pop(random_index)
						C[random_element[0]-1] = [1, random_element[1]]
					else:
						random_index = random.randint(0,30)
						while C[random_index][0]==1:
							random_index = random.randint(0,30)
						C[random_index] = [1, 0]
					total_assets_in_child += 1
					
			#change the population by adding child to it
			obj_func_val_child = 0
			[obj_func_val_child, v_lambda, improved] = evaluate(C, _lambda, 0, v_lambda, False, improved_solutions, UPDATE_H)
			
			if improved:
				population[population_obj_func_vals.index(max(population_obj_func_vals))] = C
		
		print lambda_index

		outputs.append(evaluate(improved_solutions[-1], _lambda, 0, float('Inf'), False, None, FINAL_SAMPLE))

		H.append(improved_solutions)

	np_out_matrix = np.matrix(outputs)
	np_out_matrix = np_out_matrix.T
	outputs = np_out_matrix.tolist()

	f = open("out4.csv", "w")
	writer = csv.writer(f)
	for row in outputs:
		writer.writerow(tuple(row))
	f.close()

if __name__=="__main__":
	global epsilon
	global delta
	global COV_CSV
	global RET_CSV

	if(len(sys.argv)<4):
		print "Usage: python GA_algo.py <<port(i).txt>> <<covariance_matrix.csv>> <<returns.csv>>"
		exit(1)

	COV_CSV = readCovCSV(str(sys.argv[2]))
	RET_CSV = readReturns(str(sys.argv[3]))
	
	getEpDel(str(sys.argv[1]), epsilon, delta)

	main(epsilon, delta)