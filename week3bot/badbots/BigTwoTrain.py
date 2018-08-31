import copy
import random
import itertools

def play(hand, isStartOfRound, playToBeat, roundHistory, playerNo, handSizes, scores, roundNo):
  bot = BigTwoBot(0,BigTwoBot.winPercentageStrategy)
  return bot.strategy(bot,hand, isStartOfRound, playToBeat, roundHistory, playerNo, handSizes, scores, roundNo)

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
    lastPlayerNo = -1
    while(True):
      for playerNo,player in enumerate(self.players):
        #Located First Player
        if foundRoundStarter == False:
          if ((playerNo == roundStarter) or (roundStarter == -1 and '3D' in player.cards)):
            foundRoundStarter = True
          else:
            continue
        #Make Play
        if playerNo == lastPlayerNo:
          return playerNo
        else:
          currentPlay = player.strategy(player,player.cards, True, playToBeat, roundHistory, playerNo, self.getCardCount(), self.dummyScores(), roundNo)
          assert(Dealer.validPlay(player.cards,currentPlay,playToBeat) == True)
          if len(currentPlay) > 0:
            playToBeat = currentPlay
            lastPlayerNo = playerNo
            Dealer.removePlayedCards(currentPlay,player.cards)
          current_round_history.append((playerNo,currentPlay))
        #Misc
        if playing == True: 
          if len(currentPlay) == 0:
            print("player " + str(playerNo) + " has passed")
          else:
            print("player " + str(playerNo) + " played " + ' '.join(currentPlay))
          print("player " + str(playerNo) + " cards:",' '.join(sorted(player.cards,key=Dealer.cardValue)))
        if self.win(): return playerNo

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
  def sortCombos(combos):
    return sorted(combos,key=Dealer.comboSum)

  @staticmethod
  def sortFullHouses(combos):
    sortedCombos = []
    for combo in combos:
      index = 0
      for index,comparisonCombo in enumerate(sortedCombos):
        if Dealer.checkBiggerFullHouse(comparisonCombo,combo): break
      sortedCombos.insert(index,combo) #Insert before bigger combo
    return sortedCombos

  @staticmethod
  def cardValue(card):
    return 4 * (Dealer.RANK_IMPORTANCE[card[0]]) + (Dealer.SUIT_IMPORTANCE[card[1]]) #Card[0]:Rank Card[1]:Suit

  @staticmethod
  def comboSum(combo):
    return sum(Dealer.cardValue(combo[cardNum]) for cardNum in range(len(combo)))

  @staticmethod
  def getAllCombos(hand,comboSize):
    sameValue = Dealer.rankCardDict(hand)
    combos = []
    for cards in sameValue.values():
      combos += [list(combo) for combo in itertools.combinations(cards,comboSize)]
    return combos

  @staticmethod
  def availableComboBeaters(hand,comboType):
    if comboType in {1,2,3,4}:
      comboSize = comboType
      return Dealer.getAllCombos(hand,comboSize)
    elif comboType == 'FULL':
      return Dealer.getAllFullHouses(hand)
    elif comboType == 'STRAIGHT':
      return []
    elif comboType == 'FLUSH':
      return []
    else:
      return False

  @staticmethod
  def rankCardDict(cards):
    sameRankedCards = {}
    for card in cards:
      rank = card[0]
      if rank in sameRankedCards: sameRankedCards[rank].append(card)
      else: sameRankedCards[rank] = [card]
    return sameRankedCards

  @staticmethod
  def checkBiggerCombo(combo1, combo2):
    valueType1 = combo1[0][0]
    valueType2 = combo2[0][0]
    firstMaxSuitVal = max(Dealer.SUIT_IMPORTANCE[card[1]] for card in combo1)
    secondMaxSuitVal = max(Dealer.SUIT_IMPORTANCE[card[1]] for card in combo2)
    if Dealer.RANK_IMPORTANCE[valueType1] > Dealer.RANK_IMPORTANCE[valueType2]: return True
    elif Dealer.RANK_IMPORTANCE[valueType2] > Dealer.RANK_IMPORTANCE[valueType1]: return False
    elif firstMaxSuitVal > secondMaxSuitVal: return True
    else: return False
      
  @staticmethod
  def comboCheck(combo):
    if len(combo) <= 4: return len(set(card[0] for card in combo)) == 1
    else: return False

  @staticmethod
  def validPlay(hand,play,playToBeat):
    if all(card in hand for card in play) == False: return False #Cards are in hand
    elif len(play) == 0: return True #Pass Turn
    elif len(playToBeat) == 0: #Free Round
      return any([
        Dealer.comboCheck(play),
        Dealer.fullHouseCheck(play),
        Dealer.straightCheck(play),
        Dealer.flushCheck(play)
        ])
    elif len(playToBeat) == len(play): #Beat Hand
      if Dealer.comboCheck(play): return Dealer.checkBiggerCombo(play,playToBeat)
      elif Dealer.fullHouseCheck(play): return Dealer.checkBiggerFullHouse(play,playToBeat)
      elif Dealer.straightCheck(play): return Dealer.checkBiggerStraight(play,playToBeat)
      elif Dealer.flushCheck(play): return Dealer.checkBiggerFlush(play,playToBeat)
      else: return False
    else: 
      return False

  @staticmethod
  def getRemainingCards(roundHistory):
    return Dealer.CARDS - set(card for currentRound in roundHistory for play in currentRound for card in play[1])

  @staticmethod
  def minPlay(combos,playToBeat):
    def findMinCardBeater(sortedCombos,playToBeat,comparisonFunction):
      for combo in sortedCombos:
        if comparisonFunction(combo,playToBeat): 
          return combo
      else: return []
    if len(playToBeat) <= 4:
      sortedCombos = Dealer.sortCombos(combos)
      return findMinCardBeater(sortedCombos,playToBeat,Dealer.checkBiggerCombo)
    elif len(playToBeat) == 5:
      if Dealer.fullHouseCheck(playToBeat):
        sortedCombos = Dealer.sortFullHouses(combos)
        return findMinCardBeater(sortedCombos,playToBeat,Dealer.checkBiggerFullHouse)
      elif Dealer.straightCheck(playToBeat):
        return []
      elif Dealer.flushCheck(playToBeat):
        return []
      else:
        return False
    else:
      return False

  @staticmethod
  def removeComboCards(combos,cards):
    for combo in combos:
      for card in combo:
        if card in cards:
          cards.remove(card)

  @staticmethod
  def getUnplayedCards(handCombination,startingHand):
    played = set()
    if len(handCombination) != 0:
      for play in handCombination:
        for card in play:
          played.add(card)
    availableCards = startingHand - played
    return availableCards

  @staticmethod
  def getHandCombination(comboPlans,startingHand,combinationFunction):
    seenComboPlans = set()
    for currentCombination in comboPlans:
      tupleComboPlan = tuple(sorted(tuple(sorted(combo)) for combo in currentCombination))
      seenComboPlans.add(tupleComboPlan)
    while(len(comboPlans) != 0):
      newComboPlans = []
      for currentPlan in comboPlans:
        availableCards = Dealer.getUnplayedCards(currentPlan,startingHand)
        for combo in combinationFunction(availableCards):
          newHandCombination = currentPlan + [combo]
          tupleHandCombination = tuple(sorted(tuple(sorted(combo)) for combo in newHandCombination))
          if tupleHandCombination not in seenComboPlans:
            newComboPlans.append(newHandCombination)
            seenComboPlans.add(tupleHandCombination)
      comboPlans = newComboPlans
    return seenComboPlans

  @staticmethod
  def allLargeCombinations(hand):
    startingHand = set(hand)
    existingHandCombinations = [[]]
    for combinationFunction in [Dealer.quadLengthCombinations,Dealer.getAllFullHouses,Dealer.getAllFlushes,Dealer.getAllStraights,Dealer.tripleLengthCombinations]:
      combinationSet = Dealer.getHandCombination(existingHandCombinations,startingHand,combinationFunction)
      existingHandCombinations = [[play for play in combination] for combination in combinationSet]
    return existingHandCombinations

  @staticmethod
  def singleLengthCombinations(cards):
    f = lambda cards:Dealer.getAllCombos(cards,1)
    return f(cards)
  @staticmethod
  def doubleLengthCombinations(cards):
    f = lambda cards:Dealer.getAllCombos(cards,2)
    return f(cards)

  @staticmethod
  def tripleLengthCombinations(cards):
    f = lambda cards:Dealer.getAllCombos(cards,3)
    return f(cards)

  @staticmethod
  def quadLengthCombinations(cards):
    f = lambda cards:Dealer.getAllCombos(cards,4)
    return f(cards)

  @staticmethod
  def fullHouseCheck(cards):
    if len(cards) < 5:
      return False
    else:
      rankedCards = Dealer.rankCardDict(cards)
      if len(rankedCards) == 2:
        combLenOne,combLenTwo = (len(rankedCards[rank]) for rank in rankedCards)
        return (combLenOne,combLenTwo) == (2,3) or (combLenOne,combLenTwo) == (3,2)
      else:
        return False
  
  @staticmethod
  def straightCheck(cards):
    return False

  @staticmethod
  def flushCheck(cards):
    return False

  @staticmethod
  def checkBiggerFullHouse(play,playToBeat):
    def findFullHouse(rankedCards):
      firstRank,secondRank = (rankedCards[rank] for rank in rankedCards)
      if len(firstRank) == 3: 
        return (firstRank,secondRank) #returned in form triples then doubles
      else: 
        return (secondRank,firstRank)
    firstRankedCards = Dealer.rankCardDict(play)
    secondRankedCards = Dealer.rankCardDict(playToBeat)
    firstFullHouse = findFullHouse(firstRankedCards)
    secondFullHouse = findFullHouse(secondRankedCards)
    sortedFull = sorted([firstFullHouse,secondFullHouse],key=lambda x: (Dealer.comboSum(x[0]), Dealer.comboSum(x[1])),reverse=True)
    return sortedFull[0] == firstFullHouse

  @staticmethod
  def checkBiggerStraight(play,playToBeat):
    return False

  @staticmethod
  def checkBiggerFlush(play,playToBeat):
    return False

  @staticmethod
  def getAllFullHouses(cards):
    cards = set(cards)
    triples = Dealer.getAllCombos(cards,3)
    fullHouses = []
    for triple in triples:
      doubles = Dealer.getAllCombos(cards - set(triple),2)
      for double in doubles:
        fullHouses.append(triple + double)
    return fullHouses

  @staticmethod
  def getAllFlushes(cards):
    return []

  @staticmethod
  def getAllStraights(cards):
    return []

  @staticmethod
  def find3DCombo(optimalCombos):
    for size in optimalCombos:
      for combo in optimalCombos[size]:
        if '3D' in combo:
          return combo
    return []

  @staticmethod
  def firstRoundPlay(optimalCombos,unplayed,hand):
    combo = []
    for size in optimalCombos:
      sortedCombos = Dealer.sortCombos(optimalCombos[size])
      if len(sortedCombos) > 0:
        return sortedCombos[0]
    return combo

  @staticmethod
  def getComboType(combo):
    if len(combo) == 0: return None
    elif Dealer.comboCheck(combo): return len(combo)
    elif Dealer.fullHouseCheck(combo): return 'FULL'
    elif Dealer.flushCheck(combo): return 'FLUSH'
    elif Dealer.straightCheck(combo): return 'STRAIGHT'

  def playGame(self,playing):
    round_no = 0
    round_history = []
    round_starter = -1
    while(self.win() != True):
      round_starter = self.startRound(round_no,round_history,round_starter,playing)
      round_no += 1
    for player_no,player in enumerate(self.players):
      if len(player.cards) == 0:
        return player_no,self.getCardCount()
    else:
      return False

  @staticmethod  
  def testing(players,gameCount,playing):
    playerCount = len(players)
    game = Dealer(playerCount,players)
    wins = [0 for i in range(playerCount)]
    cardCounts = [0 for i in range(playerCount)]
    for gameNo in range(gameCount):
      winner,playerCardCounts = Dealer.playGame(game,playing)
      if playing: print("player " + str(winner) + " has won game number " + str(gameNo))
      wins[winner] += 1
      for playerNum,cardCount in enumerate(playerCardCounts): cardCounts[playerNum] += cardCount
      game.setupGame()
    return wins,cardCounts

