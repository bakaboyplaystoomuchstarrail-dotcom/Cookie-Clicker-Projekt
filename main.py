import math
import random
import time

# import Toolbelt

Goal = float(input("What should the cookies baked end goal amount be?"))
while Goal <= 15:
    print("Choose a higher goal, at this level nothing can be afforded before the goal is reached and the simulation concluded")
    Goal = float(input())

class BuildingType():
    def __init__(self,_Name,_BasePrice,_BaseCPS):
        self.Name = _Name
        self.BasePrice = _BasePrice
        self.BaseCPS = _BaseCPS

    def BulkBuyFormula(self,_NumBuildings): 
        return(self.BasePrice*((1.15**_NumBuildings)-1)/0.15)

    def Calc_BuyCost(self,_NumCurrOwned=0,_PurchaseAmt=1):#Accounts for scenarios in which buildings are alr owned
        return(self.BulkBuyFormula(_NumCurrOwned + _PurchaseAmt)-self.BulkBuyFormula(_NumCurrOwned)) 

    def Calc_SellPrice(self,_NumCurrOwned,_SellAmt=1):
        return(self.BulkBuyFormula(_NumCurrOwned) - self.BulkBuyFormula(_NumCurrOwned - _SellAmt))

    def Calc_MaxBuyable(self,_Gap,_NumCurrOwned=0):
        MaxBuyable = 0
        while self.Calc_BuyCost(_NumCurrOwned + MaxBuyable,1) < _Gap:
            MaxBuyable += 1
        return(MaxBuyable)
        # return(math.floor(math.log((_Gap*0.15/(self.BasePrice*((1.15**self.AmountOwned)-1)))+1,1.15)))


Cursor = BuildingType("Cursor",15,0.1)
Grandma = BuildingType("Grandma",100,1)
Farm = BuildingType("Farm",1100,8)
Mine = BuildingType("Mine",1200,47)
Factory = BuildingType("Factory",13000,260)
BuildingTypes = [Cursor,Grandma,Farm,Mine,Factory] #These are all of the types that exist within the game, most of them have a base price above the goal amount though and as such I use "BuildingTypesWithinScope" for those instead

Counter = 0
while BuildingTypes[Counter].BasePrice < Goal:
            Counter += 1
            if Counter == len(BuildingTypes):
                break
BuildingTypesWithinScope = BuildingTypes[:Counter]

class Combination():
    def __init__(self,_ID,_BuildingInventories=[]):
        self.ID = _ID
        self.CookiesBaked = 0
        self.BuildingInventories = _BuildingInventories
        self.AllocationList = []
        self.OmittedType = None
        
    @property
    def Gap(self):
        return(Goal - self.CookiesBaked)
    
    def AddPurchase(self,_BuildingTypeID,_PurchaseAmount=1,_BuildingTypesWithinScope=BuildingTypesWithinScope):
        self.CookiesBaked += _BuildingTypesWithinScope[_BuildingTypeID].Calc_BuyCost(self.BuildingInventories[_BuildingTypeID],_PurchaseAmount)
        self.BuildingInventories[_BuildingTypeID] += _PurchaseAmount

    def AddMaxBuildingType(self,_BuildingTypeID,_BuildingTypesWithinScope=BuildingTypesWithinScope):
        self.AddPurchase(_BuildingTypeID,_BuildingTypesWithinScope[_BuildingTypeID].Calc_MaxBuyable(self.Gap,self.BuildingInventories[_BuildingTypeID]))

    def AddMaxPurchases(self,_BuildingTypesWithinScope=BuildingTypesWithinScope):
        Counter = 0
        while self.Gap => _BuildingTypesWithinScope[Counter].BasePrice:
            self.AddMaxBuildingType(Counter)
            Counter += 1
            if Counter == len(_BuildingTypesWithinScope):
                break
    
    def OmitPurchase(self,_BuildingTypeID,_OmittedAmt,_BuildingTypesWithinScope=BuildingTypesWithinScope):
        self.CookiesBaked -= _BuildingTypesWithinScope[_BuildingTypeID].Calc_SellPrice(self.BuildingInventories[_BuildingTypeID],_OmittedAmt)
        self.BuildingInventories[_BuildingTypeID] -= _OmittedAmt

    def PrintDetails(self,_BuildingTypesWithinScope=BuildingTypesWithinScope):
        print(self.CookiesBaked)
        print(self.Gap)
        for x in range(len(self.BuildingInventories)):
            print(f"{self.BuildingInventories[x]} {_BuildingTypesWithinScope[x].Name}")
        print("===============================")


    def Dupe(self):
        New_Comb = Combination(self.ID + 1)
        New_Comb.CookiesBaked = self.CookiesBaked
        New_Comb.BuildingInventories = self.BuildingInventories.copy()
        return(New_Comb)

RootCombination = Combination(0,[0 for _ in range(len(BuildingTypesWithinScope))]) 
RootCombination.AddMaxPurchases() #830 iis the sweeet spot or smth
BuildingPurchasesCombinations = [RootCombination] 

DuplicateCount = 0
Curr_Comb = BuildingPurchasesCombinations[0]
for w in range(len(BuildingTypesWithinScope)):#omitting building type w
    for x in range(1, Curr_Comb.BuildingInventories[w]+1):#omitting each of the purchases of that building type
        for i in range(w+1,len(BuildingTypesWithinScope)):
            if BuildingTypesWithinScope[w].Calc_SellPrice(Curr_Comb.BuildingInventories[w],x) > BuildingTypesWithinScope[i].Calc_BuyCost(Curr_Comb.BuildingInventories[i]):
                New_Comb = Curr_Comb.Dupe()
                New_Comb.OmitPurchase(w, x)
                New_Comb.AddMaxBuildingType(i) 
                BuildingPurchasesCombinations.append(New_Comb)
                New_Comb.PrintDetails()
                