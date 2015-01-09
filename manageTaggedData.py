import xml.etree.ElementTree as ET


def getRoot(fileDirectory, fileName):
    return ET.parse(fileDirectory+fileName).getroot()

def getXandY(recipeFile):
    
    root = getRoot('/Users/Mick/Desktop/FoodCapstone/annotated_recipes/',recipeFile)

    # get data from xml file
    annotations = []
    originalTexts = []

    for child in root:
        # get annotations
        annotations.append(child.find('annotation').text)
        # get unique texts
        originalTexts.append(child.find('originaltext').text)

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
    
    punctuationWithoutCom = ['!', '#', '"', '%', '$', "'", '&', ')', '(', '+', '*', '/', '.', ';', ':', '=', '<', '?', '>', '@', '[', ']', '\\', '_', '^', '`', '{', '}', '|', '~']

    ingArg = getArgs(text)
    ingAndDesc = ingArg.split(',')
    ingNo = getIngNum(ingAndDesc[0])
    # put ingredients back into string
    ingString = ','.join(ingAndDesc[1:])
    ingString = ''.join(ch for ch in ingString if ch not in punctuationWithoutCom)
    return ingNo, ingString