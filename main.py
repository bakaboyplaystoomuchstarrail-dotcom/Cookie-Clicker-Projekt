import math
import random
import time

# import Toolbelt

Goal = float(input("What should the cookies baked end goal amount be?"))

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
            if Counter == len(BuildingTypes):
                break
        self.ActionList = []

    def Calc_Gap(self):
        return(Goal - self.CookiesBaked - 0.0001) #If the cost of a purchase would put the sum total purchases cost to the same level as the goal, then there's no point considering it since the very frame the purchase becomes unlockable the simulation would've ended.

    def Calc_MaxBuyableOfBuildingType(self,_BuildingType):
        return(math.floor(math.log((self.Calc_Gap()*0.15/_BuildingType.BasePrice)+1,1.15)))
    
    def Buy(self,_BuildingType,_PurchaseAmount):
        self.ActionList.append((_PurchaseAmount,_BuildingType.Name))
        self.CookiesBaked += _BuildingType.BasePrice*((1.15**_PurchaseAmount)-1)/0.15

    def Buy_MaxAmtOfBuildingType(self,_BuildingType):
        self.Buy(_BuildingType,self.Calc_MaxBuyableOfBuildingType(_BuildingType))

    def MaximallyBuy(self,_PrimaryFocusBuildingType):
        ID = self.BuildingTypesWithinScope.index(_PrimaryFocusBuildingType)
        circular_arr = self.BuildingTypesWithinScope[ID:] + self.BuildingTypesWithinScope[:ID]
        Counter = 0
        while self.Calc_Gap() > circular_arr[Counter].BasePrice:
            self.Buy_MaxAmtOfBuildingType(circular_arr[Counter])
            Counter += 1
            if Counter == len(circular_arr):
                break

RootCombination = Combination(0)
