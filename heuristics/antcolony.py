from heuristics.ant import Ant

import time
import random
import sys

class AntColony:
	def __init__(self, graph, num_ants, num_iterations, alpha, q0, rho, timeLimit, updateLambda = None):
		self.graph = graph
		self.num_ants = num_ants
		self.num_iterations = num_iterations
		self.timeLimit = timeLimit
		self.alpha = alpha
		self.q0 = q0
		self.rho = rho

		# condition var
		self.updateLambda = updateLambda

		self.reset()

	def reset(self):
		self.best_path_cost = sys.maxsize
		self.best_path_vec = None
		self.best_path_mat  = None
		self.last_best_path_iteration = 0

	def start(self):
		self.reset()
		self.startTime = time.time()
		endTime = self.startTime + self.timeLimit
		self.iter_counter = 0

		if self.updateLambda:
			self.updateLambda(0, self.best_path_cost, 1, 1, self.startTime)

		while self.iter_counter < self.num_iterations and time.time() < endTime:
			# print("iteration %d" % (self.iter_counter))
			self.iteration()

			self.global_updating_rule()

			if self.updateLambda:
				self.updateLambda(self.iter_counter, self.best_path_cost, 1, 1, self.startTime)

	# one iteration involves spawning a number of ant threads
	def iteration(self):
		self.avg_path_cost = 0
		self.ant_counter = 0
		self.iter_counter += 1
		self.ants = self.create_ants()
		# print("iter_counter = %d\n" % (self.iter_counter,))
		for ant in self.ants:
			# print("starting ant = %d\n" % (ant.ID))
			ant.run()

	def num_ants(self):
		return len(self.ants)

	def num_iterations(self):
		return self.num_iterations

	def iteration_counter(self):
		return self.iter_counter

	# called by individual ants
	def update(self, ant):
		#outfile = open("results.dat", "a")

		# print("Update called by %d, %d\n" % (ant.ID, self.ant_counter))
		self.ant_counter += 1

		self.avg_path_cost += ant.path_cost

		# book-keeping
		if ant.path_cost < self.best_path_cost:
			self.best_path_cost = ant.path_cost
			self.best_path_mat = ant.path_mat
			self.best_path_vec = ant.path_vec
			self.last_best_path_iteration = self.iter_counter

		if self.ant_counter == len(self.ants):
			self.avg_path_cost /= len(self.ants)
			# print("Best: %s, %f, %d, %f\n" % (self.best_path_vec, self.best_path_cost, self.iter_counter, self.avg_path_cost,))
			#outfile.write("\n%s\t%s\t%s" % (self.iter_counter, self.avg_path_cost, self.best_path_cost,))
		#outfile.close()

	def done(self):
		return self.iter_counter == self.num_iterations

	# assign each ant a random start-node
	def create_ants(self):
		ants = []
		for i in range(0, self.num_ants):
			ant = Ant(i, random.randint(0, self.graph.num_nodes - 1), self, self.q0, self.rho)
			ants.append(ant)
		
		return ants

	# changes the tau matrix based on evaporation/deposition 
	def global_updating_rule(self):
		evaporation = 0
		deposition = 0

		for r in range(0, self.graph.num_nodes):
			for s in range(0, self.graph.num_nodes):
				if r != s:
					delt_tau = self.best_path_mat[r][s] / self.best_path_cost
					evaporation = (1 - self.alpha) * self.graph.tau(r, s)
					deposition = self.alpha * delt_tau

					self.graph.update_tau(r, s, evaporation + deposition)
