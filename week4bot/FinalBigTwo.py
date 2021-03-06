import copy
import random
import itertools
# random.seed(1)

def play(hand, isStartOfRound, playToBeat, roundHistory, playerNo, handSizes, scores, roundNo):
  bot = BigTwoBot(0,BigTwoBot.winningStrategy,BotGenes(BotGenes.ITERATION_FIVE))
  play = bot.strategy(bot,hand, isStartOfRound, playToBeat, roundHistory, playerNo, handSizes, scores, roundNo)
  if Dealer.validPlay(hand,play,playToBeat) == True: return play
  else: return []

class Dealer:
  RANK_ORDER = '34567890JQKA2'
  SUIT_ORDER = 'DCHS'
  RANK_IMPORTANCE = dict(zip(RANK_ORDER,range(len(RANK_ORDER))))
  SUIT_IMPORTANCE = dict(zip(SUIT_ORDER,range(len(SUIT_ORDER))))
  CARDS = {value + suit for value in '34567890JQKA2' for suit in 'DCHS'}
  COMBO_HIERARCHY = ['SINGLE','DOUBLE','TRIPLE','STRAIGHT','FLUSH','FULL','QUAD','STRAIGHT_FLUSH']

  def __init__(self,playerCount,players):
    self.playerCount = playerCount
    self.players = players
    self.setupGame()

  def setupGame(self):
    cards = Dealer.generateRandomDeck()
    for player in self.players:
      player.cards = []
      player.roundWinningCards = []
      self.dealCards(player,cards)
    
  def dealCards(self,player,cards,playing=False):
    cardCount = int(len(Dealer.CARDS) / self.playerCount)
    for i in range(cardCount):
      card = cards.pop(0)
      player.cards.append(card)

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
          if playing:
            print('EVENT: ' + player.name + ' has won the round')
            print()
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
            print("EVENT: " + player.name + " has passed")
          else:
            print("EVENT: " + player.name + " played " + ' '.join(currentPlay))
          # print('Cards:',' '.join(player.cards))
        if self.win(): 
          if playing:
            print('EVENT: ' + player.name + ' has won the round')
            print()
          return playerNo

  def customGameSetup(self,presetCards=False):
    cardsPerPlayer = int(52 / self.playerCount)
    if presetCards != False:
      for player in self.players:
        player.cards = []
        for i in range(cardsPerPlayer):
          player.cards.append(presetCards.pop(0))
    else:
      seenCards = set()
      for player in self.players:
        print('Player',player.name,'setup')
        correctCardInput = False
        while correctCardInput == False:
          cards = input("Enter player cards for game: ").split()
          if len(cards) != cardsPerPlayer:
            print('There should have been',cardsPerPlayer,'listed!')
            print('Either restart setup or try again!')
          elif not any(card in seenCards for card in cards):
            player.cards = cards
            seenCards |= set(cards)
            correctCardInput = True
          else:
            print('Card has already been added to another players hand!')
            print('Either restart setup or try again!')

  def playGame(self,playing=False,customGame=False,presetCards=False):
    round_no = 0
    round_history = []
    round_starter = -1
    if customGame == True:
      self.customGameSetup(presetCards=presetCards)
    while(self.win() != True):
      round_starter = self.startRound(round_no,round_history,round_starter,playing)
      round_no += 1
    for player_no,player in enumerate(self.players):
      if len(player.cards) == 0:
        if playing: 
          print('EVENT: ' + player.name + " has won!")
        return player_no,self.getCardCount()
    else:
      return False
  
  def win(self):
    return any((len(player.cards) == 0) for player in self.players)

  def getCardCount(self):
    return [len(player.cards) for player in self.players]

  def dummyScores(self):
    return [None for i in range(len(self.players))]
  
  @staticmethod 
  def getCards(fileName):
    allCards = []
    with open(fileName) as f:
      for line in f:
        allCards += line.strip().split()
    return allCards
  
  @staticmethod
  def generateRandomDeck():
    cards = copy.deepcopy(list(Dealer.CARDS))
    random.shuffle(cards)
    return cards

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
  def sortSpecialCombos(combos,comparsionFunction):
    sortedCombos = []
    for combo in combos:
      index = 0
      for index,comparisonCombo in enumerate(sortedCombos):
        if comparsionFunction(comparisonCombo,combo): break
      sortedCombos.insert(index,combo) #Insert before bigger combo
    return sortedCombos

  @staticmethod
  def sortComboType(availableCombos,comboType):
    if comboType in {'SINGLE','DOUBLE','TRIPLE'}: return Dealer.sortCombos(availableCombos)
    elif comboType == 'QUAD': return Dealer.sortSpecialCombos(availableCombos,Dealer.checkBiggerQuad)
    elif comboType == 'FULL': return Dealer.sortSpecialCombos(availableCombos,Dealer.checkBiggerFullHouse)
    elif comboType == 'STRAIGHT_FLUSH': return Dealer.sortSpecialCombos(availableCombos,Dealer.checkBiggerStraightFlush)
    elif comboType == 'FLUSH': return Dealer.sortSpecialCombos(availableCombos,Dealer.checkBiggerFlush)
    elif comboType == 'STRAIGHT': return Dealer.sortSpecialCombos(availableCombos,Dealer.checkBiggerStraight)
    else: return False

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
    playableComboTypes = Dealer.getPlayableComboTypes(comboType)
    for currentComboType in playableComboTypes:
      if currentComboType in {'SINGLE','DOUBLE','TRIPLE'}: 
        if currentComboType =='SINGLE': return Dealer.getAllCombos(hand,1)
        elif currentComboType =='DOUBLE': return Dealer.getAllCombos(hand,2)
        elif currentComboType =='TRIPLE': return Dealer.getAllCombos(hand,3)
      elif currentComboType == 'STRAIGHT_FLUSH': return Dealer.getAllStraightFlushCombos(hand)
      elif currentComboType == 'QUAD': return Dealer.getAllQuads(hand)
      elif currentComboType == 'FULL': return Dealer.getAllFullHouses(hand)
      elif currentComboType == 'FLUSH': return Dealer.getAllFlushCombos(hand)
      elif currentComboType == 'STRAIGHT': return Dealer.getAllStraightFlushCombos(hand)
    else: return False

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
    return len(combo) <= 3 and len(set(card[0] for card in combo)) == 1 #Checks if 1,2,3 and all of same rank

  @staticmethod
  def betterPlay(play,playToBeat):
    playType = Dealer.getComboType(play) 
    playToBeatType = Dealer.getComboType(playToBeat)
    if len(play) != len(playToBeat):  return False
    elif playToBeatType != playType: return playType in Dealer.getPlayableComboTypes(playToBeatType)
    elif Dealer.comboCheck(play): return Dealer.checkBiggerCombo(play,playToBeat)
    elif Dealer.straightFlushCheck(play): return Dealer.checkBiggerStraightFlush(play,playToBeat)
    elif Dealer.quadCheck(play): return Dealer.checkBiggerQuad(play,playToBeat)
    elif Dealer.fullHouseCheck(play): return Dealer.checkBiggerFullHouse(play,playToBeat)
    elif Dealer.straightCheck(play): return Dealer.checkBiggerStraight(play,playToBeat)
    elif Dealer.flushCheck(play): return Dealer.checkBiggerFlush(play,playToBeat)
    else:return False

  @staticmethod
  def validPlay(hand,play,playToBeat):
    if all(card in hand for card in play) == False or Dealer.getComboType(play) == 'INVALID': return False
    elif len(play) == 0 or len(playToBeat) == 0: return True #PASSES
    elif Dealer.betterPlay(play,playToBeat): return True
    else: return False

  @staticmethod
  def getRemainingCards(roundHistory):
    return Dealer.CARDS - set(card for currentRound in roundHistory for play in currentRound for card in play[1])

  @staticmethod
  def removeComboCards(combos,cards):
    for combo in combos:
      for card in combo:
        if card in cards:
          cards.remove(card)

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
  def quadCheck(cards):
    if len(cards) == 5:
      ranks = [card[0] for card in cards]
      for rank in ranks:
        if ranks.count(rank) == 4:
          return True
    return False

  @staticmethod
  def fullHouseCheck(cards):
    if len(cards) == 5:
      rankedCards = Dealer.rankCardDict(cards)
      if len(rankedCards) == 2:
        combLeNone,combLenTwo = (len(rankedCards[rank]) for rank in rankedCards)
        return (combLeNone,combLenTwo) == (2,3) or (combLeNone,combLenTwo) == (3,2)
      else:
        return False
    else:
      return False
  
  @staticmethod
  def straightCheck(cards):
    if len(cards) == 5:
      cardRanks = [Dealer.RANK_IMPORTANCE[card[0]] for card in cards]
      minRank = min(cardRanks)
      for rank in range(minRank,minRank+5):
        if rank not in cardRanks:
          return False
      else:
        return True
    else:
      return False

  @staticmethod
  def flushCheck(cards):
    if len(cards) == 5:
      firstSuit = cards[0][1]
      for card in cards:
        if card[1] != firstSuit:
          return False
      else:
        return True
    else:
      return False

  @staticmethod
  def straightFlushCheck(cards):
    return Dealer.straightCheck(cards) and Dealer.flushCheck(cards)

  @staticmethod
  def checkBiggerQuad(play,playToBeat):
    ranks = [card[0] for card in play]
    maxPlayRank = None
    for rank in ranks:
      if ranks.count(rank) == 4:
        maxPlayRank = rank
    maxPlayToBeatRank = None
    ranks = [card[0] for card in playToBeat]
    for rank in ranks:
      if ranks.count(rank) == 4:
        maxPlayToBeatRank = rank
    return Dealer.RANK_IMPORTANCE[maxPlayRank] > Dealer.RANK_IMPORTANCE[maxPlayToBeatRank]

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
  def compareComboCardValue(play,playToBeat):
    first =  tuple(sorted([Dealer.cardValue(card) for card in play],reverse=True))
    second = tuple(sorted([Dealer.cardValue(card) for card in playToBeat],reverse=True))
    if sorted([first,second],reverse=True)[0] == first: return True
    else: return False

  @staticmethod
  def checkBiggerStraight(play,playToBeat):
    return Dealer.compareComboCardValue(play,playToBeat)

  @staticmethod
  def checkBiggerFlush(play,playToBeat):
    playSuit = Dealer.SUIT_IMPORTANCE[play[0][1]]
    playToBeatSuit = Dealer.SUIT_IMPORTANCE[playToBeat[0][1]]
    if playSuit > playToBeatSuit: return True
    elif playSuit < playToBeatSuit: return False
    else: return Dealer.compareComboCardValue(play,playToBeat)

  @staticmethod
  def checkBiggerStraightFlush(play,playToBeat):
    return Dealer.compareComboCardValue(play,playToBeat)

  @staticmethod
  def getAllQuads(cards):
    actualQuads = []
    possibleQuads = Dealer.quadLengthCombinations(cards)
    for quad in possibleQuads:
      available = set(cards) - set(quad)
      for card in available:
        actualQuads.append(quad + [card])
    return actualQuads
    
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
  def getAllFlushCombos(cards):
    hearts = [card for card in cards if card[1]=='H']
    heartFlushes = list(itertools.combinations(hearts,5))
    diamonds = [card for card in cards if card[1]=='D']
    diamondFlushes = list(itertools.combinations(diamonds,5))
    spades = [card for card in cards if card[1]=='S']
    spadeFlushes = list(itertools.combinations(spades,5))
    clubs = [card for card in cards if card[1]=='C']
    clubFlushes = list(itertools.combinations(clubs,5))
    flushes = heartFlushes + diamondFlushes + spadeFlushes + clubFlushes
    return flushes
  
  @staticmethod
  def getAllStraightFlushCombos(cards):
    straightFlushes = []
    straights = Dealer.getAllStraights(cards)
    for straight in straights:
      if Dealer.flushCheck(straight):
        straightFlushes.append(straight)
    return straightFlushes

  @staticmethod
  def getAllStraights(cards):
    sameRankedCards = {}
    sortedCards = sorted(cards,key=Dealer.cardValue)
    for card in sortedCards:
      rankValue = Dealer.RANK_IMPORTANCE[card[0]]
      if rankValue not in sameRankedCards:
        sameRankedCards[rankValue] = [card]
      else:
        sameRankedCards[rankValue].append(card)
    straights = []
    for cardRank in sorted(sameRankedCards):
      complete=True
      currentStraights = [[]]
      for rank in range(cardRank,cardRank+5):
        newStraights = []
        if rank not in sameRankedCards:
          complete=False
          break
        else:
          for card in sameRankedCards[rank]:
            for currentStraight in currentStraights:
              newStraight = currentStraight + [card]
              newStraights.append(newStraight)
          currentStraights = newStraights
      if complete:
        straights += newStraights
    return straights

  @staticmethod
  def getComboType(combo):
    if len(combo) == 0: return 'PASS'
    elif Dealer.comboCheck(combo): 
      if len(combo) == 1: return 'SINGLE'
      elif len(combo) == 2: return 'DOUBLE'
      elif len(combo) == 3: return 'TRIPLE'
    elif Dealer.straightFlushCheck(combo): return 'STRAIGHT_FLUSH'
    elif Dealer.quadCheck(combo): return 'QUAD'
    elif Dealer.fullHouseCheck(combo): return 'FULL'
    elif Dealer.flushCheck(combo): return 'FLUSH'
    elif Dealer.straightCheck(combo): return 'STRAIGHT'
    else: return 'INVALID'

  @staticmethod
  def getPlayableComboTypes(comboType):
    if comboType in {'SINGLE','DOUBLE','TRIPLE'}:
      return [comboType]
    elif comboType == 'QUAD':
      return ['QUAD']
    else: #5 card plays
      comboIndex = Dealer.COMBO_HIERARCHY.index(comboType)
      return Dealer.COMBO_HIERARCHY[comboIndex:]

  @staticmethod  
  def testing(players,gameCount,playing):
    playerCount = len(players)
    game = Dealer(playerCount,players)
    wins = [0 for i in range(playerCount)]
    cardCounts = [0 for i in range(playerCount)]
    for gameNo in range(gameCount):
      winner,playerCardCounts = Dealer.playGame(game,playing)
      wins[winner] += 1
      for playerNum,cardCount in enumerate(playerCardCounts): cardCounts[playerNum] += cardCount
      game.setupGame()
    return wins,cardCounts

