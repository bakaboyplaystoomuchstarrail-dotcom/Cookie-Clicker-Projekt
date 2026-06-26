import math
import time

Goal = int(input("What should the goal be?"))

class BuildingType():
    def __init__(self,_BuildingName,_BasePrice,_BaseCPS):
        self.Name = _BuildingName
        self.BasePrice = _BasePrice
        self.BaseCPS = _BaseCPS
    
Cursor = BuildingType("Cursor",15,0.1)
Grandma = BuildingType("Grandma",100,1)
Farm = BuildingType("Farm",1100,8)
Mine = BuildingType("Mine",1200,47)
Factory = BuildingType("Factory",13000,260)
BuildingTypes = [Cursor,Grandma,Farm,Mine,Factory]

class UpgradePurchase():
    def __init__(self,_UpgradeName,_CorrespondingBuildingType,_Price,_UnlockRequirement):
        self.Name = _UpgradeName
        self.CorrespondingBuildingType = _CorrespondingBuildingType
        self.Price = _Price
        self.UnlockRequirement = _UnlockRequirement

#Insert these in ascending order of price
Upg1 = UpgradePurchase("Reinforced Index Finger",0,100,1)

Upgrades = [Upg1]



class Combination():
    def __init__(self):
        self.UpgradePurchases = []
        self.Cursors = 0
        self.Grandmas = 0
        self.Farms = 0
        self.Mines = 0
        self.Factories = 0
        self.Buildings = [self.Cursors,self.Grandmas,self.Farms,self.Mines,self.Factories]
        self.TimeElapsed = 0
        self.CD = 0
        self.CookiesInBank = 0
        self.CookiesBaked = 0

    def CopyCombinationInformation(self,_BlueprintCombination):
        for attr_name, attr_value in vars(_BlueprintCombination).items():
            setattr(self, attr_name, attr_value)
        self.Buildings = [self.Cursors,self.Grandmas,self.Farms,self.Mines,self.Factories]

    def Click(self):
        #FAH
        self.CookiesBaked += 1
        self.CookiesInBank += 1
        self.CD = 41

    def CalcNextBuildingCost(self,_BuildingType):
        return(BuildingTypes[_BuildingType].BasePrice * (1.15**self.Buildings[_BuildingType]))

    def BuyBuilding(self,_BuildingType,_NumBuildings=1):
        #FAH
        for x in range(_NumBuildings): 
            # self.CookiesInBank -= self.CalcNextBuildingCost(_BuildingType)
            self.Buildings[_BuildingType] += 1

    def CalcGap(self):
        return(Goal - self.CookiesBaked)

    def MaxAmtOfBuildingType(self,_BuildingType,_Gap=None):
        if _Gap == None:
            _Gap = self.CalcGap()
        self.Buildings[_BuildingType] -= 1
        MaxAmt = math.floor(math.log((((_Gap*0.15)/self.CalcNextBuildingCost(_BuildingType))+1),1.15))
        self.Buildings[_BuildingType] += 1
        return(MaxAmt)

    def Omit(self,_BuildingType,_NumBuildings):
        #F = Freed Cookies
        F = 0
        for x in range(_NumBuildings):
            self.Buildings[_BuildingType] -= 1
            F += self.CalcNextBuildingCost(_BuildingType)
        return(F)

    def GenerateBc(self,_F,_OmittedType):
        Bc = []
        Bm = []
        for x in range(len(BuildingTypes)):
            if BuildingTypes[x].MaxAmtOfBuildingType(x,_F) > 0 and x != _OmittedType:
                Bm.append(x)
        for x in range(len(Bm)):
            x += 1
            Temp_Bm = []
            for i in range(len(Bm)):
                Temp_Bm.append(Bm[i])

            row = []
            for i in range(x):
                Temp_Bm.pop(0)  

            for i in range(x):
                row.append(Bm[i])

            for i in range(len(Temp_Bm)):
                row.append(Temp_Bm[i])
            Bc.append(row)
        return(Bc)

    def GenerateAb(self,_Bc,_F):
        Ab = []
        for x in range(len(_Bc)):
            T = _Bc[x] #ie [0,1,2]

            for y in range(len(T)):
                Temp_T = []
                for i in range(len(T)):
                    Temp_T.append(T[i])
                
                for i in range(y): #keep some aside
                    Temp_T.pop(i)  
                
                for i in range(y-x):
                    Gap = _F
                    ATF = []
                    for z in range(len(Temp_T)):
                        row = [T[i]]#idx of building type
                        row.append(self.MaxAmtOfBuildingType(Temp_T[z],Gap))
                        Gap -= BuildingTypeSumPrice(Temp_T[z],self.MaxAmtOfBuildingType(Temp_T[z],Gap))
                        ATF.append(row)
                    Ab.append(ATF)
        return(Ab)

    def Redistribute(self,_T):
        for x in range(len(_T)):#single type, double type, ... etc
            for i in range(_T[x][1]):#quant of buildings of type
                self.BuyBuilding(_T[x][0],_T[x][1])

    def GenerateUc(self,_U):
        Uc = []
        for x in range(len(_U)):
            Temp_U = []
            for i in range(len(_U)):
                Temp_U.append(_U[i])

            for i in range(x):
                Temp_U.pop(0)

            for i in range(x):
                row = []
        #FAH



def BuildingTypeSumPrice(_BuildingType,_NumBuildings):
    return(BuildingTypes[_BuildingType]*((1.15**_NumBuildings)-1)/0.15)


if Goal < 16:
    print("Just click bro, the goal is too small for purchases to improve speed")
else:
    Queue = []
    delta_bC = []
    for x in range(len(BuildingTypes)):
        Queue.append(Combination())
        C = Queue[-1]
        for i in range(len(C.Buildings)):
            C.Buildings[i] = C.MaxAmtOfBuildingType(i,C.CalcGap())
            C.BuyBuilding(i,C.Buildings[i])

    for x in range(len(Queue)):
        delta_bC.append(Queue[x])
        
    while len(Queue) != 0:
        C_Template = Queue[0]
        for x in range(len(C.Buildings)):
            for i in range(C.Buildings[x]):
                F = C_Template.Omit(x,i)
                Ab = C_Template.GenerateAb(C_Template.GenerateBc(F,x),F)
                for z in range(len(Ab)):
                    Candidate_C = Combination()
                    Candidate_C.CopyCombinationInformation(C_Template)
                    Candidate_C.Redistribute(Ab[z])

                    Identity = Identical
                    while Identity == Identical:
                        for y in range(len(Candidate_C.Buildings)):
                            for w in range(delta_bC):
                                if Candidate_C.Buildings[y] != delta_bC[w].Buildings[y]:
                                    Identity = Unique
                                    delta_bC.append(Candidate_C)
                                    break
                        break
        Queue.pop(0)

    # U = []
    # Counter = 0
    # while Upgrades[Counter].Price < Goal:
    #     U.append(Upgrades[Counter])
    #     Counter += 1

    

                        
                    



#irrelevant
delta_S = []
delta_C = []
delta_Uc = []
