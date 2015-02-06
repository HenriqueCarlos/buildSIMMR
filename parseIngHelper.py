from nltk.util import ngrams
from nltk import word_tokenize


#Make list of units
def getUnitList(myStem):
    unitFile = open('/Users/Mick/Desktop/FoodCapstone/buildSIMMR/units.txt')
    units = []
    for eachLine in unitFile:
        splitLine = eachLine.rstrip().split(",")
        for eachU in splitLine:
            eachU = eachU.lstrip()
            units.append(eachU)
    fromUSDA = ['cube', 'fluid', 'individual', 'block', 'mini', 'bottle', 'lb', 'breast', 'Tbsp', 'stick', 'wing', 'medallion', 'ear', 'strips', 'skin', 'rack', 'slices', 'strip', 'medium', 'thigh', 'order', 'Cup', 'jar', 'pieces', 'large', 'link', 'can', 'chop', 'patty', 'container', 'packet', 'scoop', 'bar', 'tablespoon', 'unit', 'slice', 'fillet', 'tsp', 'piece', 'package', 'fl', 'tbsp', 'serving', 'cup', 'oz', 'inch']
    # units += fromUSDA
    units = [myStem.stem(each) for each in units]
    return units

def checkNGramMatch(myStem, sentence, wordlist):
    
    tokenList = [word_tokenize(each) for each in wordlist]
    tokenList = [[myStem.stem(d) for d in each] for each in tokenList]
    maxLenToken = max([len(each) for each in tokenList])
    
    sentenceToken = word_tokenize(sentence)
    sentenceTokenList = [myStem.stem(each) for each in sentenceToken]
    
    matches = []
    allWordList = []
    
    for n in range(maxLenToken,0,-1):
        # print "thisN:", n
        thisGramSentence = [each for each in ngrams(sentenceTokenList, n)]
        # print "thisSentence:", thisGramSentence
        wordListGram = [ [e for e in ngrams(each,n)] for each in tokenList]
        # print "wordList:", wordListGram
        wordListFoundThisLevel = []
        toBeReplacedWhenFound = []
        for i in range(len(thisGramSentence)):
            
            for j in range(len(wordListGram)):
                for k in range(len(wordListGram[j])):
                        if (wordListGram[j][k] == thisGramSentence[i]):
                            if (j not in allWordList):
                                # print (thisGramSentence[i]), "at word", j  
                                matches.append((thisGramSentence[i],n,i,j,k))
                                # gramAndPos.append((n,i,j,k))
                                wordListFoundThisLevel.append(j)
                                toBeReplacedWhenFound.append((thisGramSentence[i],n,i,j,k))

        for eachMatched in toBeReplacedWhenFound:
            # print eachMatched
            ii = eachMatched[2]
            iiN = eachMatched[1]+ii
            # print sentenceTokenList[ii:iiN]
            for replaceI in range(ii,iiN):
                sentenceTokenList[replaceI] = "?"
            # replacing = " ".join(["?" for ii in range(thisLen)])
            # replaced = " ".join(list(eachMatched))

        
        allWordList += wordListFoundThisLevel
    
    return matches
#     finalRes = []
#     for eIng in tokenList:
#         found = 0
#         for eM in matches:
#             for eT in eM[0]:
#                 if eT in eIng:
# #                     print eM[0]
#                     finalRes.append(eM)
#                     found = 1
#                 if (found == 1):
#                     break
#             if (found == 1):
#                 break
                
#     return finalRes

def hasDigit(text):
    return len([c for c in text if c.isdigit()]) > 0

def removeUnitsNum(myStem, ingString, units):
    
    punctuationWithoutCom = ['!', '#', '"', '%', '$', "'", '&', ')', '(', '+', '*', '/', '.', ';', ':', '=', '<', '?', '>', '@', '[', ']', '\\', '_', '^', '`', '{', '}', '|', '~']
    textIng = word_tokenize(ingString)
    unstemmedTextIng = textIng
    textIng = [myStem.stem(eachTok) for eachTok in textIng ]
    numIng = [i for i in range(len(textIng))  if (textIng[i] not in units and not hasDigit(textIng[i]))]
    unstemmedTextIng = [ unstemmedTextIng[eachI] for eachI in numIng ]
    returnIng = " ".join(unstemmedTextIng)
    return ''.join(ch for ch in returnIng if ch not in punctuationWithoutCom).replace(",","")


def getOriginWordFromSentence(sentence, listpositions):
    
    originWord = []
    sentenceToken = word_tokenize(sentence)
    for each in listpositions:
        (n,i,j,k) = each
        originWord.append(" ".join(sentenceToken[i:i+n]))
    return originWord

def getBeforeAfterWord(sentence, listpositions):

    before = []
    after = []
    sentenceToken = word_tokenize(sentence)
    for each in listpositions:
        (n,i,j,k) = each
        if (i>0):
            before.append(sentenceToken[i-1])
        else:
            before.append("")

        if (i+n < len(sentenceToken)):
            after.append(sentenceToken[i+n])
        else:
            after.append("")
    return before, after
    
def getAllNGrams(word):
    tokenList = word_tokenize(word)
    maxN = len(tokenList)
    for n in range(1,maxN+1):
        thisNgrams = ngrams(tokenList, n)
        for eachGram in thisNgrams:
            yield eachGram