class BigTwoBot:
  def __init__(self,name,strategy,botGenes=False):
    self.name = name
    self.strategy = strategy
    self.numImportance = Dealer.RANK_IMPORTANCE
    self.suitImportance = Dealer.SUIT_IMPORTANCE
    self.cards = []
    self.botGenes = botGenes

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
    comboPlan = {}
    addCombos(comboPlan,cards,Dealer.getAllStraightFlushCombos,'STRAIGHT_FLUSH')
    addCombos(comboPlan,cards,Dealer.quadLengthCombinations,'QUAD')
    addCombos(comboPlan,cards,Dealer.getAllFullHouses,'FULL')
    addCombos(comboPlan,cards,Dealer.getAllFlushCombos,'FLUSH')
    addCombos(comboPlan,cards,Dealer.getAllStraights,'STRAIGHT')
    addCombos(comboPlan,cards,Dealer.tripleLengthCombinations,'TRIPLE')
    addCombos(comboPlan,cards,Dealer.doubleLengthCombinations,'DOUBLE')
    addCombos(comboPlan,cards,Dealer.singleLengthCombinations,'SINGLE')
    if len(comboPlan['QUAD']) > 0: #Add missing single to quad 
      if len(comboPlan['SINGLE']) > 0: 
        minSingle = Dealer.sortCombos(comboPlan['SINGLE'])[0]
        comboPlan['SINGLE'].remove(minSingle)
        for quad in comboPlan['QUAD']: quad.append(minSingle[0])
      else: #If no available single add quad cards to singles
        for combo in comboPlan['QUAD']:
          for card in combo:
            comboPlan['SINGLE'].append([card])
        comboPlan['QUAD'] = []    
    comboPlan['SINGLE'] += [[two] for two in twos]
    return comboPlan
  
  def firstRoundPlay(self,optimalCombos,unplayed,hand):
    if self.botGenes == False:
      firstRoundHierarchy = ['STRAIGHT_FLUSH','FLUSH','STRAIGHT','FULL','QUAD','TRIPLE','DOUBLE','SINGLE']
      for comboType in firstRoundHierarchy:
        sortedCombos = Dealer.sortComboType(optimalCombos[comboType],comboType)
        if len(sortedCombos) > 0:
          return sortedCombos[0]
      return []
    else:
      evaluation = self.comboEvaluation(optimalCombos)
      bestPlayType = (max(evaluation,key=lambda key:evaluation[key]))
      sortedCombos = Dealer.sortComboType(optimalCombos[bestPlayType],bestPlayType)
      if len(sortedCombos) != 0:
        return sortedCombos[0]
      else:
        return []

  def comboEvaluation(self,optimalCombos):
    valueDict = {}
    for comboType in optimalCombos:
      cards = set(card for combo in optimalCombos[comboType] for card in combo)
      value = 0
      if comboType in {'STRAIGHT_FLUSH','FLUSH','STRAIGHT','FULL','QUAD'}:
        value = int(len(cards) / 5) * self.botGenes.genes['5_CARD'] # 6
      elif comboType == 'TRIPLE':
        value = int(len(cards) / 3) * self.botGenes.genes['3_CARD'] # 4
      elif comboType == 'DOUBLE':
        value = int(len(cards) / 2) * self.botGenes.genes['2_CARD'] # 2
      elif comboType == 'SINGLE':
        value = int(len(cards) / 1) * self.botGenes.genes['1_CARD'] # 1
      valueDict[comboType] = value
    return valueDict

  def find3DCombo(self,optimalCombos):
    for comboType in optimalCombos:
      for combo in optimalCombos[comboType]:
        if '3D' in combo:
          return combo
    return []

  def prevPlayerHighPlayCheck(self,currentRoundHistory):
    if self.botGenes == False: return False
    playerNum,previousPlay = currentRoundHistory[-1]
    if len(previousPlay) > 0: #Previous player has played something
      comboType = Dealer.getComboType(previousPlay)
      averageCardValue = sum(Dealer.cardValue(card) for card in previousPlay) / len(previousPlay)
      if comboType == 'STRAIGHT_FLUSH' and averageCardValue > self.botGenes.genes['STRAIGHT_FLUSH']: return True
      elif comboType == 'STRAIGHT' and averageCardValue > self.botGenes.genes['STRAIGHT']: return True
      elif comboType == 'FLUSH' and averageCardValue > self.botGenes.genes['FLUSH']: return True
      elif comboType == 'FULL' and averageCardValue > self.botGenes.genes['FULL']: return True
      elif comboType == 'QUAD' and averageCardValue > self.botGenes.genes['QUAD']: return True 
      elif comboType == 'TRIPLE' and averageCardValue > self.botGenes.genes['TRIPLE']: return True 
      elif comboType == 'DOUBLE' and averageCardValue > self.botGenes.genes['DOUBLE']: return True 
      elif comboType == 'SINGLE' and averageCardValue > self.botGenes.genes['SINGLE']: return True 
      else: return False
    else:
      return False

  def nextPlayerRoundWinCheck(self,currentRoundHistory,playerCount):
    passPlayerCount = playerCount - 2 
    if len(currentRoundHistory) < passPlayerCount:
      return False
    else: #All previous players have passed except original
      return all(currentRoundHistory[-roundNum] == [] for roundNum in range(passPlayerCount))
  
  def closeWinnerCheck(self,playerNo,handSizes):
    for num in range(len(handSizes)):
      if num != playerNo and handSizes[num] <= self.botGenes.genes['CLOSE_WIN']:
        return True
    return False

  def minPlay(self,combos,playToBeat):
    def findMinCardBeater(sortedCombos,playToBeat,comparisonFunction):
      for combo in sortedCombos:
        if comparisonFunction(combo,playToBeat): 
          return combo
      else: return []
    comboType = Dealer.getComboType(playToBeat)
    sortedCombos = Dealer.sortComboType(combos,comboType)
    return findMinCardBeater(sortedCombos,playToBeat,Dealer.betterPlay)
  
  def playerStrategy(self,hand, isStartOfRound, playToBeat, roundHistory, playerNo, handSizes, scores, roundNo):
    comboType = Dealer.getComboType(playToBeat)
    print()
    print(self.name+"'s"+" turn")
    print("CARDS: " + ' '.join(Dealer.sortCards(hand)))
    print("HAND SIZES: " + ' '.join('Player '+str(i)+':'+str(handSize) for i,handSize in enumerate(handSizes)))
    if comboType != 'PASS':
      sortedCombos = Dealer.sortComboType(Dealer.availableComboBeaters(hand,comboType),comboType)
      print("AVAILABLE PLAYS: " + ' | '.join(' '.join(combo) for combo in sortedCombos))
    print("PLAY TYPE: " + comboType)
    print("PLAY TO BEAT: " + ' '.join(playToBeat))
    play = []
    while(True):
      line = input("PLAY: ")
      play = line.split()
      if line == "": 
        print()
        return []
      elif Dealer.validPlay(hand,play,playToBeat): 
        print()
        return play
  
  def minPlayStrategy(self,hand, isStartOfRound, playToBeat, roundHistory, playerNo, handSizes, scores, roundNo):
    if len(playToBeat) == 0: #Play whatever
      if '3D' in hand: 
        for comboType in reversed(Dealer.COMBO_HIERARCHY):
          combos = Dealer.availableComboBeaters(hand,comboType)
          if len(combos) > 0:
            for combo in combos:
              if '3D' in combo:
                return combo
        else:
          return ['3D']
      else: 
        for comboType in reversed(Dealer.COMBO_HIERARCHY):
          combos = Dealer.availableComboBeaters(hand,comboType)
          if len(combos) > 0:
            return combos[0]
        else:
          return []
    else:
      comboType = Dealer.getComboType(playToBeat)
      combos = Dealer.availableComboBeaters(hand,comboType)
      return self.minPlay(combos,playToBeat)

  def passStrategy(self,hand, isStartOfRound, playToBeat, roundHistory, playerNo, handSizes, scores, roundNo):
    return []

  def winningStrategy(self,hand, isStartOfRound, playToBeat, roundHistory, playerNo, handSizes, scores, roundNo):
    unplayed = Dealer.getRemainingCards(roundHistory)
    optimalCombos = self.optimalComboPlan(hand)
    closeWinnerCheck = self.closeWinnerCheck(playerNo,handSizes)
    comboType = Dealer.getComboType(playToBeat)
    playerCount = len(handSizes)
    if len(playToBeat) == 0:
      if '3D' in hand: return self.find3DCombo(optimalCombos)
      else: return self.firstRoundPlay(optimalCombos,unplayed,hand)
    elif closeWinnerCheck: #Remaining players have few cards left
      combos = Dealer.availableComboBeaters(hand,comboType)
      return self.minPlay(combos,playToBeat)
    elif False:#self.nextPlayerRoundWinCheck(roundHistory[-1],playerCount): #Check if last play was made by next player and could win round
      combos = Dealer.availableComboBeaters(hand,comboType)
      return self.minPlay(combos,playToBeat)
    elif self.prevPlayerHighPlayCheck(roundHistory[-1]): #Previous player has played a high hand
      return []
    else:
      availableOptimalCombos = optimalCombos[comboType]
      selectedCombo = self.minPlay(availableOptimalCombos,playToBeat)
      if selectedCombo != []:
        return selectedCombo
      else:
        playableComboTypes = Dealer.getPlayableComboTypes(comboType)[1:]
        for comboType in playableComboTypes:
          availableOptimalCombos = optimalCombos[comboType]
          if len(availableOptimalCombos) == 0: continue
          else: return availableOptimalCombos[0]
        return []

