import random
import copy
import itertools

class Dealer:
  RANK_ORDER = '34567890JQKA2'
  SUIT_ORDER = 'DCHS'
  RANK_IMPORTANCE = dict(zip(RANK_ORDER,range(len(RANK_ORDER))))
  SUIT_IMPORTANCE = dict(zip(SUIT_ORDER,range(len(SUIT_ORDER))))
  CARDS = {value + suit for value in '34567890JQKA2' for suit in 'DCHS'}
  def __init__(self,playerCount,players):
    self.playerCount = playerCount
    self.players = players
    self.setupGame()

  def setupGame(self):
    cards = copy.deepcopy(Dealer.CARDS)
    for player in self.players:
      player.cards = []
      player.roundWinningCards = []
      self.dealCards(player,cards)
    
  def dealCards(self,player,cards,playing=False):
    assert(len(Dealer.CARDS) % self.playerCount == 0)
    cardCount = int(len(Dealer.CARDS) / self.playerCount)
    for i in range(cardCount):
      randomCard = random.sample(cards,1)[0]
      cards.remove(randomCard)
      player.cards.append(randomCard)

  def startRound(self,roundNo,roundHistory,roundStarter,playing=False):
    current_round_history = []
    roundHistory.append(current_round_history)
    playToBeat = []
    foundRoundStarter = False
    lasyPlayerNo = -1
    while(True):
      for playerNo,player in enumerate(self.players):
        #Located First Player
        if foundRoundStarter == False:
          if ((playerNo == roundStarter) or (roundStarter == -1 and '3D' in player.cards)):
            foundRoundStarter = True
          else:
            continue
        #Make Play
        if playerNo == lasyPlayerNo:
          return playerNo
        else:
          currentPlay = player.strategy(player,player.cards, True, playToBeat, roundHistory, playerNo, self.getCardCount(), self.dummyScores(), roundNo)
          assert(Dealer.validPlay(player.cards,currentPlay,playToBeat) == True)
          if len(currentPlay) > 0:
            playToBeat = currentPlay
            lasyPlayerNo = playerNo
            Dealer.removePlayedCards(currentPlay,player.cards)
          current_round_history.append((playerNo,currentPlay))
        #Misc
        if self.win(): return playerNo
        if playing == True: 
          if len(currentPlay) == 0:
            print("player " + str(playerNo) + " has passed")
          else:
            print("player " + str(playerNo) + " played " + ' '.join(currentPlay))
          print("player " + str(playerNo) + " cards:",' '.join(sorted(player.cards,key=Dealer.cardValue)))

  def win(self):
    return any((len(player.cards) == 0) for player in self.players)

  def getCardCount(self):
    return [len(player.cards) for player in self.players]

  def dummyScores(self):
    return [None for i in range(len(self.players))]
  
  @staticmethod
  def removePlayedCards(currentPlay,cards):
    for card in currentPlay:
      cards.remove(card)
    return cards

  @staticmethod
  def sortCards(cards):
    return sorted(cards,key=lambda x:Dealer.cardValue(x))

  @staticmethod
  def sortCombinations(combinations):
    return sorted(combinations,key=Dealer.combinationSum)

  @staticmethod
  def cardValue(card):
    value = card[0]
    suit = card[1]
    totalCost = 4 * (Dealer.RANK_IMPORTANCE[value]) + (Dealer.SUIT_IMPORTANCE[suit])
    return totalCost

  @staticmethod
  def combinationSum(combination):
    return sum(Dealer.cardValue(combination[cardNum]) for cardNum in range(len(combination)))

  @staticmethod
  def cardCombinations(hand,combinationSize):
    sameValue = Dealer.rankCardDict(hand)
    combos = []
    for value in sameValue:
      cards = sameValue[value]
      pairs = [list(pair) for pair in itertools.combinations(cards,combinationSize)]
      combos += pairs
    return combos

  @staticmethod
  def rankCardDict(cards):
    sameRankedCards = {}
    for card in cards:
      rank = card[0]
      if rank in sameRankedCards: sameRankedCards[rank].append(card)
      else: sameRankedCards[rank] = [card]
    return sameRankedCards

  @staticmethod
  def checkHigherCombination(combination1, combination2):
    valueType1 = combination1[0][0]
    valueType2 = combination2[0][0]
    firstMaxSuitVal = max(Dealer.SUIT_IMPORTANCE[card[1]] for card in combination1)
    secondMaxSuitVal = max(Dealer.SUIT_IMPORTANCE[card[1]] for card in combination2)
    if Dealer.RANK_IMPORTANCE[valueType1] > Dealer.RANK_IMPORTANCE[valueType2]: return True
    elif Dealer.RANK_IMPORTANCE[valueType2] > Dealer.RANK_IMPORTANCE[valueType1]: return False
    elif firstMaxSuitVal > secondMaxSuitVal: return True
    else: return False
      
  @staticmethod
  def validCombination(combination):
    sameRank = set(card[0] for card in combination)
    return len(sameRank) == 1

  @staticmethod
  def validPlay(hand,play,playToBeat):
    if all(card in hand for card in play) == False: 
      return False
    elif len(play) == 0: return True
    elif len(playToBeat) == 0:
      if len(play) in {1,2,3,4}: 
        return Dealer.validCombination(play)
      else: #Special Hand
        pass
    elif len(playToBeat) == len(play):
      if len(play) in {1,2,3,4}:
        if Dealer.validCombination(play):
          return Dealer.checkHigherCombination(play,playToBeat)
        else: 
          return False
      else: #Special Hand
        pass
    else: 
      return False

  @staticmethod
  def getRemainingCards(roundHistory):
    played = set()
    for currentRound in roundHistory:
      for play in currentRound:
        hand = play[1]
        for card in hand:
          played.add(card)
    return Dealer.CARDS - played

  @staticmethod
  def minPlay(combinations,playToBeat):
    sortedCombinations = Dealer.sortCombinations(combinations)
    for combination in sortedCombinations:
      if Dealer.checkHigherCombination(combination,playToBeat): return combination
    else: return []

  @staticmethod
  def removeCombinationCards(combinations,cards):
    for combination in combinations:
      for card in combination:
        if card in cards:
          cards.remove(card)

  @staticmethod
  def getOptimalCombinations(hand):
    optimalCombinations = {}
    cards = set(hand)
    optimalCombinations[3] = Dealer.cardCombinations(list(cards),3)
    Dealer.removeCombinationCards(optimalCombinations[3],cards)
    optimalCombinations[2] = Dealer.cardCombinations(list(cards),2)
    Dealer.removeCombinationCards(optimalCombinations[2],cards)
    optimalCombinations[1] = Dealer.cardCombinations(list(cards),1)
    Dealer.removeCombinationCards(optimalCombinations[1],cards)
    return optimalCombinations

  @staticmethod
  def findWinningChance(combination,unplayed,combinationSize,hand):
    availableCards = unplayed - set(hand)
    availableCards |= set(combination)
    availableCombinations = list(tuple(sorted(combo)) for combo in Dealer.cardCombinations(availableCards,combinationSize))
    sortedCombinations = Dealer.sortCombinations(availableCombinations)
    combinationRanks = dict(zip(sortedCombinations,range(1,len(sortedCombinations)+1)))
    currentRank = combinationRanks[tuple(sorted(combination))]
    percentile = currentRank / len(combinationRanks)
    return percentile

  @staticmethod
  def find3DiamondCombination(optimalCombinations):
    for size in optimalCombinations:
      for combination in optimalCombinations[size]:
        if '3D' in combination:
          return combination
    else:
      return []

  @staticmethod
  def firstRoundPlay(optimalCombinations,unplayed,hand):
    minWinningChance = 1.01
    combination = []
    for size in optimalCombinations:
      combinationSize = size
      sortedCombinations = Dealer.sortCombinations(optimalCombinations[size])
      if len(sortedCombinations) > 0:
        currentChance = Dealer.findWinningChance(sortedCombinations[0],unplayed,combinationSize,hand)
        if currentChance < minWinningChance:
          minWinningChance = currentChance
          combination = sortedCombinations[0]
    return combination

  @staticmethod
  def closeWinnerCheck(playerNo,handSizes):
    for num in range(len(handSizes)):
      if num != playerNo:
        if handSizes[num] <= 5:
          return True
    else:
      return False

  @staticmethod
  def playGame(game,playing):
    round_no = 0
    round_history = []
    round_starter = -1
    while(game.win() != True):
      round_starter = game.startRound(round_no,round_history,round_starter,playing)
      round_no += 1
    for player_no,player in enumerate(game.players):
      if len(player.cards) == 0:
        return player_no
    else:
      return False

  @staticmethod  
  def testing(players,gameCount):
    playerCount = len(players)
    game = Dealer(playerCount,players)
    wins = [0 for i in range(playerCount)]
    playing = False

    for gameNo in range(gameCount):
      winner = Dealer.playGame(game,playing)
      if playing: print("player " + str(winner) + " has won game number " + str(gameNo))
      wins[winner] += 1
      game.setupGame()
    return wins

