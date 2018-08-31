import copy
import random

class Dealer:
  RANK_ORDER = '34567890JQKA2'
  SUIT_ORDER = 'DCHS'
  CARDS = {value + suit for value in '34567890JQKA2' for suit in 'DCHS'}
  numImportance = dict([reversed(pair) for pair in enumerate(RANK_ORDER)])
  suitImportance = dict([reversed(pair) for pair in enumerate(SUIT_ORDER)])

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

  def startRound(self,round_no,round_history,round_starter,playing=False):
    current_round_history = []
    round_history.append(current_round_history)
    previousPlay = []
    foundRoundStarter = False
    while(True):
      for player_no,player in enumerate(self.players):
        if ((player_no == round_starter) or (round_starter == -1 and '3D' in player.cards)) and foundRoundStarter == False:
          foundRoundStarter = True
        elif foundRoundStarter == False:
          continue
        if len(current_round_history) == 0:
          currentPlay = player.strategy(player,player.cards, True, previousPlay, round_history, player_no, self.getCardCount(), [None for i in range(len(self.players))], round_no)
          previousPlay = currentPlay
          for card in currentPlay:
              player.cards.remove(card)
          current_round_history.append((player_no,currentPlay))
        elif player_no == current_round_history[-1][0]:
          return player_no
        else:
          currentPlay = player.strategy(player,player.cards, False, previousPlay, round_history, player_no, self.getCardCount(), [None for i in range(len(self.players))], round_no)
          if len(currentPlay) > 0:
            for card in currentPlay:
              player.cards.remove(card)
            previousPlay = currentPlay
            current_round_history.append((player_no,currentPlay))

        if self.win():
          return player_no
        if playing == True:
          print("player " + str(player_no) + " played " + str(currentPlay),"cards: ",sorted(player.cards,key=Dealer.cardValue))

  def win(self):
    return any((len(player.cards) == 0) for player in self.players)

  def getCardCount(self):
    return [len(player.cards) for player in self.players]

  @staticmethod
  def cardValue(card):
    value = card[0]
    suit = card[1]
    totalCost = 4 * (Dealer.numImportance[value]) + (Dealer.suitImportance[suit])
    return totalCost

    
