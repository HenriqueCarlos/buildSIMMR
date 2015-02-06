import parseIngHelper as prsIngHp
import manageTaggedData as mngTgDat
from tabulate import tabulate


def buildGraph(ingredientMap,recipeFile):
    
    instrctXWithOri = []
    verbose = False

    root = mngTgDat.getRoot('/Users/Mick/Desktop/FoodCapstone/annotated_recipes/',recipeFile)


    # get data from xml file
    annotations = []
    originalTexts = {}
    allTexts = []
    dictTextEdge = {}

    for child in root:
        
        # get annotations

        ann = child.find('annotation').text.rstrip()
        ann = ann.encode('ascii','ignore')
        ann = ann.decode('unicode_escape').encode('ascii','ignore')
        annotations.append(ann)

        # get unique texts
        oriTxt = child.find('originaltext').text.rstrip()
        oriTxt = oriTxt.encode('ascii','ignore')
        oriTxt = oriTxt.decode('unicode_escape').encode('ascii','ignore')

        allTexts.append(oriTxt)
        
        if verbose:
            print child.find('annotation').text

    xIng, xRem, yRem = mngTgDat.separateIngInstruct(allTexts,annotations)
    
    uniqText = []
    allIngs = []
    i = 0
    while mngTgDat.isIng(annotations[i]):        
        allIngs.append(allTexts[i])
        uniqText.append(allTexts[i])
        i += 1

    for eachInstruct in xRem:
        if not eachInstruct in originalTexts:
            originalTexts[eachInstruct] = len(originalTexts)
            uniqText.append(eachInstruct)

    ingredientMap.initInstructLabel(len(originalTexts)+len(allIngs))
    # parse the data

    for i, eachAn in enumerate(annotations):

        # number of instruction
        if mngTgDat.isIng(eachAn):
            if allTexts[i] in allIngs:
                # check if ing in milk is the same as that in the recipe
                # ingArg = mngTgDat.getArgs(eachAn)
                # ingAndDesc = ingArg.split(',')
                # ingString = ','.join(ingAndDesc[1:])
                # print ingString.rstrip().lstrip().rstrip('"').lstrip('"'), allTexts[i].rstrip().lstrip()
                # if ingString.rstrip().lstrip().rstrip('"').lstrip('"').lower() != allTexts[i].rstrip().lstrip().lower():
                #     askOk = input("not the same")
                instructIndex = allIngs.index(allTexts[i])
                allIngs[instructIndex] += "used"
        elif allTexts[i] in originalTexts:
            instructIndex = originalTexts[allTexts[i]] + len(xIng)

        if mngTgDat.isIng(eachAn):
            if verbose:
                print "ing", eachAn

            retVal = ingredientMap.interpretIng(eachAn,allTexts[i],instructIndex)
            if (retVal):
                instrctXWithOri.append((allTexts[i], retVal))

        elif mngTgDat.isComb(eachAn):
            if verbose:
                print "comb", eachAn
            retVal = ingredientMap.interpretComb(eachAn,instructIndex)
            if (retVal):
                instrctXWithOri.append((allTexts[i], retVal))
            else:
                print "SPECIAL#"+str(originalTexts[allTexts[i]]),  allTexts[i]


            # global countCombTags
            # countCombTags += 1


        elif mngTgDat.isMix(eachAn):
            if verbose:
                print "mix", eachAn
            retVal = ingredientMap.interpretMix(eachAn,instructIndex)
            if (retVal):
                instrctXWithOri.append((allTexts[i], retVal))
                
        elif mngTgDat.isCut(eachAn):
            if verbose:
                print "cut", eachAn
            retVal = ingredientMap.interpretCut(eachAn,instructIndex)
            if (retVal):
                instrctXWithOri.append((allTexts[i], retVal))
                
        elif mngTgDat.isDo(eachAn):
            if verbose:
                print "do", eachAn
            retVal = ingredientMap.interpretDo(eachAn,instructIndex)
            if (retVal):
                instrctXWithOri.append((allTexts[i], retVal))
                
        elif mngTgDat.isCut(eachAn):
            if verbose:
                print "cut", eachAn
            retVal = ingredientMap.interpretCut(eachAn,instructIndex)
            if (retVal):
                instrctXWithOri.append((allTexts[i], retVal))
                
        elif mngTgDat.isCook(eachAn):
            if verbose:
                print "cook", eachAn
            retVal = ingredientMap.interpretCook(eachAn,instructIndex)
            if (retVal):
                instrctXWithOri.append((allTexts[i], retVal))
        
        elif mngTgDat.isPut(eachAn):
            if verbose:
                print "put", eachAn
            retVal = ingredientMap.interpretPut(eachAn,instructIndex)
            if (retVal):
                instrctXWithOri.append((allTexts[i], retVal))
                
        elif mngTgDat.isSep(eachAn):
            if verbose:
                print "separate", eachAn
            # global countSepTags
            # countSepTags += 1
            retVal = ingredientMap.interpretSep(eachAn,instructIndex)
            if (retVal):
                instrctXWithOri.append((allTexts[i], retVal))
    

    for i in range(len(xIng)):
        thisLink = ingredientMap.instruct[i]
        if len(thisLink) > 1:
            useFirst = min(thisLink)
            ingredientMap.instruct[i] = [useFirst]
            newList = [l for l in thisLink if l != useFirst]
            ingredientMap.instruct[useFirst] += newList

    links = []
    for i, linkForward in enumerate(ingredientMap.instruct):
        ingredientMap.instruct[i] = list(set(linkForward))
        isIngredient = 1
        if i < len(xIng):
            isIngredient = -1
        links.append((isIngredient*i,uniqText[i],ingredientMap.instruct[i]))
        # print "#"+str(i),uniqText[i], ingredientMap.instruct[i]
            
    return instrctXWithOri, ingredientMap, links

def displayGraph(ingredientMap):
    # Display graph
    # list of foods
    foodNodes = ingredientMap.m.values()
    # table for display
    numNodeComb = 0
    numNodeSep = 0
    displayTable = [ [row,"nameFood",[]] for row in range(len(foodNodes)) ]
    for eachFood in foodNodes:
        displayTable[eachFood.getIndex()][1] = eachFood.getName()
    for i,each in enumerate(ingredientMap.adjList):
        stringChild = [str(eachChild) for eachChild in each ]
        if (len(stringChild) > 1):
            numNodeSep +=1
        elif (len(stringChild) == 1):
            numNodeComb += 1
        stringChild = ",".join(stringChild)
        displayTable[i][2] = stringChild
    # global countComb, countSep
    # countComb += numNodeComb
    # countSep += numNodeSep
        
    print tabulate(displayTable, headers=["node-id","node-form", "child-id"])
    
#     originalTextsWithEdge = []
#     for each in originalTexts:
#         if each in dictTextEdge.keys():
#             originalTextsWithEdge.append("\nEDGE:"+each +'\n'+ str(dictTextEdge[each])+"\n")
#         else:
#             originalTextsWithEdge.append(each)
    
     
    