class BigTwoBot:
  def __init__(self,num,strategy,botGenes):
    self.num = num
    self.strategy = strategy
    self.numImportance = Dealer.RANK_IMPORTANCE
    self.suitImportance = Dealer.SUIT_IMPORTANCE
    self.cards = []
    self.botGenes = botGenes
  
  def playerStrategy(self,hand, isStartOfRound, playToBeat, roundHistory, playerNo, handSizes, scores, roundNo):
    print()
    print("Current hand: " + ' '.join(Dealer.sortCards(hand)))
    print("Play to beat: " + ' '.join(playToBeat))
    print("Current hand sizes: " + str(handSizes))
    print("Type 'PASS' to pass turn.")
    play = []
    while(True):
      line = input("Play a hand: ")
      play = line.split()
      if line == "PASS": return []
      elif Dealer.validPlay(hand,play,playToBeat): 
        print()
        return play
  
  def minPlayStrategy(self,hand, isStartOfRound, playToBeat, roundHistory, playerNo, handSizes, scores, roundNo):
    sortedHand = Dealer.sortCards(hand)
    if len(playToBeat) == 0: #Play whatever
      if '3D' in hand:
        return ['3D']
      else:
        return [sortedHand[0]]
    else:
      combinations = Dealer.cardCombinations(hand,len(playToBeat))
      play = Dealer.minPlay(combinations,playToBeat)
      return play

  def winPercentageStrategy(self,hand, isStartOfRound, playToBeat, roundHistory, playerNo, handSizes, scores, roundNo):
    unplayed = Dealer.getRemainingCards(roundHistory)
    optimalCombinations = Dealer.getOptimalCombinations(hand)
    if len(playToBeat) == 0:
      if '3D' in hand: 
        return Dealer.find3DiamondCombination(optimalCombinations)
      else: 
        return Dealer.firstRoundPlay(optimalCombinations,unplayed,hand)
    else:
      closeWinnerCheck = Dealer.closeWinnerCheck(playerNo,handSizes)
      if closeWinnerCheck: #Remaining players have few cards left
        combinations = Dealer.cardCombinations(hand,len(playToBeat))
        play = Dealer.minPlay(combinations,playToBeat)
        return play
      else:
        combinationSize = len(playToBeat)
        availableOptimalCombinations = optimalCombinations[combinationSize]
        selectedCombination = Dealer.minPlay(availableOptimalCombinations,playToBeat)
        if len(selectedCombination) == 0: #No optimal play
          return []
        else: #Available optimal play
          winningChance = Dealer.findWinningChance(selectedCombination,unplayed,combinationSize,hand)
          if winningChance >= self.botGenes.botGenes['highWin']:
            return selectedCombination
          elif winningChance <= self.botGenes.botGenes['lowWin']:
            return selectedCombination
          else:
            return []

