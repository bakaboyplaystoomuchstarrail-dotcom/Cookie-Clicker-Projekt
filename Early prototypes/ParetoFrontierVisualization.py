import math
import itertools
from collections import deque

Goal = int(input("Please input the Cookies Baked End Goal: "))

# ---------- Building definitions ----------
class Building:
    def __init__(self, name, id, base_cpf, base_cost):
        self.Name = name
        self.ID = id
        self.BaseCPF = base_cpf
        self.BaseCost = base_cost

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
        self.Count = count

    def NextCost(self):
        base = BuildingTypes[self.BuildingID].BaseCost
        return math.ceil(base * (1.15 ** self.Count))

    def TotalCost(self):
        base = BuildingTypes[self.BuildingID].BaseCost
        if self.Count == 0:
            return 0
        return math.ceil(base * ((1.15**self.Count) - 1) / 0.15)

class Combination:
    def __init__(self, purchases):
        self.Purchases = purchases[:]
        self.CookiesBaked = sum(p.TotalCost() for p in self.Purchases)

    def MaxAffordable(self, building_id):
        Gap = Goal - self.CookiesBaked
        base = BuildingTypes[building_id].BaseCost
        if Gap <= 0:
            return 0
        return math.floor(math.log((Gap * 0.15 / base) + 1, 1.15))

    def Info(self):
        return [f"{p.Count} {BuildingTypes[p.BuildingID].Name}" for p in self.Purchases]

# ---------- Upgrade definitions ----------
class Upgrade:
    def __init__(self, name, building_id, cost, unlock):
        self.Name = name
        self.BuildingID = building_id
        self.Cost = cost
        self.Unlock = unlock   # number of buildings required

# Upgrades from Cookie Clicker wiki (under 1,000,000 cost)
UpgradeList = [
    Upgrade("Reinforced Index Finger", 4, 100, 1),
    Upgrade("Carpal Tunnel Prevention Cream", 4, 500, 1),
    Upgrade("Ambidextrous", 4, 10000, 10),
    Upgrade("Thousand Fingers", 4, 100000, 25),
    Upgrade("Million Fingers", 4, 1000000, 50),
    Upgrade("Forwards from grandma", 3, 1000, 1),
    Upgrade("Steel-plated rolling pins", 3, 5000, 5),
    Upgrade("Lubricated dentures", 3, 50000, 25),
    Upgrade("Prune juice", 3, 500000, 50),
    Upgrade("Cheap hoes", 2, 11000, 1),
    Upgrade("Fertilizer", 2, 55000, 5),
    Upgrade("Cookie trees", 2, 550000, 25),
    Upgrade("Sugar gas", 1, 120000, 1),
    Upgrade("Megadrill", 1, 600000, 5),
]

# ---------- Generate all maximal building combinations (same as before) ----------
C0_purchases = [BuildingPurchase(b.ID, 0) for b in BuildingTypes]
current_combo = Combination(C0_purchases)
for building in BuildingTypes:
    max_n = current_combo.MaxAffordable(building.ID)
    if max_n > 0:
        C0_purchases[building.ID].Count = max_n
        current_combo = Combination(C0_purchases[:])
C0 = current_combo
𝓒 = {C0}
𝓠 = [C0]

def is_maximal(combo):
    total = combo.CookiesBaked
    for i, p in enumerate(combo.Purchases):
        next_cost = math.ceil(BuildingTypes[i].BaseCost * (1.15 ** p.Count))
        if total + next_cost < Goal:
            return False
    return True

def generate_allocations(target_indices, freed, base_combo):
    result = []
    def recurse(pos, remaining, current):
        if pos == len(target_indices):
            result.append(tuple(current))
            return
        idx = target_indices[pos]
        cur_cnt = base_combo.Purchases[idx].Count
        base = BuildingTypes[idx].BaseCost
        max_q = 0
        total_cost = 0
        while True:
            next_price = math.ceil(base * (1.15 ** (cur_cnt + max_q)))
            if total_cost + next_price <= remaining:
                total_cost += next_price
                max_q += 1
            else:
                break
        for q in range(max_q + 1):
            cost_q = 0
            for k in range(q):
                cost_q += math.ceil(base * (1.15 ** (cur_cnt + k)))
            if cost_q <= remaining:
                recurse(pos+1, remaining - cost_q, current + [q])
    recurse(0, freed, [])
    return result

