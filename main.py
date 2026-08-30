import math
import random
import time

import Toolbelt

BuildingTypesRawInfo = [
    ("Cursor",15,0.1),
    ("Grandma",100,1),
    ("Farm",1100,8),
    ("Mine",12000,47),
    ("Factory",130000,260)]

class BuildingType():
    def __init__(self,_Name,_BaseCost,_BaseCPS):
        self.Name = _Name
        self.BaseCost = _BaseCost
        self.BaseCPS = _BaseCPS

BuildingTypes = Toolbelt.MassConvToObjs(BuildingTypesRawInfo,BuildingType)


class Purchase():
    def __init__(self,_ID,_Name,_Type,_Cost=None):
        self.ID = _ID
        self.Name = _Name
        self.Type = _Type
        self.Cost = _Cost

class GameState():
    def __init__(self,_Clock=0,_Bank=0,_Baked=0,_Upgrades=[],_Buildings=[]):
        self.Clock = _Clock
        self.Bank = _Bank
        self.Baked = _Baked
        self.Upgrades = _Upgrades
        self.Buildings = _Buildings

    def Buy(self,_Purchase):
        self.Bank -= _Purchase.Cost

Root_GameState = GameState()



