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
  def sortCombos(combos):
    return sorted(combos,key=Dealer.comboSum)

  @staticmethod
  def cardValue(card):
    return 4 * (Dealer.RANK_IMPORTANCE[card[0]]) + (Dealer.SUIT_IMPORTANCE[card[1]]) #Card[0]:Rank Card[1]:Suit

  @staticmethod
  def comboSum(combo):
    return sum(Dealer.cardValue(combo[cardNum]) for cardNum in range(len(combo)))

  @staticmethod
  def possibleCardCombos(hand,comboSize):
    sameValue = Dealer.rankCardDict(hand)
    combos = []
    for cards in sameValue.values():
      combos += [list(combo) for combo in itertools.combinations(cards,comboSize)]
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
  def validCombo(combo):
    return len(set(card[0] for card in combo)) == 1

  @staticmethod
  def validPlay(hand,play,playToBeat):
    if all(card in hand for card in play) == False: 
      return False
    elif len(play) == 0: 
      return True
    elif len(playToBeat) == 0:
      if len(play) in {1,2,3,4}: 
        return Dealer.validCombo(play)
      elif Dealer.fullHouseCheck(play) == True:
        return True
      else: #Straights or flushes
        pass
    elif len(playToBeat) == len(play):
      if len(play) in {1,2,3,4}:
        if Dealer.validCombo(play):
          return Dealer.checkBiggerCombo(play,playToBeat)
      elif Dealer.fullHouseCheck(play) == True:
        return True
      else: #Straights or flushes
        pass
    else: 
      return False

  @staticmethod
  def getRemainingCards(roundHistory):
    return Dealer.CARDS - set(card for currentRound in roundHistory for play in currentRound for card in play[1])

  @staticmethod
  def minPlay(combos,playToBeat):
    sortedCombos = Dealer.sortCombos(combos)
    for combo in sortedCombos:
      if Dealer.checkBiggerCombo(combo,playToBeat): return combo
    else: return []

  @staticmethod
  def removeComboCards(combos,cards):
    for combo in combos:
      for card in combo:
        if card in cards:
          cards.remove(card)

  @staticmethod
  def rateComboPlan(combos):
    return 0

  @staticmethod
  def optimalComboPlan(hand):
    optimalCombos = {}
    cards = set(hand)
    twos = filter(lambda card:card[0]==2,cards)
    Dealer.removeComboCards(twos,cards)
    #Check for full houses and flushes and straights

    posssibleFullHouses = Dealer.getAllFullHouses(cards)
    possibleFlushes = Dealer.getAllFlushes(cards)
    possibleStraights = Dealer.getAllStraights(cards)


    optimalCombos[3] = Dealer.possibleCardCombos(list(cards),3)
    Dealer.removeComboCards(optimalCombos[3],cards)
    optimalCombos[2] = Dealer.possibleCardCombos(list(cards),2)
    Dealer.removeComboCards(optimalCombos[2],cards)
    optimalCombos[1] = Dealer.possibleCardCombos(list(cards),1)
    optimalCombos[1] += [[two] for two in twos]
    Dealer.removeComboCards(optimalCombos[1],cards)
    return optimalCombos

  @staticmethod
  def fullHouseCheck(cards):
    rankedCards = Dealer.rankCardDict(cards)
    if len(rankedCards) == 2:
      combLenOne,combLenTwo = (len(rankedCards[rank]) for rank in rankedCards)
      return (combLenOne,combLenTwo) == (2,3) or (combLenOne,combLenTwo) == (3,2)
    else:
      return False

  @staticmethod
  def findFullHouse(rankedCards):
    firstRank,secondRank = (rankedCards[rank] for rank in rankedCards)
    if len(firstRank) == 3: 
      return (firstRank,secondRank) #returned in form triples then doubles
    else: 
      return (secondRank,firstRank)

  @staticmethod
  def betterFullHouse(first,second):
    firstRankedCards = Dealer.rankCardDict(first)
    secondRankedCards = Dealer.rankCardDict(second)
    firstFullHouse = Dealer.findFullHouse(firstRankedCards)
    secondFullHouse = Dealer.findFullHouse(secondRankedCards)
    sortedFull = sorted([firstFullHouse,secondFullHouse],key=lambda x: (Dealer.comboSum(x[0]), Dealer.comboSum(x[1])),reverse=True)
    return sortedFull[0] == firstFullHouse

  @staticmethod
  def getAllFullHouses(cards):
    cards = set(cards)
    triples = Dealer.possibleCardCombos(cards,3)
    fullHouses = []
    for triple in triples:
      doubles = Dealer.possibleCardCombos(cards - set(triple),2)
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
  def findWinningChance(combo,unplayed,comboSize,hand):
    availableCards = unplayed - set(hand)
    availableCards |= set(combo)
    availableCombos = list(tuple(sorted(combo)) for combo in Dealer.possibleCardCombos(availableCards,comboSize))
    sortedCombos = Dealer.sortCombos(availableCombos)
    comboRanks = dict(zip(sortedCombos,range(1,len(sortedCombos)+1)))
    currentRank = comboRanks[tuple(sorted(combo))]
    percentile = currentRank / len(comboRanks)
    return percentile

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
  def closeWinnerCheck(playerNo,handSizes):
    for num in range(len(handSizes)):
      if num != playerNo:
        if handSizes[num] <= 4:
          return True
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
  def testing(players,gameCount,playing):
    playerCount = len(players)
    game = Dealer(playerCount,players)
    wins = [0 for i in range(playerCount)]
    for gameNo in range(gameCount):
      winner = Dealer.playGame(game,playing)
      if playing: print("player " + str(winner) + " has won game number " + str(gameNo))
      wins[winner] += 1
      game.setupGame()
    return wins

