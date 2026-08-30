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

class BuildingType():
    def __init__(self,_Name,_Value,_CPS,_AmountOwned=0):
        self.Name = _Name
        self.Value = _Value
        self.CPS = _CPS
        self.AmountOwned = _AmountOwned

Template_BuildingTypes = [BuildingType("Cursor",15,0.1)]

class GameState():
    def __init__(self,_FramesPassed=0,_Bank=0,_CookiesBaked=0,_Buildings=Template_BuildingTypes,_UpgradeVault=[]):
        self.FramesPassed = _FramesPassed
        self.Bank = _Bank
        self.CookiesBaked = _CookiesBaked
        self.Buildings = _Buildings
        self.UpgradeVault = _UpgradeVault
        self.NextFrameActions = ["Wait"]

    def RemoveFromUpgradeVault(self,_Upgrade):
        self.UpgradeVault.pop(UpgradeVault.index(_Upgrade.Name))

    def Buy_Upgrade(self,_UpgradePurchase):
        self.Bank -= _UpgradePurchase.Cost
        RemoveFromUpgradeVault(_UpgradePurchase)

    def Calc_BuildingPurchaseCost(_BuildingTypeObj,_PurchaseQuantity=1):
        Purchase_Cost = 0
        for x in range(_PurchaseQuantity):
            Purchase_Cost += _BuildingTypeObj.Value * 1.15 ** (x)
        return(Purchase_Cost)

    def Buy_Building(self,_BuildingTypeObj,_PurchaseQuantity=1):
        if Calc_BuildingPurchaseCost(_BuildingTypeObj,_PurchaseQuantity) <= self.Bank:
            self.Bank -= Purchase_Cost
            _BuildingTypeObj.AmountOwned += _PurchaseQuantity

    