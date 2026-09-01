import math
import random
import time

import Toolbelt

Goal = int(input("What should the cookies baked end goal amount be?"))

#FOCUS ON PRUNING FIRST, Evaluation mechanism later bro

class BuildingType():
    def __init__(self,_Name,_BasePrice,_BaseCPS):
        self.Name = _Name
        self.BasePrice = _BasePrice
        self.BaseCPS = _BaseCPS

Cursor = BuildingType("Cursor",15,0.1)
Grandma = BuildingType("Grandma",100,1)
Farm = BuildingType("Farm",1100,8)
Mine = BuildingType("Mine",1200,47)
Factory = BuildingType("Factory",13000,260)
BuildingTypes = [Cursor,Grandma,Farm,Mine,Factory] #These are all of the types that exist within the game, most of them have a base price above the goal amount though and as such I use "BuildingTypesWithinScope" for those instead

class Combination():
    def __init__(self,_ID):
        self.CookiesBaked = 0
        self.BuildingTypesWithinScope = []
        Counter = 0
        while BuildingTypes[Counter].BasePrice < Goal:
            self.BuildingTypesWithinScope.append(BuildingTypes[Counter])
            Counter += 1
        self.ActionList = []

    def Calc_Gap(self):
        return(Goal - self.CookiesBaked)

    def Calc_MaxBuyableOfBuildingType(self,_BuildingType):
        return(math.floor(math.log((self.Calc_Gap()*0.15/_BuildingType.BasePrice)+1)))
    
    def Buy(self,_BuildingType,_PurchaseAmount):
        self.ActionList.append((_PurchaseAmount,_BuildingType))
        self.CookiesBaked += _BuildingType.BasePrice*((1.15**_PurchaseAmount)-1)/0.15

    def Buy_MaxAmtofBuildingType(self,_BuildingType):
        self.Buy(_BuildingType,self.Calc_MaxBuyableOfBuildingType(_BuildingType))

    def MaximallyBuy_FocusBuildingType(self,_BuildingType):
        ID = self.BuildingTypesWithinScope.index(_BuildingType)
        Counter = 0
        while self.Calc_Gap() > self.BuildingTypesWithinScope[ID+Counter+1].BasePrice:
            self.Buy_MaxAmtofBuildingType(self.BuildingTypesWithinScope[ID+Counter])

#Start by finding the corner of the pareto frontier, take one combination and make it have a maximal amount of purchases of a certain building type
RootCombination = Combination(0)

RootCombination.Calc_MaxBuyableOfBuildingType(RootCombination.BuildingTypesWithinScope[-1])