import manageTaggedData as mngTgDat
from food import Food

class IngMap:

    def __init__(self):
        self.m = {} # key - ID according to milk label, value - Food object
        self.adjList = []
        self.states = []
        self.sortedList = []
        self.originIng = {}

    def initInstructLabel(self,numInstruct):
        self.instruct = [[] for i in range(numInstruct)]


    # add Ingredients
    def addIng(self,instructIndex,ingNo, desc):
        thisFood = Food(desc,ingNo, instructIndex)
        self.m[ingNo] = thisFood
        self.adjList.append([])
#         print "addIng:", self.m.keys()
#         print "originIng: ", [ self.originIng[e].getIndex() for e in self.originIng.keys()]
    
    def modifyFood(self,instructIndex, ingNo, newIngNo, newIngDesc):
        # get old food
        oldFood = self.m[ingNo]
        # food to be modified as a produce from this sentene has link to this given sentence
        if oldFood.instructProd != instructIndex:
            self.instruct[oldFood.instructProd].append(instructIndex)

        self.m.pop(ingNo, None)
        oldFood.setFoodNo(newIngNo)
        oldFood.setName(newIngDesc)
        self.m[newIngNo] = oldFood
        self.m[newIngNo].setProcess()
        
    # get Index
    def getIndex(self,ingNo):
        return self.m[ingNo].fIndex
    
    # link a child node with list of parent nodes
    def linkIng(self,instructIndex, ingChild, ingParents):

        indexForChild = self.getIndex(ingChild)
        for eachIngParent in ingParents:
            oldFood = self.m[eachIngParent]
            if oldFood.instructProd != instructIndex:
                self.instruct[oldFood.instructProd].append(instructIndex)
                self.instruct[oldFood.instructProd] = list(set(self.instruct[oldFood.instructProd]))
            self.adjList[self.getIndex(eachIngParent)].append(indexForChild)

    def prepTopSort(self):
        self.states = [0 for each in range(len(self.adjList))]
        self.sortedList = []
        
    def topSort(self,nodeIndex):
        
        if (self.states[nodeIndex] != 0):
            return
        
        myChildren = self.adjList[nodeIndex]

        for each in myChildren:
            self.topSort(each)
        self.states[nodeIndex] = 1
        
        self.sortedList.append(nodeIndex)

    def getTopSort(self):
        self.prepTopSort()
        for eachIndex in range(len(self.states)):
            self.topSort(eachIndex)
        self.sortedList.reverse()        
        return self.sortedList

    # how many new nodes are constructed from this
    def getNumAddiNodes(self):
        return len(self.adjList) - len(self.originIng.keys())

    ## INTERPRET ##
    def interpretIng(self,text, ingRecipe, instructIndex):
        # create_ing(ing28, "1/2 cup butter, softened")

        ingNo, ingString = mngTgDat.preProcessIngArgs(text)
        self.addIng(instructIndex, ingNo, mngTgDat.cleanPunc(ingRecipe))

        self.originIng[self.getIndex(ingNo)] = self.m[ingNo]
        self.m[ingNo].composite.append(self.getIndex(ingNo))

    def interpretComb(self,text, instructIndex): 
        # combine(ingredient set ins, ingredient out, string outdesc, string manner)
        # combine({ing0, ing1}, ing2, "dough", "")

        ingArg = mngTgDat.getArgs(text)
        left = text.split('{')
        assert len(left) == 2, 'there are more than 1 {'
        right = left[1].split('}')
        assert len(right) == 2, 'there are more than 1 )'

        # get ingredient source
        setIngIn = right[0]
        setIngList = setIngIn.split(',')
        setIngListNo =  [mngTgDat.getIngNum(eachIng) for eachIng in setIngList]

        remArgs = right[1].lstrip(',')
        remArgs = remArgs.split(',')

        # create new food
        ingOutNo = mngTgDat.getIngNum(remArgs[0])
        ingOutDesc = remArgs[1]
    #     print ingOutNo,ingOutDesc
        self.addIng(instructIndex, ingOutNo,ingOutDesc)     
#         print text
        oriIndex = [self.m[eachIng].getIndex() for eachIng in setIngListNo if ((len(self.m[eachIng].composite) == 1) and (self.m[eachIng].raw))]
