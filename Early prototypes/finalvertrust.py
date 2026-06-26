import math

class BuildingType():
    def __init__(self,_BuildingTypeName,_BuildingIdx,_BasePrice,_BaseCPS):
        self.BasePrice = _BasePrice
        self.BaseCPS = _BaseCPS

BuildingTypes = {
    "Cursor":BuildingType(15,0.1),
    "Grandma":BuildingType(100,1),
    "Farm":BuildingType(1100,8),
    "Mine":BuildingType(12000,47),
    "Factory":BuildingType(130000,260)}



class Game():
    def __init__(self):
        print()

class GameState():
    def __init__(self,_TimeElapsed,_BuildingsOwned,_UpgradesOwned,_ClickDelay):
        self.TimeElapsed = _TimeElapsed
        self.BuildingsOwned = _BuildingsOwned
        #ie [BuildingTypes["Cursor"],3]
        self.UpgradesOwned = _UpgradesOwned
        self.ClickDelay = _ClickDelay

    def CalcNextBuildingCost(self,_BuildingType):
        BuildingTypes[_BuildingType.BuildingIdx].BasePrice*(1.15**())
        return()

    def BuyBuilding(self,_PurchaseBuildingType,_NumPurchases=1):