while 𝓠:
    C = 𝓠.pop(0)
    for i in range(len(C.Purchases)):
        if C.Purchases[i].Count == 0:
            continue
        for O in range(1, C.Purchases[i].Count + 1):
            omitted_counts = [p.Count for p in C.Purchases]
            omitted_counts[i] -= O
            omitted_purchases = [BuildingPurchase(bid, omitted_counts[bid]) for bid in range(len(BuildingTypes))]
            C_omitted = Combination(omitted_purchases)
            freed = C.CookiesBaked - C_omitted.CookiesBaked
            cheaper = list(range(i+1, len(BuildingTypes)))
            if not cheaper:
                continue
            BC = []
            for r in range(1, len(cheaper)+1):
                for subset in itertools.combinations(cheaper, r):
                    BC.append(list(subset))
            for T in BC:
                allocations = generate_allocations(T, freed, C)
                for alloc in allocations:
                    new_counts = omitted_counts[:]
                    for pos, idx in enumerate(T):
                        new_counts[idx] += alloc[pos]
                    new_purchases = [BuildingPurchase(bid, new_counts[bid]) for bid in range(len(BuildingTypes))]
                    new_combo = Combination(new_purchases)
                    if is_maximal(new_combo) and new_combo not in 𝓒:
                        𝓒.add(new_combo)
                        𝓠.append(new_combo)

print(f"Found {len(𝓒)} maximal building combinations.")

# ---------- Step 2: Generate valid upgrade subsets for each building combo ----------
def valid_upgrade_subsets(building_combo):
    """Return list of frozensets of upgrade indices that are affordable and unlockable."""
    valid = []
    total_building = building_combo.CookiesBaked
    n = len(UpgradeList)
    # Generate all subsets using bitmask (efficient)
    for mask in range(1 << n):
        subset = []
        cost = 0
        ok = True
        for j in range(n):
            if mask & (1 << j):
                u = UpgradeList[j]
                cost += u.Cost
                if building_combo.Purchases[u.BuildingID].Count < u.Unlock:
                    ok = False
                    break
        if ok and total_building + cost < Goal:
            valid.append(frozenset(j for j in range(n) if mask & (1 << j)))
    return valid

combined_combos = []   # list of (building_combo, upgrade_set)
for bc in 𝓒:
    for us in valid_upgrade_subsets(bc):
        combined_combos.append((bc, us))

print(f"Generated {len(combined_combos)} combined (building+upgrade) combinations.")

# ---------- Step 3: Generate all valid sequences for a combined combination ----------
def generate_sequences(bc, us):
    """Return list of sequences (each sequence is list of (type, idx)). type 0=building,1=upgrade."""
    n_types = len(BuildingTypes)
    # Initial state: owned=0, remaining=bc.Purchases counts, remainingU=us, unlockedU=empty
    owned = [0]*n_types
    remaining = [p.Count for p in bc.Purchases]
    remainingU = set(us)
    unlockedU = set()

    # Queue elements: (sequence list, owned, remaining, remainingU, unlockedU)
    queue = deque()
    # First moves: all buildings with remaining>0
    for i in range(n_types):
        if remaining[i] > 0:
            new_owned = owned[:]
            new_remaining = remaining[:]
            new_owned[i] = 1
            new_remaining[i] -= 1
            new_unlocked = set()
            for u_idx in remainingU:
                u = UpgradeList[u_idx]
                if u.BuildingID == i and new_owned[i] >= u.Unlock:
                    new_unlocked.add(u_idx)
            queue.append(([(0, i)], new_owned, new_remaining, set(remainingU), new_unlocked))

    sequences = []
    while queue:
        seq, own, rem, remU, unlocked = queue.popleft()
        # Check if complete
        if all(r == 0 for r in rem) and len(remU) == 0:
            sequences.append(seq)
            continue
        # Determine available purchases
        available = []
        for i in range(n_types):
            if rem[i] > 0:
                available.append(('b', i))
        for u_idx in remU:
            if u_idx in unlocked:
                available.append(('u', u_idx))
        for typ, idx in available:
            new_own = own[:]
            new_rem = rem[:]
            new_remU = set(remU)
            new_unlocked = set(unlocked)
            if typ == 'b':
                new_own[idx] += 1
                new_rem[idx] -= 1
                # Check for newly unlocked upgrades
                for u_idx in new_remU:
                    if u_idx not in new_unlocked:
                        u = UpgradeList[u_idx]
                        if u.BuildingID == idx and new_own[idx] >= u.Unlock:
                            new_unlocked.add(u_idx)
            else:  # upgrade
                new_remU.remove(idx)
                if idx in new_unlocked:
                    new_unlocked.remove(idx)
            new_seq = seq + [(1, idx) if typ == 'u' else (0, idx)]
            queue.append((new_seq, new_own, new_rem, new_remU, new_unlocked))
    return sequences

