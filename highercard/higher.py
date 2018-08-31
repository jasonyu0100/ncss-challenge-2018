
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
    


if __name__ == '__main__':
  print(is_higher('8D', '9S'))
  print(is_higher('2S', '2D'))
  print(is_higher('3H', '2H'))
  print(is_higher('QS', 'JS'))
  print(is_higher('AD', '2S'))