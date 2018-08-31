RANK_ORDER = '34567890JQKA2'
SUIT_ORDER = 'DCHS'

def is_higher(card1, card2):
  num1,suit1 = list(card1)
  num2,suit2 = list(card2)
  numImportance = dict([reversed(pair) for pair in enumerate(RANK_ORDER)])
  suitImportance = dict([reversed(pair) for pair in enumerate(SUIT_ORDER)])
  if numImportance[num1] > numImportance[num2]:
    return True
  elif numImportance[num1] == numImportance[num2]:
    if suitImportance[suit1] > suitImportance[suit2]:
      return True
    else:
      return False
  else:
    return False

def sort_cards(cards):
  sortedCards = []
  for currentCard in cards:
    insertIndex = 0
    for comparisonCard in sortedCards:
      if is_higher(comparisonCard, currentCard): #Comparison > Current
        break
      else:
        insertIndex += 1
    sortedCards.insert(insertIndex,currentCard)
  return sortedCards

if __name__ == '__main__':
  print(sort_cards(['AS', '5H']))
  print(sort_cards(['JC', '3H', '6H', 'KH', '6S', '4H', '2C', '2S', '2D', '2H', '4S']))