class BigTwoBot:
  def __init__(self,num,strategy,botGenes=False):
    self.num = num
    self.strategy = strategy
    self.numImportance = Dealer.RANK_IMPORTANCE
    self.suitImportance = Dealer.SUIT_IMPORTANCE
    self.cards = []
    self.botGenes = botGenes


  def rateComboPlan(self,comboPlan):
    totalValue = 0
    for comboType,combos in comboPlan.items():
      totalValue += len(combos) * self.botGenes.cardValue[comboType]
    return totalValue

  def optimalComboPlan(self,cards):
    def addCombos(optimalCombos,cards,combinationFunction,key):
      optimalCombos[key] = combinationFunction(cards)
      Dealer.removeComboCards(optimalCombos[key],cards)
    cards = set(cards)
    twos = []
    for card in cards: 
      if card[0] == '2': 
        twos.append(card)
    for two in twos: cards.remove(two)
    optimalComboPlans = []
    possibleLargeCombinations = Dealer.allLargeCombinations(cards)
    for comboPlan in possibleLargeCombinations:
      possibleCombo = {1:[],2:[],3:[],4:[],'FULL':[],'FLUSH':[],'STRAIGHT':[]}
      unplayed = Dealer.getUnplayedCards(comboPlan,cards)
      for combo in comboPlan:
        comboType = Dealer.getComboType(combo)
        if comboType not in possibleCombo:
          possibleCombo[comboType] = [combo]
        else:
          possibleCombo[comboType].append(combo)
      addCombos(possibleCombo,unplayed,Dealer.doubleLengthCombinations,2)
      addCombos(possibleCombo,unplayed,Dealer.singleLengthCombinations,1)
      possibleCombo[1] += [[two] for two in twos]
      optimalComboPlans.append(possibleCombo)

    bestCombo =  max(optimalComboPlans,key=self.rateComboPlan)
    return bestCombo

  def closeWinnerCheck(self,playerNo,handSizes):
    for num in range(len(handSizes)):
      if num != playerNo and handSizes[num] <= int(self.botGenes.thresholdValue['CLOSE_WINNER']):
        return True
    return False

  def optimalPlay(self,selectedCombo,unplayed,playToBeat,hand):
    availableCards = unplayed | set(hand)
    winningChance = self.findWinningChance(selectedCombo,playToBeat,availableCards)
    if winningChance >= self.botGenes.thresholdValue['HIGH_WIN_THRESH']:
      return selectedCombo
    elif winningChance <= self.botGenes.thresholdValue['LOW_WIN_THRESH']:
      return selectedCombo
    else:
      return []

  def findWinningChance(self,combo,playToBeat,availableCards):
    comboType = Dealer.getComboType(playToBeat)
    availableCombos = list(tuple(sorted(combo)) for combo in Dealer.availableComboBeaters(availableCards,comboType))
    sortedCombos = Dealer.sortCombos(availableCombos)
    comboRanks = dict(zip(sortedCombos,range(1,len(sortedCombos)+1)))
    currentRank = comboRanks[tuple(sorted(combo))]
    percentile = currentRank / len(comboRanks)
    return percentile
  
  def playerStrategy(self,hand, isStartOfRound, playToBeat, roundHistory, playerNo, handSizes, scores, roundNo):
    print()
    print("Current hand: " + ' '.join(Dealer.sortCards(hand)))
    print("Play to beat: " + ' '.join(playToBeat))
    print("Current hand sizes: " + ' '.join('P'+str(i)+':'+str(handSize) for i,handSize in enumerate(handSizes)))
    play = []
    while(True):
      line = input("Play a hand: ")
      play = line.split()
      if line == "": 
        print()
        return []
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
      combos = Dealer.availableComboBeaters(hand,Dealer.getComboType(playToBeat))
      return Dealer.minPlay(combos,playToBeat)

  def winPercentageStrategy(self,hand, isStartOfRound, playToBeat, roundHistory, playerNo, handSizes, scores, roundNo):
    unplayed = Dealer.getRemainingCards(roundHistory)
    optimalCombos = self.optimalComboPlan(hand)
    closeWinnerCheck = self.closeWinnerCheck(playerNo,handSizes)
    if len(playToBeat) == 0:
      if '3D' in hand: return Dealer.find3DCombo(optimalCombos)
      else: return Dealer.firstRoundPlay(optimalCombos,unplayed,hand)
    elif closeWinnerCheck: #Remaining players have few cards left
      combos = Dealer.availableComboBeaters(hand,Dealer.getComboType(playToBeat))
      return Dealer.minPlay(combos,playToBeat)
    else:
      comboType = Dealer.getComboType(playToBeat)
      availableOptimalCombos = optimalCombos[comboType]
      selectedCombo = Dealer.minPlay(availableOptimalCombos,playToBeat)
      if len(selectedCombo) == 0: return [] #No Optimal Play
      else: return self.optimalPlay(selectedCombo,unplayed,playToBeat,hand) #Decide Optimal Play

