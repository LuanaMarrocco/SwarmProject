import random
import numpy as np
import copy

class Ant(object):

	def __init__(self, ACS):
		self.ACS = ACS
		self.size = ACS.PFSPobj.getNumJobs()
		self.solutionSequence = [-1] * self.size
		self.isAlreadySelected = [False] * self.size
		self.selectionProb = [0] * self.size
		self.completionTimeMatrix = []
		self.completionTime = None
		self.tardiness = [0] * self.size
		self.totalWeihtedTardiness = 0
		random.seed(self.ACS.seed)
		np.random.seed(self.ACS.seed)

	def search(self):
		self.clearSolution()
		self.solutionSequence[0] = int(random.random()*self.size)
		self.isAlreadySelected[self.solutionSequence[0]] = True
		
		#Selection of the next job
		for i in range(1,self.size):
			self.solutionSequence[i] = self.getNextJobACS(i)
			self.isAlreadySelected[self.solutionSequence[i]] = True
		self.computeSolution()
		#print(self.solutionSequence)
	

		#Using the random proportional rule	
	def getNextJob(self, time):
		sumProb = 0.0
		for j in range (self.size):
			if(self.isAlreadySelected[j] == False):
				sumProb += self.ACS.probability[j][time]
			else:
				self.selectionProb[j] = 0.0
		if (sumProb == 0):
			nextJob = self.getRandomWithoutP()
		else: 
			for j in range(self.size):
				if(self.isAlreadySelected[j] == False):
					self.selectionProb[j] = self.ACS.probability[j][time]/sumProb 
			nextJob = np.random.choice(self.size, p=self.selectionProb)
		return nextJob
	
	def getRandomWithoutP(self):
		listChoices = []
		for i in range (self.size):
			if(self.isAlreadySelected[i] ==  False):
				listChoices.append(i)
		return np.random.choice(listChoices)

	#Using the state transition rule
	def getNextJobACS(self,time):
		q = random.random()
		nextJob = -1
		if (q <= self.ACS.q0):
			maxVal = 0
			for i in range(self.size):
				if(self.isAlreadySelected[i] == False):
					val = self.ACS.pheromone[i][time]*(self.ACS.heuristic[i][time]**self.ACS.beta)
					if(val > maxVal):
						nextJob = i
						maxVal = val
		else:
			nextJob = self.getNextJob(time)
		self.localUpdatePheromone(nextJob,time)
		return nextJob

	def localUpdatePheromone(self, i, j):
		self.ACS.pheromone[i][j] = ((1-self.ACS.rho) * self.ACS.pheromone[i][j] + self.ACS.rho * self.ACS.initial_pheromone)

	def computeSolution(self):
		self.computeCompletionTimeMatrix()
		self.computeTardinessList()
		self.computeTotelWeightedTardiness()

	def computeTardinessList(self):
		dueDates = self.ACS.PFSPobj.getDueDates()
		for i in range(self.size):
			valTardi = self.completionTime[i] - dueDates[self.solutionSequence[i]]
			tardi = max(0, valTardi)
			self.tardiness[i] = tardi

	def computeTotelWeightedTardiness(self):
		tot = 0
		weights = self.ACS.PFSPobj.getWeights()
		for i in range(self.size):
			tot = tot + self.tardiness[i]*weights[self.solutionSequence[i]]
		self.totalWeihtedTardiness = tot

	def computeCompletionTimeMatrix(self):
		M = self.ACS.PFSPobj.getM()
		processingTimes = self.ACS.PFSPobj.getProcessingTime()
		for i in range (M):
			completionTimePerMachine = []
			if (i==0):
				time = processingTimes[self.solutionSequence[0]][i*2+1]
				completionTimePerMachine.append(time)
				for j in range(1,self.size):
					time = time + processingTimes[self.solutionSequence[j]][i*2+1]
					completionTimePerMachine.append(time)
			else:
				for j in range(self.size):
					if(j==0):
						time = self.completionTimeMatrix[i-1][j]+processingTimes[self.solutionSequence[j]][i*2+1]
						completionTimePerMachine.append(time)
					else:
						maxVal = max(self.completionTimeMatrix[i-1][j],completionTimePerMachine[-1])
						time = maxVal + processingTimes[self.solutionSequence[j]][i*2+1]
						completionTimePerMachine.append(time)

			self.completionTimeMatrix.append(completionTimePerMachine)
		self.completionTime = self.completionTimeMatrix[-1]

	def SLS(self):
		previousSol = -1
		while(previousSol != self.totalWeihtedTardiness):
			previousSol = self.totalWeihtedTardiness
			indexJobToMove = np.random.choice(self.size)
			self.moveJob(indexJobToMove)

	def moveJob(self, index):
		#Storage of the previous solution
		previousSol = copy.copy(self.solutionSequence)
		previousTardi = self.totalWeihtedTardiness
		
		#Perumation and calculation of the new sol
		previousIndex = np.random.choice(self.size)#previousIndex = (index - 1)%self.size
		while(index == previousIndex):
			previousIndex = np.random.choice(self.size)

		previousJob = self.solutionSequence[previousIndex]
		job = self.solutionSequence[index]
		self.solutionSequence[index] = previousJob
		self.solutionSequence[previousIndex] = job
		self.computeSolution()
		#Keeping the best
		if(previousTardi < self.totalWeihtedTardiness):
			self.solutionSequence = copy.copy(previousSol)
			self.totalWeihtedTardiness = previousTardi
		

	def getJob(self,i):
		return self.solutionSequence[i]

	def getWeightedTardiness(self):
		return self.totalWeihtedTardiness

	def getSolution(self):
		return self.solutionSequence

	def clearSolution(self):
		self.solutionSequence = [-1] * self.size
		self.isAlreadySelected = [False] * self.size
		self.selectionProb = [0] * self.size
		self.completionTimeMatrix = []
		self.completionTime = None
		self.tardiness = [0] * self.size
		self.totalWeihtedTardiness = 0