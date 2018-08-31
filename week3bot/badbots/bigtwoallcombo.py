'''
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
  def getHandCombination(currentHandCombinations,startingHand,combinationFunction):
    seenCombinations = set()
    for currentCombination in currentHandCombinations:
      tupleHandCombination = tuple(sorted(tuple(sorted(combo)) for combo in currentCombination))
      seenCombinations.add(tupleHandCombination)
    while(len(currentHandCombinations) != 0):
      newHandCombinations = []
      for handCombination in currentHandCombinations:
        availableCards = Dealer.getUnplayedCards(handCombination,startingHand)
        for combo in combinationFunction(availableCards):
          newHandCombination = handCombination + [combo]
          tupleHandCombination = tuple(sorted(tuple(sorted(combo)) for combo in newHandCombination))
          if tupleHandCombination not in seenCombinations:
            newHandCombinations.append(newHandCombination)
            seenCombinations.add(tupleHandCombination)
      currentHandCombinations = newHandCombinations
    return seenCombinations

  @staticmethod
  def allPossibleHandCombinations(hand):
    singleLengthCombinations = lambda cards:Dealer.getAllCombos(cards,1)
    doubleLengthCombinations = lambda cards:Dealer.getAllCombos(cards,2)
    tripleLengthCombinations = lambda cards:Dealer.getAllCombos(cards,3)
    quadLengthCombinations = lambda cards:Dealer.getAllCombos(cards,4)
    bigCombinationPreferences = [
      quadLengthCombinations,
      Dealer.getAllFullHouses,
      Dealer.getAllFlushes,
      Dealer.getAllStraights,
      tripleLengthCombinations,
    ]
    minCombinationPreferences = [
      doubleLengthCombinations,
      singleLengthCombinations,
    ]
    startingHand = set(hand)
    existingHandCombinations = [[]]
    for combinationFunction in bigCombinationPreferences:
      combinationSet = Dealer.getHandCombination(existingHandCombinations,startingHand,combinationFunction)
      existingHandCombinations = [[play for play in combination] for combination in combinationSet]
    # combinationSet.remove(())
    # existingHandCombinations = [[play for play in combination] for combination in combinationSet]
    for combinationFunction in minCombinationPreferences:
      combinationSet = Dealer.getHandCombination(existingHandCombinations,startingHand,combinationFunction)
      existingHandCombinations = [[play for play in combination] for combination in combinationSet]
    return existingHandCombinations
'''