class BotGenes:
  def __init__(self,thresholdValue,cardValue):
    if thresholdValue == cardValue == False:
      self.generateGenes()
    else:
      self.thresholdValue = thresholdValue
      self.cardValue = cardValue
    self.winPercentage = 0
    self.cardPercentage = 0

  def generateGenes(self):
    self.thresholdValue = {
      'LOW_WIN_THRESH':70 + random.random() * 20,
      'HIGH_WIN_THRESH':80 + random.random() * 20,
      'CLOSE_WINNER':random.randint(1,5)
      }
    self.cardValue = {
      1:0+2*random.random(),
      2:1+3*random.random(),
      3:3+4*random.random(),
      4:6+5*random.random(),
      'FULL':6+5*random.random(),
      'STRAIGHT':6+5*random.random(),
      'FLUSH':6+5*random.random() 
      }

  def getFitness(self):
    fitness =  self.winPercentage * 20 + (1 - self.cardPercentage) * 5
    return fitness

class BotPopulation:
  def __init__(self,popCount,trainingGameCount):
    self.population = self.generatePopulation(popCount)
    self.trainingGameCount = trainingGameCount

  def generatePopulation(self,popCount):
    population = [BigTwoBot(botNum,BigTwoBot.winPercentageStrategy,BotGenes(False,False)) for botNum in range(popCount)]
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
      wins,cardCounts = Dealer.testing(players,self.trainingGameCount,False)
      winPercentage = wins[0] / self.trainingGameCount
      cardPercentage =  (cardCounts[0] / self.trainingGameCount) / 13
      currentBot.botGenes.winPercentage = winPercentage
      currentBot.botGenes.cardPercentage = cardPercentage

  @staticmethod
  def reproduce(parent1,parent2):
    newThreshold = {}
    for key in parent1.botGenes.thresholdValue:
      # val = [parent1.botGenes.thresholdValue[key], parent2.botGenes.thresholdValue[key]][random.randint(0,1)]
      val = (parent1.botGenes.thresholdValue[key] + parent2.botGenes.thresholdValue[key]) / 2
      newThreshold[key] = val
    newCardValues = {}
    for key in parent1.botGenes.cardValue:
      val = (parent1.botGenes.cardValue[key] + parent2.botGenes.cardValue[key]) / 2
      newCardValues[key] = val
    return BotGenes(newThreshold,newCardValues)

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
      indexOne = random.randint(0,len(parentPopulation)-1)
      indexTwo = random.randint(0,len(parentPopulation)-1)
      parentOne = self.population[parentPopulation[indexOne]]
      parentTwo = self.population[parentPopulation[indexTwo]]
      newGene = BotPopulation.reproduce(parentOne,parentTwo)
      newGenes.append(newGene)
    for i in range(len(self.population)):
      self.population[i].botGenes = newGenes[i]

  def findBest(self):
    return max(self.population,key=lambda bot:bot.botGenes.getFitness())

  def trainPopulation(self,iterations):
    self.calculateFitness()
    maxWinPercentage = self.findBest().botGenes.winPercentage
    for i in range(iterations):
      avgWinPercentage = (sum(bot.botGenes.winPercentage for bot in self.population) / len(self.population))
      print('avg-win-percentage:',avgWinPercentage,'max-win-percentage:',maxWinPercentage)
      parents = self.selectParents() #Select parent population for mating
      self.crossOver(parents) #Creates new genes from parents
      self.calculateFitness() #Calculates new fitness
      maxWinPercentage = self.findBest().botGenes.winPercentage
    return self.findBest().botGenes