# ---------- Step 4: Time calculation for a sequence ----------
def sequence_time(seq, bc, us):
    """Simulate sequence and return frames to reach Goal."""
    owned = [0]*len(BuildingTypes)
    upgrade_counts = [0]*len(BuildingTypes)
    bank = 0
    frames = 0
    total_spent = 0
    for typ, idx in seq:
        if typ == 0:  # building
            price = math.ceil(BuildingTypes[idx].BaseCost * (1.15 ** owned[idx]))
        else:  # upgrade
            # idx is index in us, need actual upgrade object
            u = UpgradeList[list(us)[idx]]   # convert us to list for indexing
            price = u.Cost
        # wait until affordable
        while bank < price:
            cpf = 0
            for i in range(len(BuildingTypes)):
                cpf += BuildingTypes[i].BaseCPF * owned[i] * (2 ** upgrade_counts[i])
            click = 1 * (2 ** upgrade_counts[4])  # cursor index 4
            prod = cpf + click
            bank += prod
            frames += 1
        bank -= price
        total_spent += price
        if typ == 0:
            owned[idx] += 1
        else:
            upgrade_counts[u.BuildingID] += 1
    # wait until total baked reaches goal
    while bank + total_spent < Goal:
        cpf = 0
        for i in range(len(BuildingTypes)):
            cpf += BuildingTypes[i].BaseCPF * owned[i] * (2 ** upgrade_counts[i])
        click = 1 * (2 ** upgrade_counts[4])
        prod = cpf + click
        bank += prod
        frames += 1
    return frames

# ---------- Step 5: Find optimal sequence ----------
best_time = float('inf')
best_seq = None
best_combined = None

for i, (bc, us) in enumerate(combined_combos):
    print(f"Processing combined combo {i+1}/{len(combined_combos)}: {bc.Info()} with {len(us)} upgrades")
    seqs = generate_sequences(bc, us)
    print(f"  Generated {len(seqs)} sequences")
    for s in seqs:
        t = sequence_time(s, bc, us)
        if t < best_time:
            best_time = t
            best_seq = s
            best_combined = (bc, us)
            print(f"    New best: {t} frames")

# ---------- Step 6: Other algorithms for comparison (greedy, heuristic, click-only, first-affordable) ----------
def greedy_algorithm():
    owned = [0]*len(BuildingTypes)
    upg_counts = [0]*len(BuildingTypes)
    bank = 0
    frames = 0
    seq = []
    while bank < Goal:
        cpf = sum(BuildingTypes[i].BaseCPF * owned[i] * (2**upg_counts[i]) for i in range(len(BuildingTypes)))
        best = None
        best_ratio = 0
        # buildings
        for i in range(len(BuildingTypes)):
            if BuildingTypes[i].BaseCost < Goal:  # affordable in principle
                price = math.ceil(BuildingTypes[i].BaseCost * (1.15 ** owned[i]))
                if bank >= price:
                    gain = BuildingTypes[i].BaseCPF * (2**upg_counts[i])
                    ratio = gain / price
                    if ratio > best_ratio:
                        best_ratio = ratio
                        best = ('b', i)
        # upgrades
        for u in UpgradeList:
            if owned[u.BuildingID] >= u.Unlock and bank >= u.Cost:
                gain = BuildingTypes[u.BuildingID].BaseCPF * owned[u.BuildingID] * (2**upg_counts[u.BuildingID])
                ratio = gain / u.Cost
                if ratio > best_ratio:
                    best_ratio = ratio
                    best = ('u', u)
        if best:
            if best[0] == 'b':
                i = best[1]
                price = math.ceil(BuildingTypes[i].BaseCost * (1.15 ** owned[i]))
                bank -= price
                owned[i] += 1
                seq.append(('b', i))
            else:
                u = best[1]
                bank -= u.Cost
                upg_counts[u.BuildingID] += 1
                seq.append(('u', UpgradeList.index(u)))
        else:
            bank += cpf + 1
            frames += 1
    return seq, frames