class BigTwoBot:
  def __init__(self,num,strategy):
    self.num = num
    self.strategy = strategy
    self.numImportance = Dealer.RANK_IMPORTANCE
    self.suitImportance = Dealer.SUIT_IMPORTANCE
    self.cards = []
  
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
      combos = Dealer.possibleCardCombos(hand,len(playToBeat))
      play = Dealer.minPlay(combos,playToBeat)
      return play

  def winPercentageStrategy(self,hand, isStartOfRound, playToBeat, roundHistory, playerNo, handSizes, scores, roundNo):
    unplayed = Dealer.getRemainingCards(roundHistory)
    optimalCombos = Dealer.optimalComboPlan(hand)
    if len(playToBeat) == 0:
      if '3D' in hand: return Dealer.find3DCombo(optimalCombos)
      else: return Dealer.firstRoundPlay(optimalCombos,unplayed,hand)
    else:
      closeWinnerCheck = Dealer.closeWinnerCheck(playerNo,handSizes)
      if closeWinnerCheck: #Remaining players have few cards left
        combos = Dealer.possibleCardCombos(hand,len(playToBeat))
        play = Dealer.minPlay(combos,playToBeat)
        return play
      else:
        comboSize = len(playToBeat)
        availableOptimalCombos = optimalCombos[comboSize]
        selectedCombo = Dealer.minPlay(availableOptimalCombos,playToBeat)
        if len(selectedCombo) == 0: #No optimal play
          return []
        else: #Available optimal play
          winningChance = Dealer.findWinningChance(selectedCombo,unplayed,comboSize,hand)
          if winningChance >= 0.95:
            return selectedCombo
          elif winningChance <= 0.80:
            return selectedCombo
          else:
            return []

players = [
          BigTwoBot(0,BigTwoBot.winPercentageStrategy),
          BigTwoBot(1,BigTwoBot.playerStrategy),
          BigTwoBot(2,BigTwoBot.minPlayStrategy),
          BigTwoBot(3,BigTwoBot.minPlayStrategy),
          ]
wins = Dealer.testing(players,1,True)
print(wins)

#New goal 
#Rating system of combo plan
#FullHouse
#Straight
#Flushes

#Win against player that goes after
#Pass aginat play that goes before