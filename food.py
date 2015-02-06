#Ingredient map
class Food:
    
    # count food created
    # also serve as index for the node
    foodCount = 0
    ingCount = 0
    def __init__(self,fNm,fNo,instructIndex):
        self.fNm = self.normalizeFoodName(fNm)
        self.foodNo = fNo
        self.fIndex = Food.foodCount
        Food.foodCount += 1
        self.composite = []
        self.raw = True
        self.instructProd = instructIndex

    # set name and number
    # index with respect to the adjacency list however cannot be changed
    def setName(self, newFoodName):
        self.fNm = self.normalizeFoodName(newFoodName)
    
    def setFoodNo(self, newFoodNo):
        self.fNm = newFoodNo
    
    def setProcess(self):
        self.raw = False

    def getName(self):
        return self.fNm
    def getNo(self):
        return self.foodNo
    def getIndex(self):
        return self.fIndex
    
    def __str__(self):
        return self.fNm

#         return str(self.foodNo)+":"+self.fNm
        
    def normalizeFoodName(self,foodName):
        # To be implemented
        foodName = foodName.lstrip()
        if (foodName[-1] != '\"'):
            foodName += '\"';
        if (foodName[0] != '\"'):
            foodName = '\"'+foodName
        
        return foodName
    
    def printComposite(self, comp, ingMap, depth):
        
        if len(comp) != 0:
            if (type(comp[0]) == type([])):
                for d in comp:
                    self.printComposite(d, ingMap, depth+1)
                print ""
            else:
                print comp[0],
         
   