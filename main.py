import math
import random
import time

# import Toolbelt

Goal = float(input("What should the cookies baked end goal amount be?"))
while Goal <= 15:
    print("Choose a higher goal, at this level nothing can be afforded before the goal is reached and the simulation concluded")
    Goal = float(input())

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

    def Calc_BuyCost(self,_NumBuildings=1):#Accounts for scenarios in which buildings are alr owned
        return(self.BulkBuyFormula(self.AmountOwned + _NumBuildings)-self.Value) 

    def Calc_SellPrice(self,_NumBuildings):
        return(self.Value - self.BulkBuyFormula(self.AmountOwned-_NumBuildings))

    def Calc_MaxBuyable(self,_Gap):
        MaxBuyable = 0
        while self.Calc_BuyCost(MaxBuyable+1) < _Gap:
            MaxBuyable += 1
        return(MaxBuyable)
        # return(math.floor(math.log((_Gap*0.15/(self.BasePrice*((1.15**self.AmountOwned)-1)))+1,1.15)))

    def copy(self):
        # Return a new BuildingType with the same attribute values
        return BuildingType(self.Name, self.BasePrice, self.BaseCPS, self.AmountOwned)


Cursor = BuildingType("Cursor",15,0.1)
Grandma = BuildingType("Grandma",100,1)
Farm = BuildingType("Farm",1100,8)
Mine = BuildingType("Mine",1200,47)
Factory = BuildingType("Factory",13000,260)
BuildingTypes = [Cursor,Grandma,Farm,Mine,Factory] #These are all of the types that exist within the game, most of them have a base price above the goal amount though and as such I use "BuildingTypesWithinScope" for those instead

class Combination():
    def __init__(self,_ID):
        self.ID = _ID
        self.CookiesBaked = 0
        self.BuildingTypesWithinScope = []
        Counter = 0
        while BuildingTypes[Counter].BasePrice < Goal:
            self.BuildingTypesWithinScope.append(BuildingTypes[Counter].copy())
            Counter += 1
            if Counter == len(BuildingTypes):
                break
        self.AllocationList = []
        self.OmittedType = None
        
        
    @property
    def Gap(self):
        return(Goal - self.CookiesBaked - 0.0001) #fah If the cost of a purchase would put the sum total purchases cost to the same level as the goal, then there's no point considering it since the very frame the purchase becomes unlockable the simulation would've ended.
    
    def AddPurchase(self,_BuildingTypeID,_PurchaseAmount):
        self.CookiesBaked += self.BuildingTypesWithinScope[_BuildingTypeID].Calc_BuyCost(_PurchaseAmount)
        self.BuildingTypesWithinScope[_BuildingTypeID].AmountOwned += _PurchaseAmount

    def AddMaxBuildingType(self,_BuildingTypeID):
        self.AddPurchase(_BuildingTypeID,self.BuildingTypesWithinScope[_BuildingTypeID].Calc_MaxBuyable(self.Gap))

    def AddMaxPurchases(self):
        Counter = 0
        while self.Gap > self.BuildingTypesWithinScope[Counter].BasePrice:#shouldn't be base price but it doesn't matter because this func is only ever called to find corners, meaning no buildings will be owned 
            self.AddMaxBuildingType(Counter)
            Counter += 1
            if Counter == len(self.BuildingTypesWithinScope):
                break
    
    def OmitPurchase(self,_BuildingTypeID,_OmittedAmt):
        self.CookiesBaked -= self.BuildingTypesWithinScope[_BuildingTypeID].Calc_SellPrice(_OmittedAmt)
        self.BuildingTypesWithinScope[_BuildingTypeID].AmountOwned -= _OmittedAmt

    def PrintDetails(self):
        print(self.CookiesBaked)
        print(self.Gap)
        for x in range(len(self.BuildingTypesWithinScope)):
            print(f"{self.BuildingTypesWithinScope[x].AmountOwned} {self.BuildingTypesWithinScope[x].Name}")
        print("===============================")


    def Dupe(self):
        New_Comb = Combination(self.ID + 1)
        New_Comb.CookiesBaked = self.CookiesBaked
        New_Comb.BuildingTypesWithinScope = []
        for x in range(len(self.BuildingTypesWithinScope)):
            New_Comb.BuildingTypesWithinScope.append(self.BuildingTypesWithinScope[x].copy())
        return(New_Comb)

RootCombination = Combination(0) 
RootCombination.AddMaxPurchases() #830 iis the sweeet spot or smth
BuildingPurchasesCombinations = [RootCombination] #The array containing all the combinations of building purchases affordable within the scope of the goal

DuplicateCount = 0
Curr_Comb = BuildingPurchasesCombinations[0]
for w in range(len(Curr_Comb.BuildingTypesWithinScope)):
    other_indices = [idx for idx in range(len(Curr_Comb.BuildingTypesWithinScope)) if idx != w]
    for x in range(1, Curr_Comb.BuildingTypesWithinScope[w].AmountOwned):
        for orig_idx in other_indices:
            if Curr_Comb.BuildingTypesWithinScope[w].Calc_SellPrice(x) > Curr_Comb.BuildingTypesWithinScope[orig_idx].Calc_BuyCost():
                New_Comb = Curr_Comb.Dupe()
                New_Comb.OmitPurchase(w, x)
                New_Comb.AddMaxBuildingType(orig_idx)   # now correct
                BuildingPurchasesCombinations.append(New_Comb)
                New_Comb.PrintDetails()
                