# {1: 0.6615253641011627, 2: 2.0139692070228947, 3: 4.0542498941325995, 4: 9.828046069608673, 'FULL': 8.501541673847598, 'STRAIGHT': 8.7444655876317, 'FLUSH': 7.777131461613616}
# {'LOW_WIN_THRESH': 80.29205095425843, 'HIGH_WIN_THRESH': 85.25955288540894, 'CLOSE_WINNER': 4.5}

cardValues = {1: 1.0684488147780393, 2: 3.63443791909227, 3: 4.733868136567127, 4: 9.48266346176158, 'FULL': 8.810699627742999, 'STRAIGHT': 7.914590844790364, 'FLUSH': 8.538434973618426}
threshValues = {'LOW_WIN_THRESH': 74.3503219387137, 'HIGH_WIN_THRESH': 96.5471028408307, 'CLOSE_WINNER': 3.7464494705200195}
players = [
          BigTwoBot(0,BigTwoBot.winPercentageStrategy,BotGenes(threshValues,cardValues)),
          BigTwoBot(1,BigTwoBot.playerStrategy),
          BigTwoBot(2,BigTwoBot.minPlayStrategy),
          BigTwoBot(3,BigTwoBot.minPlayStrategy),
          ]
game = Dealer(len(players),players)
print(Dealer.testing(players,1,True))

# pop = BotPopulation(20,20)
# genes = (pop.trainPopulation(20))
# print(genes.cardValue)
# print(genes.thresholdValue)


#Rating system of combo plan
#Straight
#Flushes

#Win against player that goes after
#Pass aginat play that goes before