import xml.etree.ElementTree as ET
from food import Food
from ingMap import IngMap
from getLabel import buildGraph

def getRoot(fileDirectory, fileName):
    return ET.parse(fileDirectory+fileName).getroot()

def getXandY(recipeFile):
    
    root = getRoot('/Users/Mick/Desktop/FoodCapstone/annotated_recipes/',recipeFile)

    # get data from xml file
    annotations = []
    originalTexts = []

    for child in root:
        # get annotations

        ann = child.find('annotation').text
        ann = ann.encode('ascii','ignore')
        ann = ann.decode('unicode_escape').encode('ascii','ignore')
        annotations.append(ann)
        # get unique texts
        oriTxt = child.find('originaltext').text
        oriTxt = oriTxt.encode('ascii','ignore')
        oriTxt = oriTxt.decode('unicode_escape').encode('ascii','ignore')
        originalTexts.append(oriTxt)

    return originalTexts, annotations

def separateIngInstruct(originalTexts,annotations):
    allIngs = []
    
    i = 0
    while isIng(annotations[i]):        
        ingNo, ingString = preProcessIngArgs(annotations[i])
        allIngs.append(ingString)
        i += 1

    return allIngs, originalTexts[i:], annotations[i:]

def getOneToOneMatch(originalTexts,annotations, listOfFuncs):

    dictTexts = {}
    originTextUnique = []
    for i, each in enumerate(originalTexts):
        each = each.rstrip()
        if each in dictTexts.keys():
            for eachF in listOfFuncs:
                if eachF(annotations[i]):
                    dictTexts[each] = annotations[i]
        else:
            for eachF in listOfFuncs:
                if eachF(annotations[i]):
                    dictTexts[each] = annotations[i]
                    originTextUnique.append(each)
    x = []
    y = []
    
    for i, each in enumerate(originTextUnique):
        x.append(each)
        y.append(dictTexts[each])
    
    return x,y

###############################

#2.1 entity creation
commndIng = "create_ing("

#2.2 action
commndComb = "combine("
commndSep = "separate("

#2.3 location - no implementation
#put
#remove
#index of ingredients remain the same

#2.4 alter ingredients
commndCut = "cut("
commndMix = "mix("
commndCook = "cook("
commndDo = "do("

commndPut = "put("

def checkCommnd(text, commndKey):

    return text[:len(commndKey)] == commndKey

def isIng(text):
    return checkCommnd(text,commndIng)

def isNotIng(text):
    return (not isIng(text))

def isComb(text):
    return checkCommnd(text,commndComb)
    
def isSep(text):
    return checkCommnd(text,commndSep)

def isCut(text):
    return checkCommnd(text,commndCut)

def isMix(text):
    return checkCommnd(text,commndMix)

def isCook(text):
    return checkCommnd(text,commndCook)

def isDo(text):
    return checkCommnd(text,commndDo)

def isPut(text):
    return checkCommnd(text,commndPut)


def isGeneral(text):
    return True

###################################



def getArgs(text):
    for charIndex in range(len(text)):
        if (text[charIndex] == '('):
            break
#     print "arg: ", text[(charIndex+1):-1]
    return text[(charIndex+1):-1]

def getIngNum(text):
    text = text.lstrip()
    assert text[:3] == "ing"
    textSplit = text.split("ing")
    return int(textSplit[1])

    # process getIng Args
def preProcessIngArgs(text):
    

    ingArg = getArgs(text)
    ingAndDesc = ingArg.split(',')
    ingNo = getIngNum(ingAndDesc[0])
    # put ingredients back into string
    ingString = ','.join(ingAndDesc[1:])
    ingString = cleanPunc(ingString)

    return ingNo, ingString

def cleanPunc(text):
    punctuationWithoutCom = ['!', '#', '"', '%', '$', "'", '&', ')', '(', '+', '*', '/', '.', ';', ':', '=', '<', '?', '>', '@', '[', ']', '\\', '_', '^', '`', '{', '}', '|', '~']
    text = ''.join(ch for ch in text if ch not in punctuationWithoutCom)

    return text

def processLabeledData(filename):
    
    ingredientMap = IngMap()
    Food.foodCount = 0
    Food.ingCount = 0    
    
    ## get instructions with original ingredients
    instrctXWithOri, ingredientMap, links = buildGraph(ingredientMap,filename)
    
    ## get standard instruction number labeled
    x, y = getXandY(filename)
    xIng, xRem, yRem = separateIngInstruct(x,y)
    xInstructNumb, yInstructNumb = getOneToOneMatch(xRem,yRem, [isGeneral])

    numberedInstruct = {}
    for i, each in enumerate(xInstructNumb):
        numberedInstruct[each] = i
    
    numberedInstrctXWithOri = {}
    
    previousInstructX = instrctXWithOri[0][0].rstrip()
    collectIng = []
    collectTag = []
    for each in instrctXWithOri:
        instrctX = each[0].rstrip()
        oriIng = each[1]
        label = oriIng[0]
        if (previousInstructX == instrctX):
            collectIng += oriIng[1]
            collectTag.append(oriIng[0])
        else:
            whichNum = numberedInstruct[previousInstructX]
            numberedInstrctXWithOri[whichNum] = (previousInstructX, collectTag, collectIng)

            previousInstructX = instrctX
            collectIng = oriIng[1]
            collectTag = [oriIng[0]]

    whichNum = numberedInstruct[previousInstructX]
    numberedInstrctXWithOri[whichNum] = (previousInstructX, collectTag, collectIng)
    
    return numberedInstrctXWithOri , ingredientMap, links