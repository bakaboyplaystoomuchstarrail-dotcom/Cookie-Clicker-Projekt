import math
import random
import time

# import Toolbelt

Goal = float(input("What should the cookies baked end goal amount be?"))

#FOCUS ON PRUNING FIRST, Evaluation mechanism later bro

class BuildingType():
    def __init__(self,_Name,_BasePrice,_BaseCPS,_AmountOwned=0):
        self.Name = _Name
        self.BasePrice = _BasePrice
        self.BaseCPS = _BaseCPS
        self.AmountOwned = _AmountOwned

    def BulkBuyFormula(self,_NumBuildings): 
        return(self.BasePrice*((1.15**_NumBuildings)-1)/0.15)

    @property
    def Value(self):
        return(self.BulkBuyFormula(self.AmountOwned))

    def Calc_BuyCost(self,_NumBuildings):#Accounts for scenarios in which buildings are alr owned
        return(self.BulkBuyFormula(_NumBuildings)-self.Value) 

    def Calc_SellPrice(self,_NumBuildings):
        return(self.Value - self.BulkBuyFormula(self.AmountOwned-_NumBuildings))

    def Calc_MaxBuyable(self,_Gap):
            return(math.floor(math.log((_Gap*0.15/self.BasePrice)+1,1.15)))


Cursor = BuildingType("Cursor",15,0.1)
Grandma = BuildingType("Grandma",100,1)
Farm = BuildingType("Farm",1100,8)
Mine = BuildingType("Mine",1200,47)
Factory = BuildingType("Factory",13000,260)
BuildingTypes = [Cursor,Grandma,Farm,Mine,Factory] #These are all of the types that exist within the game, most of them have a base price above the goal amount though and as such I use "BuildingTypesWithinScope" for those instead

CombinationIDIncrementer = 0
class Combination():
    def __init__(self,_ID):
        self.ID = _ID
        self.CookiesBaked = 0
        self.BuildingTypesWithinScope = []
        Counter = 0
        while BuildingTypes[Counter].BasePrice < Goal:
            self.BuildingTypesWithinScope.append(BuildingTypes[Counter])
            Counter += 1
            if Counter == len(BuildingTypes):
                break
        
        
    @property
    def Gap(self):
        return(Goal - self.CookiesBaked - 0.0001) #fah If the cost of a purchase would put the sum total purchases cost to the same level as the goal, then there's no point considering it since the very frame the purchase becomes unlockable the simulation would've ended.
    
    def AddPurchase(self,_BuildingType,_PurchaseAmount):
        _BuildingType.AmountOwned += 1
        self.CookiesBaked += _BuildingType.Calc_BuyCost(_PurchaseAmount)

    def AddMaxBuildingType(self,_BuildingType):
        self.AddPurchase(_BuildingType,_BuildingType.Calc_MaxBuyable(self.Gap))

    def AddMaxPurchases(self,_PrimaryFocusBuildingType=BuildingTypes[0]):
        FocusedTypeID = self.BuildingTypesWithinScope.index(_PrimaryFocusBuildingType)
        LoopedTypesWithinScope = self.BuildingTypesWithinScope[FocusedTypeID:] + self.BuildingTypesWithinScope[:FocusedTypeID]
        Counter = 0
        while self.Gap > LoopedTypesWithinScope[Counter].BasePrice:#shouldn't be base price but it doesn't matter because this func is only ever called to find corners, meaning no buildings will be owned 
            self.AddMaxBuildingType(LoopedTypesWithinScope[Counter])
            Counter += 1
            if Counter == len(LoopedTypesWithinScope):
                break
    
    def DupeCombination(self,_CombinationIDIncrementer=CombinationIDIncrementer):
        _CombinationIDIncrementer += 1
        New_Comb = Combination(_CombinationIDIncrementer)
        New_Comb.CookiesBaked = self.CookiesBaked
        New_Comb.BuildingTypesWithinScope = self.BuildingTypesWithinScope
        return(New_Comb)




RootCombination = Combination(CombinationIDIncrementer) 
RootCombination.AddMaxPurchases(BuildingTypes[0])
C = [RootCombination] #The array containing all the combinations of building purchases affordable within the scope of the goal

print(RootCombination.CookiesBaked)
print(RootCombination.Gap)
for x in range(len(RootCombination.BuildingTypesWithinScope)):
    print(f"{RootCombination.BuildingTypesWithinScope[x].AmountOwned} {RootCombination.BuildingTypesWithinScope[x].Name}")