class BigTwoBot:
  def __init__(self,num,strategy):
    self.num = num
    self.strategy = strategy
    self.numImportance = Dealer.numImportance
    self.suitImportance = Dealer.suitImportance
    self.cards = []

  def is_higher(self,card1, card2):
    num1 = card1[0]
    suit1 = card1[1]
    num2 = card2[0]
    suit2 = card2[1]
    if self.numImportance[num1] > self.numImportance[num2]:
        return True
    elif self.numImportance[num1] == self.numImportance[num2]:
      if self.suitImportance[suit1] > self.suitImportance[suit2]:
        return True
      else:
        return False
    else:
        return False

  def sort_cards(self,cards):
    return sorted(cards,key=lambda x:Dealer.cardValue(x))

  def canBeatHand(self,sortedHand,card_to_beat):
    for card in sortedHand:
      if self.is_higher(card,card_to_beat): #Found card that beats current hand
        return card
    else:
      return False

  def higherValueCard(self,startCard,sortedHand,percent):
    for i,card in enumerate(sortedHand):
      if card == startCard:
        break
    start = i
    viableCardRange = len(sortedHand) - start
    higherCardIndex = start + int(viableCardRange * percent)
    return sortedHand[higherCardIndex]

  def oneCardStrategy(self,hand, is_start_of_round, play_to_beat, round_history, player_no, hand_sizes, scores, round_no):
    sortedHand = self.sort_cards(hand)
    if is_start_of_round or len(play_to_beat) == 0:
      return [sortedHand[0]]
    else:
      card_to_beat = play_to_beat[0]
      canBeat = self.canBeatHand(sortedHand,card_to_beat)
      if canBeat:
        minCardBeater = canBeat
        return [minCardBeater]
      else:
        return []
  
  def oneCardStrategy2(self,hand, is_start_of_round, play_to_beat, round_history, player_no, hand_sizes, scores, round_no):
    sortedHand = self.sort_cards(hand)
    earlyGame = all(hand > 6 for hand in hand_sizes)
    midGame = any(hand <= 6 for hand in hand_sizes)
    lateGame = any(hand <= 4 for hand in hand_sizes)
    if is_start_of_round or len(play_to_beat) == 0:
      return [sortedHand[0]]
    else:
      card_to_beat = play_to_beat[0]
      canBeat = self.canBeatHand(sortedHand,card_to_beat)
      if canBeat:
        minCardBeater = canBeat
        value = minCardBeater[0]
        if lateGame:
          maxCard = sortedHand[-1]
          return [maxCard]
        elif midGame:
          return [minCardBeater]
        elif earlyGame:
          if Dealer.numImportance[str(value)] > 8:
            return []
          else:
            return [minCardBeater]
        else:
          return []
      else:
        return []

  def oneCardStrategy3(self,hand, is_start_of_round, play_to_beat, round_history, player_no, hand_sizes, scores, round_no):
    '''
    If there is a round winning card, play all min cards before playing that winnning card (If there are multiple round winners play min)
    Else play min cards until top 3 cards reserved for pass play have been made

    Reserve top 3 cards for the pass play
    '''
    sortedHand = self.sort_cards(hand)
    roundWinningCards = self.winningCards(round_history,hand,player_no,4)
    if is_start_of_round or len(play_to_beat) == 0: #First Play
      return [sortedHand[0]]
    else: #Beat current hand
      card_to_beat = play_to_beat[0]
      canBeat = self.canBeatHand(sortedHand,card_to_beat)
      if canBeat:
        minCardBeater = canBeat
        roundWinners = self.findMinRoundWinner(hand,round_history,roundWinningCards)
        if len(roundWinners) > 0:
          if minCardBeater in roundWinners:
            return [minCardBeater]
          elif minCardBeater in roundWinningCards and minCardBeater not in roundWinners:
            return [] #Current card does not win round
          else:
            return [minCardBeater]
        else:
          lateGame = any(size <= len(roundWinningCards) for size in hand_sizes)
          if lateGame:
            return [minCardBeater]
          if minCardBeater in roundWinningCards:
            return []
          else:
            return [minCardBeater]
      else:
        return []

  def oneCardStrategy4(self,hand, is_start_of_round, play_to_beat, round_history, player_no, hand_sizes, scores, round_no):
    '''
    If there is a round winning card, play all min cards before playing that winnning card (If there are multiple round winners play min)
    Else play min cards until top 3 cards reserved for pass play have been made

    Reserve top 3 cards for the pass play
    '''
    sortedHand = self.sort_cards(hand)
    roundWinningCards = self.winningCards(round_history,hand,player_no,3)
    if is_start_of_round or len(play_to_beat) == 0: #First Play
      return [sortedHand[0]]
    else: #Beat current hand
      card_to_beat = play_to_beat[0]
      canBeat = self.canBeatHand(sortedHand,card_to_beat)
      if canBeat:
        minCardBeater = canBeat
        roundWinners = self.findMinRoundWinner(hand,round_history,roundWinningCards)
        if len(roundWinners) > 0:
          if minCardBeater in roundWinners:
            return [minCardBeater]
          elif minCardBeater in roundWinningCards and minCardBeater not in roundWinners:
            return [] #Current card does not win round
          else:
            return [minCardBeater] 
        else:
          lateGame = any(size <= len(roundWinningCards)+1 for size in hand_sizes)
          if lateGame:
            return [minCardBeater]
          if minCardBeater in roundWinningCards:
            return []
          else:
            return [minCardBeater]
      else:
        return []
    
  def findMinRoundWinner(self,hand,round_history,roundWinningCards):
    '''
    Get set of cards from round_history
    Get cards that havent been played by minusing round_history from whole set 
    Check cards in winning cards and check if they would win round
    Return list of these cards 
    '''
    played = set()
    for currentRound in round_history:
      for turn in currentRound:
        play = turn[1]
        for card in play:
          played.add(card)
    unplayed = set(Dealer.CARDS) - played
    opponentUnplayed = unplayed - set(hand)
    if len(opponentUnplayed) == 0:
      maxOpponentCardValue = 0
    else:
      maxOpponentCardValue = max(Dealer.cardValue(card) for card in opponentUnplayed)
    roundWinners = []
    for card in roundWinningCards:
      if Dealer.cardValue(card) > maxOpponentCardValue:
        roundWinners.append(card)
    return roundWinners

  def winningCards(self,round_history,hand,player_no,numCards):
    myCards = []
    for currentRound in round_history:
      for turn in currentRound:
        num = turn[0]
        play = turn[1]
        if num == player_no:
          for card in play:
            myCards.append(card)
    myCards += hand
    sortedCards = sorted(myCards,key=Dealer.cardValue)
    return [sortedCards[i] for i in range(-1,-numCards-1,-1)]


  def playerStrategy(self,hand, is_start_of_round, play_to_beat, round_history, player_no, hand_sizes, scores, round_no):
    '''
    Min card strategy which always plays min card
    '''
    print()
    print("Current hand: " + str(self.sort_cards(hand)))
    print("Play to beat: " + str(play_to_beat))
    print("Current hand sizes: " + str(hand_sizes))
    print("Type 'PASS' to pass turn.")
    while(True):
      card = input("Play a card: ")
      if card == "PASS":
        return []
      elif card in hand:
        return [card]
  
  def play(self,hand, is_start_of_round, play_to_beat, round_history, player_no, hand_sizes, scores, round_no):
    bigTwo = BigTwoBot(0,BigTwoBot.oneCardStrategy3)
    return bigTwo.strategy(bigTwo,hand, is_start_of_round, play_to_beat, round_history, player_no, hand_sizes, scores, round_no)
    
  @staticmethod
  def getRemainingCards(round_history):
    played = set()
    for currentRound in round_history:
      for play in currentRound:
        player_no,hand = play
        for card in hand:
          played.add(card)
    return Dealer.CARDS - played

def play(hand, is_start_of_round, play_to_beat, round_history, player_no, hand_sizes, scores, round_no):
  bigTwo = BigTwoBot(0,BigTwoBot.oneCardStrategy3)
  return bigTwo.strategy(bigTwo,hand, is_start_of_round, play_to_beat, round_history, player_no, hand_sizes, scores, round_no)

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
  
def testing():
  players = [
    BigTwoBot(0,BigTwoBot.oneCardStrategy),
    BigTwoBot(1,BigTwoBot.oneCardStrategy),
    BigTwoBot(2,BigTwoBot.oneCardStrategy),
    BigTwoBot(3,BigTwoBot.oneCardStrategy4)
  ]
  playerCount = len(players)
  game = Dealer(playerCount,players)
  wins = [0 for i in range(playerCount)]
  gameCount = 1000
  playing = False

  for game_no in range(gameCount):
    winner = playGame(game,playing)
    if playing:
      print("Player " + str(winner) + " has won game number " + str(game_no))
    wins[winner] += 1
    game.setupGame()
  print(wins)
for i in range(5):
  testing()