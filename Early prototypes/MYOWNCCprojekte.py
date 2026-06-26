import math
import itertools

Goal = int(input("Please input the Cookies Baked End Goal: "))

class Building:
    def __init__(self, name, id, base_cpf, base_cost):
        self.Name = name
        self.ID = id
        self.BaseCPF = base_cpf
        self.BaseCost = base_cost

# Building types: order them from most expensive to least expensive
BuildingTypes = [
    Building("Factory", 0, 260, 130000),
    Building("Mine", 1, 47, 12000),
    Building("Farm", 2, 8, 1100),
    Building("Grandma", 3, 1, 100),
    Building("Cursor", 4, 0.1, 15)
]

class BuildingPurchase:
    def __init__(self, building_id, count):
        self.BuildingID = building_id
        self.Count = count          # number of buildings of this type owned

    def NextCost(self):
        """Cost of the next building of this type."""
        base_cost = BuildingTypes[self.BuildingID].BaseCost
        return math.ceil(base_cost * (1.15 ** self.Count))

    def TotalCost(self):
        """Total cost of all buildings of this type (geometric series)."""
        base_cost = BuildingTypes[self.BuildingID].BaseCost
        if self.Count == 0:
            return 0
        else:
            # Use the sum total price of n buildings formula we established
            return math.ceil(base_cost * ((1.15**self.Count) - 1) / 0.15)

class Combination:
    def __init__(self, purchases=None):
        self.Purchases = purchases if purchases is not None else []
        self.CookiesBaked = sum(purchase.TotalCost() for purchase in self.Purchases)

    def MaxAffordable(self, building_id):
        """Maximum number of buildings of type 'building_id' that can be added
           given the remaining cookies."""
        Gap = Goal - self.CookiesBaked
        base_cost = BuildingTypes[building_id].BaseCost
        if Gap <= 0:
            return 0
        # Use the max amount of building type n affordable formula we created
        return math.floor(math.log((Gap * 0.15 / base_cost) + 1, 1.15))

    def Info(self):
        return [f"{purchase.Count} {BuildingTypes[purchase.BuildingID].Name}" for purchase in self.Purchases]

# Generate template combination C0
C0_purchases = []
current_combo = Combination()  # start with empty combination

# Loop over building types in the given order (most expensive first)
for building in BuildingTypes:
    max_n = current_combo.MaxAffordable(building.ID)
    if max_n > 0:
        # Add a purchase record for this building type with the max affordable count
        C0_purchases.append(BuildingPurchase(building.ID, max_n))
        # Update the current combination to include all purchases so far
        current_combo = Combination(C0_purchases[:])  # pass a copy

C0 = current_combo
𝓒 = [C0]
𝓠 = [C0]

while len(𝓠) != 0:
    #We consider a combination C, from the start of the queue, 
    #however we need to make many altercations to this combination so we save this one as a template
    C = 𝓠[0]
    C_template = 𝓠[0]

    for bi in range(len(C.Purchases)):
        #Checking if the building type being considered is the last possible one, if so just end because omitting and redistributing it's purchase
        #Would be backtracking which is not something we want. 
        if bi == len(C.Purchases):
            print("No more building types to check")
        else:
            purchase_bi = C.Purchases[bi]
            OmissionQuantity = 0
            while purchase_bi.Count != 0:
                #The amount of purchases being made in C is reduced by the omission quantity, the template remains unchanged
                #Sometimes there can be a disconnect between the template and the combination, if say an entire building type's worth of omissions have occured
                #For these scenarios we need to find the id of the building purchase of type bi in the template since it may not be the same as the actual combination
                Template_bi = C_template.Purchases.index(purchase_bi) 
                Template_purchase_bi = C_template.Purchases[Template_bi]
                purchase_bi.Count = Template_purchase_bi.Count - OmissionQuantity

                #This frees up F cookies
                Freed_Cookies = sum(purchase.TotalCost() for purchase in C_template.Purchases) - sum(purchase.TotalCost() for purchase in C.Purchases)
                
                #k represents the amount of building types we need to consider redistributing to since we consider redistributing 
                #To every type after the current until the last, since we don't want to backtrack and redistribute cookies to a type we've 
                #already omitted purchases from
                m = len(C.Purchases)
                #bi + k = m therefore you can rearrange to get
                k = m - bi
                AllocationTypes = []
                for cheaper_bi in range(k):
                    AllocationTypes.append(BuildingTypes[C.Purchases[cheaper_bi].BuildingID])

                #The IDs of all the building types cheaper than the type omitted
                AllocationIDs = [bi.ID for bi in AllocationTypes]

                B_c = []
                for t in range(k):
                    B_c.append(list(itertools.combinations(AllocationIDs,t)))
                #This finishes the generation of B_c by creating and appending all possible subsets of building types that can be owned 

                while len(B_c) != 0:
                    T = B_c[0]
                    𝒜 = []

                    Gap = F
                    while Gap > 0:
                        for x in range(len(T)): 
                            new_max_bi = C.MaxAffordable(T[x])
                            quant_difference = new_max_bi - T[x].count
                            if quant_difference == 0:
                                print()
                            else:
                                for z in range(quant_difference):
                                    Gap -= T[x].NextCost()
                                    if Gap < 0:
                                        Gap += T[x].NextCost()
                                        
                
                                        
                                        𝒜.append()
                                        break
