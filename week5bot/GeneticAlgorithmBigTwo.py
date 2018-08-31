import copy
import random
import itertools
from FinalBigTwo import BigTwoBot
from Dealer import Dealer

class BotGenes:
  GENES = {'STRAIGHT_FLUSH': 32, 'FLUSH': 11, 'STRAIGHT': 28, 'QUAD': 44, 'FULL': 17, 'TRIPLE': 30, 'DOUBLE': 40, 'SINGLE': 37, 'CLOSE_WIN': 2, '5_CARD': 5, '3_CARD': 3, '2_CARD': 6, '1_CARD': 1}
  def __init__(self,genes):
    if genes == False:
      self.generateGenes()
    else:
      self.genes = genes
    self.winPercentage = 0
    self.cardPercentage = 0

  def generateGenes(self):
    self.genes = {
      'STRAIGHT_FLUSH':random.randint(0,52),
      'FLUSH':random.randint(0,52),
      'STRAIGHT':random.randint(0,52),
      'QUAD':random.randint(0,52),
      'FULL':random.randint(0,52),
      'TRIPLE':random.randint(0,52),
      'DOUBLE':random.randint(0,52),
      'SINGLE':random.randint(0,52),
      'CLOSE_WIN':random.randint(0,7),
      '5_CARD':random.randint(0,10),
      '3_CARD':random.randint(0,10),
      '2_CARD':random.randint(0,10),
      '1_CARD':random.randint(0,10),
    }

  def getFitness(self):
    return (self.winPercentage * 100)

class BotPopulation:
  def __init__(self,popCount,trainingGameCount):
    self.population = self.generatePopulation(popCount)
    self.trainingGameCount = trainingGameCount

  def generatePopulation(self,popCount):
    population = [BigTwoBot(botNum,BigTwoBot.winningStrategy,BotGenes(False)) for botNum in range(popCount)]
    return population

  def calculateFitness(self):
    players = [
    None,
    BigTwoBot(1,BigTwoBot.minPlayStrategy,BotGenes(BotGenes.GENES)),
    BigTwoBot(1,BigTwoBot.minPlayStrategy,BotGenes(BotGenes.GENES)),
    BigTwoBot(1,BigTwoBot.minPlayStrategy,BotGenes(BotGenes.GENES)),
    ]
    for currentBot in self.population:
      players[0] = currentBot
      wins,cardCounts = Dealer.testing(players,self.trainingGameCount,False)
      winPercentage = wins[0] / self.trainingGameCount
      cardPercentage =  (cardCounts[0] / self.trainingGameCount) / 13
      currentBot.botGenes.winPercentage = winPercentage
      currentBot.botGenes.cardPercentage = cardPercentage

  def reproduce(self,parent1,parent2):
    newGenes = {}
    for key in parent1.botGenes.genes:
      # val = (parent1.botGenes.genes[key] + parent2.botGenes.genes[key]) / 2
      val = [parent1.botGenes.genes[key],parent2.botGenes.genes[key]][random.randint(0,1)]
      newGenes[key] = val
    return BotGenes(newGenes)

  def selectParents(self):
    parents = []
    for index,bot in enumerate(self.population):
      count = int(bot.botGenes.getFitness())
      for i in range(count):
        parents.append(index)
    return parents

  def crossOver(self,parentPopulation):
    newGenes = []
    for i in range(len(self.population)):
      indexITERATION_THREE = random.randint(0,len(parentPopulation)-1)
      indexTwo = random.randint(0,len(parentPopulation)-1)
      parentITERATION_THREE = self.population[parentPopulation[indexITERATION_THREE]]
      parentTwo = self.population[parentPopulation[indexTwo]]
      newGene = self.reproduce(parentITERATION_THREE,parentTwo)
      newGenes.append(newGene)
    for i in range(len(self.population)):
      self.population[i].botGenes = newGenes[i]

  def findBest(self):
    return max(self.population,key=lambda bot:bot.botGenes.getFitness())

  def getAverageGene(self):
    genes = {}
    for key in self.population[0].botGenes.genes:
      total = 0
      for bot in self.population:
        total += bot.botGenes.genes[key]
      average = int(total / len(self.population))
      genes[key] = average
    return genes

  def trainPopulation(self,iterations):
    self.calculateFitness()
    maxWinPercentage = self.findBest().botGenes.winPercentage
    for i in range(iterations):
      print(self.getAverageGene())
      avgWinPercentage = (sum(bot.botGenes.winPercentage for bot in self.population) / len(self.population))
      print('avg-win-percentage:',avgWinPercentage,'max-win-percentage:',maxWinPercentage)
      parents = self.selectParents() #Select parent population for mating
      self.crossOver(parents) #Creates new genes from parents
      self.calculateFitness() #Calculates new fitness
      maxWinPercentage = self.findBest().botGenes.winPercentage
    return self.getAverageGene()