class BotGenes:
  ITERATION_ONE = {'STRAIGHT_FLUSH': 12, 'FLUSH': 36, 'STRAIGHT': 26, 'QUAD': 22, 'FULL': 32, 'TRIPLE': 35, 'DOUBLE': 11, 'SINGLE': 24, 'CLOSE_WIN': 5,'5_CARD':6,'3_CARD':4,'2_CARD':2,'1_CARD':1}
  ITERATION_TWO = {'STRAIGHT_FLUSH': 30, 'FLUSH': 47, 'STRAIGHT': 43, 'QUAD': 37, 'FULL': 36, 'TRIPLE': 16, 'DOUBLE': 40, 'SINGLE': 49, 'CLOSE_WIN': 1,'5_CARD':6,'3_CARD':4,'2_CARD':2,'1_CARD':1} #SEEMS TO WIN MORE AGAINST HARD
  ITERATION_THREE = {'STRAIGHT_FLUSH': 38, 'FLUSH': 13, 'STRAIGHT': 25, 'QUAD': 31, 'FULL': 44, 'TRIPLE': 7, 'DOUBLE': 7, 'SINGLE': 37, 'CLOSE_WIN': 1, '5_CARD': 5, '3_CARD': 3, '2_CARD': 4, '1_CARD': 1}
  ITERATION_FOUR = {'STRAIGHT_FLUSH': 46, 'FLUSH': 39, 'STRAIGHT': 30, 'QUAD': 19, 'FULL': 22, 'TRIPLE': 20, 'DOUBLE': 46, 'SINGLE': 41, 'CLOSE_WIN': 3, '5_CARD': 7, '3_CARD': 5, '2_CARD': 5, '1_CARD': 2} #SEEMS TO WIN MORE AGAINST EASY
  ITERATION_FIVE = {'STRAIGHT_FLUSH': 32, 'FLUSH': 11, 'STRAIGHT': 28, 'QUAD': 44, 'FULL': 17, 'TRIPLE': 30, 'DOUBLE': 40, 'SINGLE': 37, 'CLOSE_WIN': 2, '5_CARD': 5, '3_CARD': 3, '2_CARD': 6, '1_CARD': 1}
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
    # return (1 - self.cardPercentage) * 50 + (self.winPercentage) * 100
    # return (self.winPercentage) * 100

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
    BigTwoBot(1,BigTwoBot.winningStrategy,BotGenes(BotGenes.ITERATION_FIVE)),
    BigTwoBot(1,BigTwoBot.winningStrategy,BotGenes(BotGenes.ITERATION_TWO)),
    BigTwoBot(1,BigTwoBot.minPlayStrategy,BotGenes(BotGenes.ITERATION_THREE)),
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
      newGene = BotPopulation.reproduce(parentITERATION_THREE,parentTwo)
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
    #Get averages genes
    return self.getAverageGene()


