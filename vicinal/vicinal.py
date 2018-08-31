IS_VICINAL, IS_NON_VICINAL, IS_NEITHER = 1, 2, 3


def categorise_word(word):
  word = word.lower()
  values = set()
  for letter in word:
    values.add(ord(letter) - 97)
    
  count = 0
  for letter in word:
    right = (ord(letter) - 97 + 1) % 26
    left = (ord(letter) - 97 - 1) % 26
    if right in values or left in values:
      count += 1
  if count == len(word):
    return IS_VICINAL
  elif count == 0:
    return IS_NON_VICINAL
  else:
    return IS_NEITHER
  

if __name__ == '__main__':
  print(categorise_word('The'))
  print(categorise_word('blacksmith'))
  print(categorise_word('fights'))
  print(categorise_word('some'))
  print(categorise_word('baker'))
  print(categorise_word('baa'))