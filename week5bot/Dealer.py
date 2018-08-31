import copy
import random
import itertools

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
        if foundRoundStarter == False:
          if ((playerNo == roundStarter) or (roundStarter == -1 and '3D' in player.cards)):
            foundRoundStarter = True
          else:
            continue
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
        if playing == True: 
          if len(currentPlay) == 0: print("EVENT: " + player.name + " has passed")
          else: print("EVENT: " + player.name + " played " + ' '.join(currentPlay))
          print('CARDS:',' '.join(player.cards))
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
    if all(card in hand for card in play) == False:
      raise Exception('Not all cards are in hand')
    elif Dealer.getComboType(play) == 'INVALID': 
      print(play,playToBeat)
      raise Exception('Invalid combo')
    elif len(play) == 0 or len(playToBeat) == 0: 
      return True #PASSES
    elif Dealer.betterPlay(play,playToBeat): 
      return True
    else: 
      raise Exception('Play does not beat play to beat')

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