import math
import random
import time

import Toolbelt

GoalTypes = {
    "Time to reach fixed endpoint":"placeholder",
    "CPF":"placeholder",
    "Cookies Produced in fixed time slot":"placeholder"}

Goal = 100

class UpgradePurchase():
    def __init__(self,_Name,_BuildingType,_Cost,UpgradeFactor,_UnlockBuildingAmount=None):
        self.Name = _Name
        self.BuildingType = _BuildingType
        self.Cost = _Cost
        self.UnlockBuildingAmount = _UnlockBuildingAmount

class BuildingType():
    def __init__(self,_Name,_Value,_CPS,_Cooldown=999999999,_AmountOwned=0):
        self.Name = _Name
        self.Value = _Value
        self.CPS = _CPS
        self.Cooldown = _Cooldown
        self.AmountOwned = _AmountOwned

Template_BuildingTypes = [BuildingType("Cursor",15,0.1)]

class GameState():
    def __init__(self,_FramesPassed=0,_ClickCooldown=40,_ClickPower=1,_Bank=0,_CookiesBaked=0,_Buildings=Template_BuildingTypes,_UpgradeVault=[]):
        self.TimePassed = _FramesPassed
        self.ClickCooldown = _ClickCooldown
        self.ClickPower = _ClickPower
        self.Bank = _Bank
        self.CookiesBaked = _CookiesBaked
        self.Buildings = _Buildings
        self.UpgradeVault = _UpgradeVault
        self.ActionCooldowns = [self.ClickCooldown]
        self.ActionCooldownSources = ["Clicking"]
        for x in range(len(self.Buildings)):
            self.ActionCooldownSources.append(Toolbelt.TaggedVal(self.Buildings[x].Cooldown,self.Buildings[x]))
            
            

    def Click(self):
        self.Bank += self.ClickPower
        self.CookiesBaked += self.ClickPower
        self.ClickCooldown = 40

    def AdvanceSim(self):
        for x in range()


        NextAction = min(self.ActionCooldowns)
        self.TimePassed += NextAction

        for x in range(len(self.ActionCooldowns)):
            self.ActionCooldowns[x] -= 

        self.ClickCooldown -= 1
        if self.ClickCooldown == 0:
            Click()
        for x in range(len(self.Buildings)):
            self.Buildings[x].Cooldown -= 1
            if self.Buildings[x].Cooldown == 0:
                self.Bank += self.Buildings[x].CPS/30

    def RemoveFromUpgradeVault(self,_Upgrade):
        self.UpgradeVault.pop(UpgradeVault.index(_Upgrade.Name))

    def Buy_Upgrade(self,_UpgradePurchase):
        self.Bank -= _UpgradePurchase.Cost
        RemoveFromUpgradeVault(_UpgradePurchase)
        if _UpgradePurchase.BuildingType == "Cursor":
            self.ClickPower = self.ClickPower * _UpgradePurchase.UpgradeFactor
        self.Buildings[]

