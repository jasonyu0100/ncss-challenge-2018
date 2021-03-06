import copy
import random
import itertools
random.seed(1)

def play(hand, isStartOfRound, playToBeat, roundHistory, playerNo, handSizes, scores, roundNo):
  bot = BigTwoBot(0,BigTwoBot.winningStrategy)
  play = bot.strategy(bot,hand, isStartOfRound, playToBeat, roundHistory, playerNo, handSizes, scores, roundNo)
  if Dealer.validPlay(hand,play,playToBeat) == True: return play
  else: return []

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
          if playing:
            print('player ' + str(playerNo) + ' has won the round')
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
        if self.win(): 
          if playing:
            print('player ' + str(playerNo) + ' has won the round')
          return playerNo

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
  def sortSpecialCombos(combos,comparsionFunction):
    sortedCombos = []
    for combo in combos:
      index = 0
      for index,comparisonCombo in enumerate(sortedCombos):
        if comparsionFunction(comparisonCombo,combo): break
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
    if comboType in {1,2,3}:
      return Dealer.getAllCombos(hand,comboType)
    elif comboType == 'STRAIGHT_FLUSH':
      return Dealer.getAllStraightCombos(hand)
    elif comboType == 'QUAD':
      return Dealer.getAllQuads(hand)
    elif comboType == 'FULL':
      return Dealer.getAllFullHouses(hand)
    elif comboType == 'FLUSH':
      return Dealer.getAllFlushCombos(hand)
    elif comboType == 'STRAIGHT':
      return Dealer.getAllStraightCombos(hand)
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
    if len(combo) <= 3: return len(set(card[0] for card in combo)) == 1
    else: return False

  @staticmethod
  def validPlay(hand,play,playToBeat):
    if all(card in hand for card in play) == False: return False #Cards are in hand
    elif len(play) == 0: return True #Pass Turn
    elif len(playToBeat) == 0: #Free Round
      return any([
        Dealer.comboCheck(play),
        Dealer.quadCheck(play),
        Dealer.fullHouseCheck(play),
        Dealer.straightCheck(play),
        Dealer.flushCheck(play)
        ])
    elif len(playToBeat) == len(play): #Beat Hand
      #Checks if play type is a better combination type than play to beat type
      playType = Dealer.getComboType(play) 
      playToBeatType = Dealer.getComboType(playToBeat)
      if playToBeatType != playType and playType in Dealer.getPlayableComboTypes(playToBeatType): return True
      elif Dealer.comboCheck(play): return Dealer.checkBiggerCombo(play,playToBeat)
      elif Dealer.quadCheck(play): return Dealer.checkBiggerQuad(play,playToBeat)
      elif Dealer.fullHouseCheck(play): return Dealer.checkBiggerFullHouse(play,playToBeat)
      elif Dealer.straightCheck(play): return Dealer.checkBiggerStraight(play,playToBeat)
      elif Dealer.flushCheck(play): return Dealer.checkBiggerFlush(play,playToBeat)
      else: return False
    else:
      playType = Dealer.getComboType(play) 
      playToBeatType = Dealer.getComboType(playToBeat)
      if playToBeatType != playType and playType in Dealer.getPlayableComboTypes(playToBeatType): 
        return True
      else: return False

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
    if len(playToBeat) <= 3:
      sortedCombos = Dealer.sortCombos(combos)
      return findMinCardBeater(sortedCombos,playToBeat,Dealer.checkBiggerCombo)
    elif len(playToBeat) == 5:
      if Dealer.quadCheck(playToBeat):
        sortedCombos = Dealer.sortSpecialCombos(combos,Dealer.checkBiggerQuad)
        return findMinCardBeater(sortedCombos,playToBeat,Dealer.checkBiggerQuad)
      elif Dealer.straightFlushCheck(playToBeat):
        sortedCombos = Dealer.sortSpecialCombos(combos,Dealer.checkBiggerStraightFlush)
        return findMinCardBeater(sortedCombos,playToBeat,Dealer.checkBiggerStraightFlush) 
      elif Dealer.fullHouseCheck(playToBeat):
        sortedCombos = Dealer.sortSpecialCombos(combos,Dealer.checkBiggerFullHouse)
        return findMinCardBeater(sortedCombos,playToBeat,Dealer.checkBiggerFullHouse)
      elif Dealer.straightCheck(playToBeat):
        sortedCombos = Dealer.sortSpecialCombos(combos,Dealer.checkBiggerStraight)
        return findMinCardBeater(sortedCombos,playToBeat,Dealer.checkBiggerStraight)
      elif Dealer.flushCheck(playToBeat):
        sortedCombos = Dealer.sortSpecialCombos(combos,Dealer.checkBiggerFlush)
        return findMinCardBeater(sortedCombos,playToBeat,Dealer.checkBiggerFlush)
      else:
        return []
    else:
      return []

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
        combLenOne,combLenTwo = (len(rankedCards[rank]) for rank in rankedCards)
        return (combLenOne,combLenTwo) == (2,3) or (combLenOne,combLenTwo) == (3,2)
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
  def getAllStraightCombos(cards):
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
    elif Dealer.straightFlushCheck(combo): return 'STRAIGHT_FLUSH'
    elif Dealer.quadCheck(combo): return 'QUAD'
    elif Dealer.fullHouseCheck(combo): return 'FULL'
    elif Dealer.flushCheck(combo): return 'FLUSH'
    elif Dealer.straightCheck(combo): return 'STRAIGHT'

  @staticmethod
  def getPlayableComboTypes(comboType):
    hierarchy = [1,2,3,'STRAIGHT','FLUSH','FULL','QUAD','STRAIGHT_FLUSH']
    if comboType in {1,2,3}:
      return [comboType]
    elif comboType == 'QUAD':
      return ['QUAD']
    else: #5 card plays
      comboIndex = hierarchy.index(comboType)
      return hierarchy[comboIndex:]

  def playGame(self,playing):
    round_no = 0
    round_history = []
    round_starter = -1
    while(self.win() != True):
      round_starter = self.startRound(round_no,round_history,round_starter,playing)
      round_no += 1
    for player_no,player in enumerate(self.players):
      if len(player.cards) == 0:
        if playing: print('player '+str(player_no) + " has won!")
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
    comboPlan = {}
    addCombos(comboPlan,cards,Dealer.getAllStraightCombos,'STRAIGHT_FLUSH')
    addCombos(comboPlan,cards,Dealer.quadLengthCombinations,'QUAD')
    addCombos(comboPlan,cards,Dealer.getAllFullHouses,'FULL')
    addCombos(comboPlan,cards,Dealer.getAllFlushCombos,'FLUSH')
    addCombos(comboPlan,cards,Dealer.getAllStraights,'STRAIGHT')
    addCombos(comboPlan,cards,Dealer.tripleLengthCombinations,3)
    addCombos(comboPlan,cards,Dealer.doubleLengthCombinations,2)
    addCombos(comboPlan,cards,Dealer.singleLengthCombinations,1)
    if len(comboPlan['QUAD']) > 0: #Add missing single to quad 
      if len(comboPlan[1]) > 0: 
        minSingle = Dealer.sortCombos(comboPlan[1])[0]
        comboPlan[1].remove(minSingle)
        for quad in comboPlan['QUAD']: quad.append(minSingle[0])
      else: #If no available single add quad cards to singles
        for combo in comboPlan['QUAD']:
          for card in combo:
            comboPlan[1].append([card])
        comboPlan['QUAD'] = []    
    comboPlan[1] += [[two] for two in twos]
    return comboPlan

  def closeWinnerCheck(self,playerNo,handSizes):
    for num in range(len(handSizes)):
      if num != playerNo and handSizes[num] <= 4:
        return True
    return False

  def playerStrategy(self,hand, isStartOfRound, playToBeat, roundHistory, playerNo, handSizes, scores, roundNo):
    print()
    print("Current hand: " + ' '.join(Dealer.sortCards(hand)))
    print("Current hand sizes: " + ' '.join('Player '+str(i)+':'+str(handSize) for i,handSize in enumerate(handSizes)))
    print("Play to beat: " + ' '.join(playToBeat))
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
      if '3D' in hand: return ['3D']
      else: return [sortedHand[0]]
    else:
      combos = Dealer.availableComboBeaters(hand,Dealer.getComboType(playToBeat))
      return Dealer.minPlay(combos,playToBeat)

  def winningStrategy(self,hand, isStartOfRound, playToBeat, roundHistory, playerNo, handSizes, scores, roundNo):
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
      if selectedCombo != []:
        return selectedCombo
      else: #Searches for higher combo type plays such as a quad play on a double
        playableComboTypes = Dealer.getPlayableComboTypes(comboType)[1:] #First combotype is the default
        for comboType in playableComboTypes:
          availableOptimalCombos = optimalCombos[comboType]
          if len(availableOptimalCombos) == 0: continue
          else: return availableOptimalCombos[0]
        return []

players = [
          BigTwoBot(0,BigTwoBot.winningStrategy),
          BigTwoBot(1,BigTwoBot.minPlayStrategy),
          BigTwoBot(2,BigTwoBot.minPlayStrategy),
          BigTwoBot(3,BigTwoBot.minPlayStrategy),
          ]

game = Dealer(len(players),players)
print(Dealer.testing(players,1000,False))
# game.playGame(True)

#TODO Goals
#Add preference to play against person playing after
#Add preference to not play against person playing before