def heuristic_algorithm():
    owned = [0]*len(BuildingTypes)
    upg_counts = [0]*len(BuildingTypes)
    bank = 0
    frames = 0
    seq = []
    cheap_first = True
    while bank < Goal:
        cpf = sum(BuildingTypes[i].BaseCPF * owned[i] * (2**upg_counts[i]) for i in range(len(BuildingTypes)))
        bought = False
        if cheap_first:
            order = sorted(range(len(BuildingTypes)), key=lambda i: BuildingTypes[i].BaseCost)
        else:
            order = sorted(range(len(BuildingTypes)), key=lambda i: BuildingTypes[i].BaseCost, reverse=True)
        for i in order:
            price = math.ceil(BuildingTypes[i].BaseCost * (1.15 ** owned[i]))
            if bank >= price:
                bank -= price
                owned[i] += 1
                seq.append(('b', i))
                cheap_first = not cheap_first
                bought = True
                break
        if not bought:
            for u in UpgradeList:
                if owned[u.BuildingID] >= u.Unlock and bank >= u.Cost:
                    bank -= u.Cost
                    upg_counts[u.BuildingID] += 1
                    seq.append(('u', UpgradeList.index(u)))
                    bought = True
                    break
        if not bought:
            bank += cpf + 1
            frames += 1
    return seq, frames

def click_only():
    return [], Goal  # 1 frame per cookie

def first_affordable():
    owned = [0]*len(BuildingTypes)
    upg_counts = [0]*len(BuildingTypes)
    bank = 0
    frames = 0
    seq = []
    # priority: buildings sorted by cost, then upgrades sorted by cost
    building_order = sorted(range(len(BuildingTypes)), key=lambda i: BuildingTypes[i].BaseCost)
    upgrade_order = sorted(range(len(UpgradeList)), key=lambda i: UpgradeList[i].Cost)
    while bank < Goal:
        cpf = sum(BuildingTypes[i].BaseCPF * owned[i] * (2**upg_counts[i]) for i in range(len(BuildingTypes)))
        bought = False
        for i in building_order:
            price = math.ceil(BuildingTypes[i].BaseCost * (1.15 ** owned[i]))
            if bank >= price:
                bank -= price
                owned[i] += 1
                seq.append(('b', i))
                bought = True
                break
        if not bought:
            for u_idx in upgrade_order:
                u = UpgradeList[u_idx]
                if owned[u.BuildingID] >= u.Unlock and bank >= u.Cost:
                    bank -= u.Cost
                    upg_counts[u.BuildingID] += 1
                    seq.append(('u', u_idx))
                    bought = True
                    break
        if not bought:
            bank += cpf + 1
            frames += 1
    return seq, frames

print("\nRunning comparison algorithms...")
g_seq, g_time = greedy_algorithm()
h_seq, h_time = heuristic_algorithm()
c_seq, c_time = click_only()
f_seq, f_time = first_affordable()

print("\n" + "="*50)
print("RESULTS")
print("="*50)
print(f"Optimal: {best_time} frames ({best_time/30:.2f} s)")
print(f"Greedy: {g_time} frames ({g_time/30:.2f} s) – {g_time/best_time:.2f}x slower")
print(f"Heuristic: {h_time} frames ({h_time/30:.2f} s) – {h_time/best_time:.2f}x slower")
print(f"First-Affordable: {f_time} frames ({f_time/30:.2f} s) – {f_time/best_time:.2f}x slower")
print(f"Click-Only: {c_time} frames ({c_time/30:.2f} s) – {c_time/best_time:.2f}x slower")

# Optional: print optimal sequence
print("\nOptimal sequence (first 10 purchases):")
for i, p in enumerate(best_seq[:10]):
    if p[0] == 0:
        print(f"  {i+1}. Buy {BuildingTypes[p[1]].Name}")
    else:
        # need to map upgrade index
        u_idx = list(best_combined[1])[p[1]]
        print(f"  {i+1}. Buy {UpgradeList[u_idx].Name}")