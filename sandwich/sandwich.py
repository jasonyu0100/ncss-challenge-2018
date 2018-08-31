preferences = open('preferences.txt')
sandwiches = open('sandwiches.txt')
ingredientsDict = {}
for line in preferences:
  name,val = line.strip().split(',')
  val = int(val)
  ingredientsDict[name] = val
 
combinations = []
for line in sandwiches:
  combination = line.strip().split(',')
  combinations.append(combination)
def alphabetical(value):
  return ','.join(value)
combinations.sort(key=alphabetical)

def preference(values):
  total = sum(ingredientsDict[key] if key in ingredientsDict else 0 for key in values)
  return total

sortedCombinations = []
for combination in combinations:
  total = preference(combination)
  for otherCombinations in sortedCombinations:
    if otherCombinations[0] == total:
      otherCombinations[1].append(combination)
      break
  else:
    sortedCombinations.append((total,[combination]))
    
for combinationType in sortedCombinations:
  combinationType[1].sort(key=len,reverse=True)
  
sortedCombinations.sort(key=lambda x:(x[0]),reverse=True)
if len(sortedCombinations) == 0:
  print("devo :(")
else:
  for combinationSize in sortedCombinations:
    for combination in combinationSize[1]:
      print(','.join(combination))


preferences.close()
sandwiches.close()