class BotPopulation:
  def __init__(self,popCount,trainingGameCount):
    self.population = self.generatePopulation(popCount)
    self.trainingGameCount = trainingGameCount

  def generatePopulation(self,popCount):
    population = [BigTwoBot(botNum,BigTwoBot.winPercentageStrategy,BotGenes()) for botNum in range(popCount)]
    return population

  def calculateFitness(self):
    players = [
    None,
    BigTwoBot(1,BigTwoBot.minPlayStrategy,None),
    BigTwoBot(2,BigTwoBot.minPlayStrategy,None),
    BigTwoBot(3,BigTwoBot.minPlayStrategy,None),
    ]
    for currentBot in self.population:
      players[0] = currentBot
      wins = Dealer.testing(players,self.trainingGameCount)
      winPercentage = wins[0] / self.trainingGameCount
      currentBot.botGenes.winPercentage = winPercentage
      currentBot.botGenes.updateFitness()
  @staticmethod
  def reproduce(parent1,parent2):
    #combine genes of both parents
    genes = {}
    genes['highWin'] = (parent1.botGenes['highWin'] + parent2.botGenes['highWin']) / 2
    genes['lowWin'] = (parent1.botGenes['lowWin'] + parent2.botGenes['lowWin']) / 2
    return BotGenes(genes)

  def selectParents(self):
    parents = []
    for index,bot in enumerate(self.population):
      count = int(bot.botGenes.fitness)
      for i in range(count):
        parents.append(index)
    return parents

  def crossOver(self,parentPopulation):
    newGenes = []
    for i in range(len(self.population)):
      indexOne = int(random.random() * len(parentPopulation))
      indexTwo = int(random.random() * len(parentPopulation))
      parentOne = self.population[parentPopulation[indexOne]].botGenes
      parentTwo = self.population[parentPopulation[indexTwo]].botGenes
      newGene = BotPopulation.reproduce(parentOne,parentTwo)
      newGenes.append(newGene)
    for i in range(len(self.population)):
      self.population[i].botGenes = newGenes[i]

  def mutation(self):
    for bot in self.population:
      if random.random() < 0.1:
        genes = bot.botGenes.botGenes
        for key in genes:
          genes[key] += 0.05 * (1 - 2 * random.random())

  def findBest(self):
    return max(self.population,key=lambda bot:bot.botGenes.winPercentage)

  def trainPopulation(self,goalWinPercentage):
    self.calculateFitness()
    maxWinPercentage = self.findBest().botGenes.winPercentage
    # while(maxWinPercentage < goalWinPercentage):
    for i in range(20):
      avgWinPercentage = (sum(bot.botGenes.winPercentage for bot in self.population) / len(self.population))
      print(avgWinPercentage,maxWinPercentage)
      parents = self.selectParents() #Select parent population for mating
      self.crossOver(parents) #Creates new genes from parents
      self.mutation() #Mutates Genes
      self.calculateFitness() #Calculates new fitness
      maxWinPercentage = self.findBest().botGenes.winPercentage
    return self.findBest().botGenes

class BotGenes:
  def __init__(self,botGenes=False):
    if botGenes == False: self.botGenes = self.generateGenes()
    else: self.botGenes = botGenes
    self.winPercentage = 0
    self.fitness = 0

  def generateGenes(self):
    return {'highWin':0.95,'lowWin':0.8}

  def updateFitness(self):
    self.fitness = ((self.winPercentage)*5 + 1) ** 2

pop = BotPopulation(40,10)
best = pop.trainPopulation(0)
print(best.botGenes)