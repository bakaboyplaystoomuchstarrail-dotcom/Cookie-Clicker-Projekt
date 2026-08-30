import math
import random
import time

import Toolbelt

class UpgradePurchase():
    def __init__(self,_Name,_BuildingType,_Cost,_UnlockBuildingAmount=None):
        self.Name = _Name
        self.BuildingType = _BuildingType
        self.Cost = _Cost
        self.UnlockBuildingAmount = _UnlockBuildingAmount

class GameState():
    def __init__(self,_FramesPassed=0,_Bank=0,_CookiesBaked=0,_Buildings=[],_UpgradeVault=[]):
        self.FramesPassed = _FramesPassed
        self.Bank = _Bank
        self.CookiesBaked = _CookiesBaked
        self.Buildings = _Buildings
        self.UpgradeVault = _UpgradeVault

    def RemoveFromUpgradeVault(self,_Upgrade):
        self.UpgradeVault.pop(UpgradeVault.index(_Upgrade.Name))

    def Buy_Upgrade(self,_UpgradePurchase):
        self.Bank -= _UpgradePurchase.Cost
        RemoveFromUpgradeVault(_UpgradePurchase)