# TRAINING 
# pop = BotPopulation(50,10)
# best = pop.trainPopulation(50)
# print(best)

# EVALUATION
players = [
          BigTwoBot('Bot 1',BigTwoBot.winningStrategy,BotGenes(BotGenes.ITERATION_FIVE)),
          BigTwoBot('Bot 2',BigTwoBot.minPlayStrategy,BotGenes(BotGenes.ITERATION_FIVE)),
          BigTwoBot('Jason',BigTwoBot.minPlayStrategy,BotGenes(BotGenes.ITERATION_FIVE)),
          BigTwoBot('Rong',BigTwoBot.minPlayStrategy,BotGenes(BotGenes.ITERATION_FIVE)),
          ]
# game = Dealer(len(players),players)
print(Dealer.testing(players,1000,False))
# game.playGame(playing=True)

# Custom Game
# A mixture of strategies to play against
# players = [
#           BigTwoBot('Bot',BigTwoBot.winningStrategy,BotGenes(BotGenes.ITERATION_FIVE)),
#           BigTwoBot('Kevin',BigTwoBot.playerStrategy,BotGenes(BotGenes.ITERATION_FIVE)),
#           BigTwoBot('Jason',BigTwoBot.playerStrategy,BotGenes(BotGenes.ITERATION_FIVE)),
#           ]
# game = Dealer(len(players),players)
# cards = Dealer.getCards('cards.txt')
# cards = Dealer.generateRandomDeck()
# game.playGame(playing=True,customGame=True,presetCards=False)

#BEST_GENES = {'STRAIGHT_FLUSH': 31.579906397281988, 'FLUSH': 24.9557212342052, 'STRAIGHT': 35.55677314543644, 'QUAD': 33.737532311131176, 'FULL': 25.9097780246274, 3: 24.748219351043467, 2: 31.00665293569748, 1: 20.989323126934565}