#         print [self.m[eachIng].composite for eachIng in setIngListNo] 

        # link the child food to new food created
        self.linkIng(instructIndex, ingOutNo, setIngListNo)

        for ing in setIngListNo:
            self.m[ingOutNo].composite.append(self.m[ing].composite)
        
        if (oriIndex):
            return (text, oriIndex)
        
    def interpretSep(self,text ,instructIndex):
        # separate(ing0, ing1, "raisins", ing2, "peanuts and almonds", "")

        ingArg = mngTgDat.getArgs(text)
        ingArgs = ingArg.split(",")

        # ingredientNum of the source
        ing0No = mngTgDat.getIngNum(ingArgs[0])

        # build new ingredients
        ing1No = mngTgDat.getIngNum(ingArgs[1])
        ing1Des = ingArgs[2]
        self.addIng(instructIndex, ing1No,ing1Des)  

        ing2No = mngTgDat.getIngNum(ingArgs[3])
        ing2Des = ingArgs[4]
        self.addIng(instructIndex, ing2No,ing2Des)  

        # from source ing0 separated (direct edges) to two others 1 and 2
        self.linkIng(instructIndex, ing1No, [ing0No])
        self.linkIng(instructIndex, ing2No, [ing0No])

        if self.m[ing0No].getIndex() in self.originIng and self.m[ing0No].raw:
            return (text, [self.m[ing0No].getIndex()] )



    def interpretCut(self,text,instructIndex):
        # cut(ingredient in, tool t, ingredient out, string outdesc, string manner)

        ingArg = mngTgDat.getArgs(text)
        ingArgs = ingArg.split(",")

        ingNoExist = mngTgDat.getIngNum(ingArgs[0])
        ingNoTransformed = mngTgDat.getIngNum(ingArgs[2])
        desTransformed = ingArgs[3]
        
        retVal = []
        if ((self.m[ingNoExist].getIndex() in self.originIng) and (self.m[ingNoExist].raw)):
            retVal = (text, [self.m[ingNoExist].getIndex()] )
        self.modifyFood(instructIndex, ingNoExist, ingNoTransformed, desTransformed)    
        if (retVal):
            return retVal
   
    def interpretMix(self,text,instructIndex):

        # mixing here does not add more ingredients (just a manner of cooking)
        # interchange old ingredient number with a new one
        # mix(ingredient in, tool t, ingredient out, string outdesc, string manner)


        ingArg = mngTgDat.getArgs(text)
        ingArgs = ingArg.split(",")

        ingNoExist = mngTgDat.getIngNum(ingArgs[0])
        ingNoTransformed = mngTgDat.getIngNum(ingArgs[2])
        desTransformed = ingArgs[3]

        retVal = []      
        if ((self.m[ingNoExist].getIndex() in self.originIng) and (self.m[ingNoExist].raw)):
            retVal = (text, [self.m[ingNoExist].getIndex()] )
        self.modifyFood(instructIndex, ingNoExist, ingNoTransformed, desTransformed)    
        if (retVal):
            return retVal
   
        
    def interpretCook(self,text,instructIndex):
        # cook(ingredient in, tool t, ingredient out, string outdesc, string manner)
        # cook(ing0, t0, ing1, "hot water", "boil")


        ingArg = mngTgDat.getArgs(text)
        ingArgs = ingArg.split(",")

        ingNoExist = mngTgDat.getIngNum(ingArgs[0])
        ingNoTransformed = mngTgDat.getIngNum(ingArgs[2])
        desTransformed = ingArgs[3]

        retVal = []      
        if ((self.m[ingNoExist].getIndex() in self.originIng) and (self.m[ingNoExist].raw)):
            retVal = (text, [self.m[ingNoExist].getIndex()] )
        self.modifyFood(instructIndex, ingNoExist, ingNoTransformed, desTransformed)    
        if (retVal):
            return retVal
        
    def interpretDo(self,text,instructIndex):

        # do(ing0, , ing1, "dumplings", "fold into dumpling shapes")

        ingArg = mngTgDat.getArgs(text)
        ingArgs = ingArg.split(",")

        ingNoExist = mngTgDat.getIngNum(ingArgs[0])
        ingNoTransformed = mngTgDat.getIngNum(ingArgs[2])
        desTransformed = ingArgs[3]

        retVal = []      
        if ((self.m[ingNoExist].getIndex() in self.originIng) and (self.m[ingNoExist].raw)):
            retVal = (text, [self.m[ingNoExist].getIndex()] )
        self.modifyFood(instructIndex, ingNoExist, ingNoTransformed, desTransformed)    
        if (retVal):
            return retVal
    
    def interpretPut(self,text,instructIndex):
        # put({ing9}, t0)
        if ("{" in text):
            ingArg = mngTgDat.getArgs(text)
            left = text.split('{')
            assert len(left) == 2, 'there are more than 1 {'
            right = left[1].split('}')
            assert len(right) == 2, 'there are more than 1 )'

            # get ingredient list that are put
            setIngIn = right[0]
            setIngList = setIngIn.split(',')
            setIngListNo =  [mngTgDat.getIngNum(eachIng) for eachIng in setIngList]

            retValIng = []      
            for ingNoExist in setIngListNo:
                if ((self.m[ingNoExist].getIndex() in self.originIng) and (self.m[ingNoExist].raw)):
                    retValIng.append(self.m[ingNoExist].getIndex())

            for ingNoExist in setIngListNo:
                self.modifyFood(instructIndex, ingNoExist, ingNoExist, self.m[ingNoExist].getName())

            if (retValIng):
                return (text,retValIng)
        else:
            ingArg = mngTgDat.getArgs(text)
            ingArgs = ingArg.split(",")

            ingNoExist = mngTgDat.getIngNum(ingArgs[0])

            retVal = []      
            if ((self.m[ingNoExist].getIndex() in self.originIng) and (self.m[ingNoExist].raw)):
                retVal = (text, [self.m[ingNoExist].getIndex()] )
            self.modifyFood(instructIndex, ingNoExist, ingNoExist, self.m[ingNoExist].getName())
            if (retVal):
                return retVal
       