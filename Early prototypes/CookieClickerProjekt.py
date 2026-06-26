import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set
from functools import lru_cache
from collections import defaultdict
import time
from datetime import datetime, timedelta

# Constants
MILLISECONDS_PER_FRAME = 100 / 3  # 33.333... ms
CLICK_COOLDOWN = 40  # ms
CURSOR_BASE_CLICK_VALUE = 1  # cookie per click

class ProgressTracker:
    """Tracks and displays detailed progress information"""
    
    def __init__(self, total_items: int, description: str = "Processing"):
        self.total_items = total_items
        self.description = description
        self.start_time = time.time()
        self.last_update = self.start_time
        self.processed = 0
        self.current_item = 0
        self.best_time_so_far = float('inf')
        self.best_combination = None
        
        # Statistics
        self.combinations_explored = 0
        self.permutations_explored = 0
        self.pruned_count = 0
        
        # For ETA calculation
        self.progress_history = []
        
    def update(self, processed: int = None, current_item: str = None):
        """Update progress and display status"""
        current_time = time.time()
        
        if processed is not None:
            self.processed = processed
            self.current_item = processed
        else:
            self.processed += 1
            self.current_item = self.processed
            
        # Record progress for ETA
        self.progress_history.append((current_time, self.processed))
        if len(self.progress_history) > 10:
            self.progress_history.pop(0)
            
        # Only update display every 0.5 seconds to avoid spam
        if current_time - self.last_update > 0.5:
            self._display_progress(current_item)
            self.last_update = current_time
            
    def _display_progress(self, current_item: str = None):
        """Display formatted progress information"""
        elapsed = time.time() - self.start_time
        
        # Calculate progress percentage
        if self.total_items > 0:
            percent = (self.processed / self.total_items) * 100
        else:
            percent = 0
            
        # Calculate ETA
        eta = self._calculate_eta()
        
        # Clear line and print progress
        print(f"\r{' ' * 100}", end='\r')
        
        # Progress bar
        bar_length = 30
        filled = int(bar_length * self.processed / self.total_items) if self.total_items > 0 else 0
        bar = '█' * filled + '░' * (bar_length - filled)
        
        # Main progress line
        print(f"\r[{bar}] {percent:.1f}% | ", end='')
        print(f"{self.processed}/{self.total_items} {self.description} | ", end='')
        print(f"Elapsed: {self._format_time(elapsed)} | ", end='')
        print(f"ETA: {self._format_time(eta) if eta != float('inf') else 'unknown'}", end='')
        
        # Current item on new line
        if current_item:
            print(f"\n  → Currently: {current_item}", end='')
            
        # Stats on new line
        stats = []
        if self.combinations_explored > 0:
            stats.append(f"Combinations: {self.combinations_explored}")
        if self.permutations_explored > 0:
            stats.append(f"Permutations: {self.permutations_explored}")
        if self.pruned_count > 0:
            stats.append(f"Pruned: {self.pruned_count}")
        if self.best_time_so_far != float('inf'):
            stats.append(f"Best time: {self.best_time_so_far/1000:.1f}s")
            
        if stats:
            print(f"\n  → {' | '.join(stats)}", end='')
            
        import sys
        sys.stdout.flush()
        
    def _calculate_eta(self) -> float:
        """Calculate estimated time remaining"""
        if len(self.progress_history) < 2 or self.processed == 0:
            return float('inf')
            
        times = [t for t, _ in self.progress_history]
        counts = [c for _, c in self.progress_history]
        
        if len(times) >= 2:
            time_diff = times[-1] - times[0]
            count_diff = counts[-1] - counts[0]
            
            if count_diff > 0 and time_diff > 0:
                rate = count_diff / time_diff
                remaining_items = self.total_items - self.processed
                return remaining_items / rate
                
        return float('inf')
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds into readable time"""
        if seconds == float('inf'):
            return "unknown"
            
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def set_best(self, time_ms: float, combination):
        """Update the best time found"""
        if time_ms < self.best_time_so_far:
            self.best_time_so_far = time_ms
            self.best_combination = combination
            
    def finish(self):
        """Display final statistics"""
        elapsed = time.time() - self.start_time
        print(f"\n\n✅ Complete! Total time: {self._format_time(elapsed)}")
        print(f"   Combinations explored: {self.combinations_explored}")
        print(f"   Permutations explored: {self.permutations_explored}")
        print(f"   Branches pruned: {self.pruned_count}")

@dataclass
class Building:
    """Represents a building type in Cookie Clicker"""
    name: str
    base_price: float
    base_cpf: float
    unlock_threshold: int = 0
    
    def price(self, owned: int) -> int:
        """Calculate price of next building"""
        if owned == 0:
            return self.base_price
        return math.ceil(self.base_price * (1.15 ** owned))
    
    def total_cost(self, n: int) -> float:
        """Calculate total cost for n buildings"""
        if n == 0:
            return 0
        return self.base_price * (1.15 ** n - 1) / 0.15
    
    def max_affordable(self, cookies: float) -> int:
        """Calculate maximum number of this building affordable with given cookies"""
        if cookies < self.base_price:
            return 0
        max_n = math.floor(math.log((cookies * 0.15 / self.base_price) + 1, 1.15))
        return max(max_n, 0)

@dataclass
class Upgrade:
    """Represents an upgrade purchase"""
    building_name: str
    cost: int
    unlocks_at: int
    name: str = ""
    
    def __post_init__(self):
        if not self.name:
            self.name = f"{self.building_name} Upgrade #{self.unlocks_at}"
    
    def is_unlocked(self, owned_buildings: int) -> bool:
        return owned_buildings >= self.unlocks_at

# Define all buildings
BUILDINGS = {
    "cursor": Building("cursor", 15, 0.1, 0),
    "grandma": Building("grandma", 100, 0.5, 1),
    "farm": Building("farm", 1100, 4, 1),
    "mine": Building("mine", 12000, 40, 1),
    "factory": Building("factory", 130000, 100, 1),
}

# Define upgrades
UPGRADES = {
    "cursor": [
        Upgrade("cursor", 100, 1, "Reinforced index finger"),
        Upgrade("cursor", 500, 10, "Carpal tunnel prevention cream"),
        Upgrade("cursor", 10000, 50, "Ambidextrous"),
    ],
    "grandma": [
        Upgrade("grandma", 500, 1, "Forwards from grandma"),
        Upgrade("grandma", 5000, 10, "Steel-plated rolling pins"),
    ],
    "farm": [
        Upgrade("farm", 6000, 1, "Cheaper eggs"),
    ],
    "mine": [
        Upgrade("mine", 70000, 1, "Sugar gas"),
    ],
}

@dataclass
class ProductionState:
    """Represents the current production capabilities"""
    buildings: Dict[str, int] = field(default_factory=dict)
    upgrades: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.buildings:
            self.buildings = {name: 0 for name in BUILDINGS}
        if not self.upgrades:
            self.upgrades = {name: 0 for name in BUILDINGS}
    
    def copy(self) -> 'ProductionState':
        new_state = ProductionState()
        new_state.buildings = self.buildings.copy()
        new_state.upgrades = self.upgrades.copy()
        return new_state
    
    def building_cpf(self, building_name: str) -> float:
        b = BUILDINGS[building_name]
        n = self.buildings[building_name]
        u = self.upgrades[building_name]
        return b.base_cpf * n * (2 ** u)
    
    def total_cpf(self) -> float:
        return sum(self.building_cpf(name) for name in BUILDINGS)
    
    def total_cpms(self) -> float:
        return self.total_cpf() / MILLISECONDS_PER_FRAME
    
    def click_value(self) -> float:
        return CURSOR_BASE_CLICK_VALUE * (2 ** self.upgrades["cursor"])
    
    def click_cpms(self) -> float:
        return self.click_value() / CLICK_COOLDOWN
    
    def total_cpms_with_clicks(self) -> float:
        return self.total_cpms() + self.click_cpms()
    
    def purchase_building(self, building_name: str):
        self.buildings[building_name] += 1
    
    def purchase_upgrade(self, building_name: str):
        self.upgrades[building_name] += 1

@dataclass
class Purchase:
    """Represents a single purchase action"""
    type: str
    name: str
    cost: int
    upgrade_index: int = -1
    upgrade_name: str = ""
    time_purchased: float = 0.0
    bank_before: float = 0.0
    
    def __post_init__(self):
        if self.type == 'upgrade' and self.upgrade_index >= 0:
            if self.name in UPGRADES and self.upgrade_index < len(UPGRADES[self.name]):
                self.upgrade_name = UPGRADES[self.name][self.upgrade_index].name
    
    def __str__(self):
        if self.type == 'building':
            return f"Buy {self.name} (${self.cost})"
        else:
            name = self.upgrade_name if self.upgrade_name else f"{self.name} upgrade #{self.upgrade_index + 1}"
            return f"Buy {name} (${self.cost})"
    
    def short_str(self) -> str:
        if self.type == 'building':
            return f"{self.name}"
        else:
            return f"{self.name}↑{self.upgrade_index + 1}"
    
    def __hash__(self):
        return hash((self.type, self.name, self.cost, self.upgrade_index))
    
    def __eq__(self, other):
        return (self.type == other.type and 
                self.name == other.name and 
                self.cost == other.cost and
                self.upgrade_index == other.upgrade_index)

@dataclass
class PathCombination:
    """Represents a specific combination of purchases"""
    buildings: Dict[str, int]
    upgrades: Dict[str, int] = field(default_factory=dict)
    total_cost: float = 0.0
    remaining_cookies: float = 0.0
    
    def __post_init__(self):
        self.calculate_total_cost()
    
    def calculate_total_cost(self):
        self.total_cost = 0
        for b_name, count in self.buildings.items():
            if count > 0:
                self.total_cost += BUILDINGS[b_name].total_cost(count)
        
        for b_name, upgrade_count in self.upgrades.items():
            upgrades_list = UPGRADES.get(b_name, [])
            for i in range(upgrade_count):
                if i < len(upgrades_list):
                    self.total_cost += upgrades_list[i].cost
    
    def get_final_state(self) -> ProductionState:
        state = ProductionState()
        for b_name, count in self.buildings.items():
            state.buildings[b_name] = count
        for b_name, count in self.upgrades.items():
            state.upgrades[b_name] = count
        return state
    
    def get_description(self) -> str:
        parts = []
        for b, c in sorted(self.buildings.items()):
            if c > 0:
                parts.append(f"{c}{b[0]}")
        for b, c in sorted(self.upgrades.items()):
            if c > 0:
                parts.append(f"{c}{b[0]}↑")
        return " ".join(parts) if parts else "empty"
    
    def __hash__(self):
        b_tuple = tuple((k, v) for k, v in sorted(self.buildings.items()))
        u_tuple = tuple((k, v) for k, v in sorted(self.upgrades.items()))
        return hash((b_tuple, u_tuple))
    
    def __eq__(self, other):
        return (self.buildings == other.buildings and 
                self.upgrades == other.upgrades)
    
    def __str__(self):
        purchases = []
        for b, c in sorted(self.buildings.items()):
            if c > 0:
                purchases.append(f"{c}x {b}")
        for b, c in sorted(self.upgrades.items()):
            if c > 0:
                name = f"{b} upgrade"
                if c > 1:
                    name += f" x{c}"
                purchases.append(name)
        return f"[{', '.join(purchases)}] (${self.total_cost:.0f})"

class TimeCalculator:
    """Handles time calculations with discrete production considerations"""
    
    @staticmethod
    @lru_cache(maxsize=10000)
    def calculate_segment_time(start_bank: float,
                              target_cookies: float,
                              current_time: float,
                              click_value: float,
                              total_cpms: float) -> Tuple[float, float]:
        """
        Calculate time needed to reach target cookies from current state.
        Simplified version using continuous approximation.
        """
        if start_bank >= target_cookies:
            return 0.0, start_bank
        
        # Calculate minimum delay until next click
        dc = CLICK_COOLDOWN - (current_time % CLICK_COOLDOWN)
        
        if total_cpms <= 0:
            return float('inf'), start_bank
        
        cookies_needed = target_cookies - start_bank
        continuous_time = cookies_needed / total_cpms
        total_time = math.ceil(continuous_time) + dc
        
        # Estimate final bank (simplified)
        clicks = total_time // CLICK_COOLDOWN
        cookie_gain = clicks * click_value + total_cpms * total_time
        final_bank = start_bank + cookie_gain
        
        return total_time, final_bank
    
    @staticmethod
    def calculate_permutation_time(purchases: List[Purchase], 
                                  goal: float) -> Tuple[float, ProductionState, List[float]]:
        """Calculate total time for a specific permutation"""
        if not purchases:
            return 0.0, ProductionState(), []
        
        state = ProductionState()
        bank = 0.0
        total_time = 0.0
        current_time = 0.0
        bank_at_purchases = []
        
        for purchase in purchases:
            segment_time, bank = TimeCalculator.calculate_segment_time(
                bank, 
                purchase.cost, 
                current_time,
                state.click_value(),
                state.total_cpms_with_clicks()
            )
            
            if segment_time == float('inf'):
                return float('inf'), state, []
            
            total_time += segment_time
            current_time += segment_time
            purchase.time_purchased = current_time
            purchase.bank_before = bank
            
            bank -= purchase.cost
            bank_at_purchases.append(bank)
            
            if purchase.type == 'building':
                state.purchase_building(purchase.name)
            else:
                state.purchase_upgrade(purchase.name)
        
        return total_time, state, bank_at_purchases

class CombinationGenerator:
    """Generates all viable purchase combinations for a given goal"""
    
    def __init__(self, goal: float):
        self.goal = goal
        self.affordable_buildings = self._get_affordable_buildings()
        self.combinations_generated = 0
        self.combinations_pruned = 0
        
    def _get_affordable_buildings(self) -> List[str]:
        """Get list of building types that are affordable within the goal"""
        affordable = []
        for name, building in BUILDINGS.items():
            max_n = building.max_affordable(self.goal)
            if max_n > 0:
                affordable.append(name)
        return sorted(affordable, key=lambda x: BUILDINGS[x].base_price)
    
    def _get_affordable_upgrades(self, building_name: str, 
                                available_cookies: float, 
                                owned_buildings: int) -> int:
        """Get maximum number of affordable upgrades for a building"""
        max_upgrades = 0
        for i, upgrade in enumerate(UPGRADES.get(building_name, [])):
            if upgrade.is_unlocked(owned_buildings):
                if upgrade.cost <= available_cookies:
                    max_upgrades += 1
                    available_cookies -= upgrade.cost
                else:
                    break
        return max_upgrades
    
    def generate_combinations(self) -> Set[PathCombination]:
        """Generate all viable purchase combinations"""
        if not self.affordable_buildings:
            return {PathCombination({}, {})}
        
        combinations = set()
        
        self._generate_recursive(
            remaining_cookies=self.goal,
            building_idx=0,
            current_buildings={b: 0 for b in BUILDINGS},
            current_upgrades={b: 0 for b in BUILDINGS},
            combinations=combinations
        )
        
        return combinations
    
    def _generate_recursive(self, remaining_cookies: float, building_idx: int,
                           current_buildings: Dict[str, int],
                           current_upgrades: Dict[str, int],
                           combinations: Set[PathCombination]):
        """Recursive combination generation"""
        
        if building_idx >= len(self.affordable_buildings):
            if self._is_viable_combination(current_buildings, current_upgrades, remaining_cookies):
                comb = PathCombination(
                    current_buildings.copy(),
                    current_upgrades.copy(),
                    remaining_cookies=remaining_cookies
                )
                combinations.add(comb)
                self.combinations_generated += 1
            else:
                self.combinations_pruned += 1
            return
        
        building_name = self.affordable_buildings[building_idx]
        building = BUILDINGS[building_name]
        
        max_buildings = building.max_affordable(remaining_cookies)
        
        for n in range(max_buildings, -1, -1):
            cost = building.total_cost(n) if n > 0 else 0
            
            if cost <= remaining_cookies:
                new_remaining = remaining_cookies - cost
                current_buildings[building_name] = n
                
                if n >= building.unlock_threshold:
                    max_upgrades = self._get_affordable_upgrades(
                        building_name, new_remaining, n
                    )
                    
                    for u in range(max_upgrades + 1):
                        upgrade_cost = 0
                        for i in range(u):
                            upgrade_cost += UPGRADES[building_name][i].cost
                        
                        if upgrade_cost <= new_remaining:
                            current_upgrades[building_name] = u
                            
                            self._generate_recursive(
                                new_remaining - upgrade_cost,
                                building_idx + 1,
                                current_buildings,
                                current_upgrades,
                                combinations
                            )
                else:
                    current_upgrades[building_name] = 0
                    self._generate_recursive(
                        new_remaining,
                        building_idx + 1,
                        current_buildings,
                        current_upgrades,
                        combinations
                    )
        
        current_buildings[building_name] = 0
        current_upgrades[building_name] = 0
    
    def _is_viable_combination(self, buildings: Dict[str, int],
                              upgrades: Dict[str, int],
                              remaining: float) -> bool:
        """Check if a combination is viable (no wasted opportunity cost)"""
        if all(v == 0 for v in buildings.values()):
            return True
        
        for b_name in self.affordable_buildings:
            building = BUILDINGS[b_name]
            current_count = buildings[b_name]
            
            if current_count > 0:
                next_cost = building.price(current_count)
                if next_cost <= remaining:
                    return False
            
            current_upgrade_count = upgrades[b_name]
            upgrades_list = UPGRADES.get(b_name, [])
            if current_upgrade_count < len(upgrades_list):
                next_upgrade = upgrades_list[current_upgrade_count]
                if (current_count >= next_upgrade.unlocks_at and 
                    next_upgrade.cost <= remaining):
                    return False
        
        return True

class PermutationOptimizer:
    """Finds optimal ordering for a given combination of purchases"""
    
    def __init__(self, goal: float):
        self.goal = goal
        self.cache = {}
        self.permutations_evaluated = 0
        self.pruned_count = 0
    
    def find_fastest_permutation(self, combination: PathCombination) -> Tuple[List[Purchase], float]:
        """Find the fastest ordering of purchases for a given combination"""
        purchases = []
        
        # Add building purchases
        for b_name, count in combination.buildings.items():
            for i in range(count):
                cost = BUILDINGS[b_name].price(i)
                purchases.append(Purchase('building', b_name, cost, -1))
        
        # Add upgrade purchases
        for b_name, upgrade_count in combination.upgrades.items():
            for i in range(upgrade_count):
                if b_name in UPGRADES and i < len(UPGRADES[b_name]):
                    cost = UPGRADES[b_name][i].cost
                    purchases.append(Purchase('upgrade', b_name, cost, i))
        
        if not purchases:
            return [], 0.0
        
        return self._branch_and_bound_search(purchases, combination)
    
    def _branch_and_bound_search(self, purchases: List[Purchase], 
                                combination: PathCombination) -> Tuple[List[Purchase], float]:
        """Branch and bound search for optimal ordering"""
        best_time = float('inf')
        best_sequence = None
        
        from collections import Counter
        purchase_counter = Counter(purchases)
        unique_purchases = list(purchase_counter.keys())
        purchase_counts = {p: purchase_counter[p] for p in unique_purchases}
        unique_purchases.sort(key=lambda p: p.cost)
        
        def dfs(sequence, state, bank, current_time, remaining_counts):
            nonlocal best_time, best_sequence
            
            if current_time >= best_time:
                self.pruned_count += 1
                return
            
            if all(count == 0 for count in remaining_counts.values()):
                if current_time < best_time:
                    best_time = current_time
                    best_sequence = sequence.copy()
                return
            
            for purchase in unique_purchases:
                count = remaining_counts[purchase]
                if count == 0:
                    continue
                
                if purchase.type == 'upgrade':
                    current_upgrade_count = state.upgrades[purchase.name]
                    if purchase.upgrade_index != current_upgrade_count:
                        continue
                    
                    upgrades_list = UPGRADES.get(purchase.name, [])
                    if purchase.upgrade_index >= len(upgrades_list):
                        continue
                    
                    if state.buildings[purchase.name] < upgrades_list[purchase.upgrade_index].unlocks_at:
                        continue
                
                segment_time, new_bank = TimeCalculator.calculate_segment_time(
                    bank, 
                    purchase.cost, 
                    current_time,
                    state.click_value(),
                    state.total_cpms_with_clicks()
                )
                
                if segment_time == float('inf'):
                    self.pruned_count += 1
                    continue
                
                new_time = current_time + segment_time
                new_bank_val = new_bank - purchase.cost
                new_sequence = sequence + [purchase]
                new_state = state.copy()
                
                if purchase.type == 'building':
                    new_state.purchase_building(purchase.name)
                else:
                    new_state.purchase_upgrade(purchase.name)
                
                new_remaining = remaining_counts.copy()
                new_remaining[purchase] -= 1
                
                dfs(new_sequence, new_state, new_bank_val, new_time, new_remaining)
        
        remaining = {p: purchase_counts[p] for p in unique_purchases}
        dfs([], ProductionState(), 0.0, 0.0, remaining)
        
        if best_sequence is None:
            sorted_purchases = sorted(purchases, key=lambda x: (x.cost, x.type))
            time, _, _ = TimeCalculator.calculate_permutation_time(sorted_purchases, self.goal)
            return sorted_purchases, time
        
        return best_sequence, best_time * 1000

class OptimalPathFinder:
    """Main class to find optimal path to any goal"""
    
    def __init__(self, goal: float):
        self.goal = goal
        self.combination_generator = CombinationGenerator(goal)
        self.permutation_optimizer = PermutationOptimizer(goal)
        
    def find_optimal_path(self) -> Tuple[List[Purchase], float, PathCombination]:
        """Find the absolute fastest path to the goal"""
        print(f"\n📊 PHASE 1: GENERATING PURCHASE COMBINATIONS")
        print("-" * 40)
        
        # Check affordable buildings first
        affordable = []
        for name, building in BUILDINGS.items():
            max_n = building.max_affordable(self.goal)
            if max_n > 0:
                affordable.append(f"{name}: {max_n}")
        
        if affordable:
            print(f"   Affordable buildings: {', '.join(affordable)}")
        else:
            print("   No buildings affordable within this goal.")
        
        combinations = self.combination_generator.generate_combinations()
        non_empty_combinations = [c for c in combinations if not (all(v == 0 for v in c.buildings.values()))]
        
        if not non_empty_combinations:
            print("\n⚠️  No viable purchase combinations found. Just clicking to goal.")
            clicks_needed = math.ceil(self.goal / CURSOR_BASE_CLICK_VALUE)
            time_needed = clicks_needed * CLICK_COOLDOWN
            return [], time_needed, PathCombination({}, {})
        
        print(f"\n📈 Found {len(combinations)} total combinations")
        print(f"   • {len(non_empty_combinations)} contain purchases")
        
        # Show sample combinations
        print("\n📋 Sample combinations:")
        sample_size = min(3, len(non_empty_combinations))
        for i, comb in enumerate(sorted(non_empty_combinations, key=lambda c: c.total_cost)[:sample_size]):
            print(f"   {i+1}. {comb}")
        
        print(f"\n⚡ PHASE 2: OPTIMIZING PERMUTATIONS")
        print("-" * 40)
        
        tracker = ProgressTracker(len(non_empty_combinations), "combinations")
        
        best_time = float('inf')
        best_sequence = None
        best_combination = None
        
        # Sort by production potential
        def combination_score(comb):
            state = comb.get_final_state()
            return -state.total_cpms_with_clicks()
        
        non_empty_combinations.sort(key=combination_score)
        
        for i, combination in enumerate(non_empty_combinations):
            desc = combination.get_description()
            tracker.update(current_item=f"{desc} ({i+1}/{len(non_empty_combinations)})")
            
            sequence, time_to_last = self.permutation_optimizer.find_fastest_permutation(combination)
            
            if time_to_last < best_time and sequence:
                final_state = combination.get_final_state()
                bank_at_last = sequence[-1].bank_before - sequence[-1].cost
                last_purchase_time = sequence[-1].time_purchased
                
                segment_time, _ = TimeCalculator.calculate_segment_time(
                    bank_at_last,
                    self.goal,
                    last_purchase_time,
                    final_state.click_value(),
                    final_state.total_cpms_with_clicks()
                )
                
                total_time = time_to_last + segment_time
                
                if total_time < best_time:
                    best_time = total_time
                    best_sequence = sequence
                    best_combination = combination
                    tracker.set_best(total_time, combination)
            
            tracker.combinations_explored = len(non_empty_combinations[:i+1])
            tracker.permutations_explored = self.permutation_optimizer.permutations_evaluated
            tracker.pruned_count = self.permutation_optimizer.pruned_count
        
        tracker.finish()
        return best_sequence, best_time, best_combination

class GameSimulator:
    """Perfect simulation for verification"""
    
    @staticmethod
    def simulate(sequence: List[Purchase], goal: float) -> float:
        """Perfect discrete simulation of the game"""
        state = ProductionState()
        bank = 0.0
        time_ms = 0.0
        last_click_time = -CLICK_COOLDOWN
        last_frame_time = 0.0
        
        purchase_index = 0
        next_purchase_cost = sequence[0].cost if sequence else float('inf')
        
        while bank < goal:
            # Process clicks
            can_click = time_ms - last_click_time >= CLICK_COOLDOWN - 0.001
            if can_click:
                bank += state.click_value()
                last_click_time = time_ms
            
            # Process frames
            if time_ms - last_frame_time >= MILLISECONDS_PER_FRAME - 0.001:
                bank += state.total_cpf()
                last_frame_time = time_ms
            
            # Check for purchases
            if purchase_index < len(sequence) and bank >= next_purchase_cost - 0.001:
                purchase = sequence[purchase_index]
                bank -= purchase.cost
                purchase.bank_before = bank + purchase.cost
                purchase.time_purchased = time_ms
                
                if purchase.type == 'building':
                    state.purchase_building(purchase.name)
                else:
                    state.purchase_upgrade(purchase.name)
                
                purchase_index += 1
                if purchase_index < len(sequence):
                    next_purchase_cost = sequence[purchase_index].cost
                else:
                    next_purchase_cost = float('inf')
            
            time_ms += 1
            
            # Safety check
            if time_ms > 10000000:
                break
        
        return time_ms

def format_time(ms: float) -> str:
    """Format milliseconds into readable time"""
    if ms < 1000:
        return f"{ms:.2f} ms"
    elif ms < 60000:
        return f"{ms/1000:.2f} seconds"
    elif ms < 3600000:
        return f"{ms/60000:.2f} minutes"
    else:
        return f"{ms/3600000:.2f} hours"

def get_user_goal() -> float:
    """Get goal from user input"""
    print("\n🍪 COOKIE CLICKER - OPTIMAL PATH CALCULATOR")
    print("="*60)
    print("\nThis program finds the mathematically optimal sequence of")
    print("purchases to reach any cookie goal as fast as possible.\n")
    
    while True:
        try:
            goal_str = input("Enter your cookie goal (e.g., 1000, 5000, 10000): ").strip()
            goal_str = goal_str.replace(',', '')  # Remove commas
            goal = float(goal_str)
            
            if goal <= 0:
                print("❌ Goal must be greater than 0.")
                continue
                
            if goal > 1000000:
                print("⚠️  Warning: Large goals may take significant time to compute.")
                confirm = input("Continue anyway? (y/n): ").lower()
                if confirm != 'y':
                    continue
                    
            return goal
            
        except ValueError:
            print("❌ Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            exit(0)

def main():
    """Main function - runs once with user input"""
    
    goal = get_user_goal()
    
    print(f"\n" + "="*60)
    print(f"🎯 OPTIMIZING FOR: {goal:,.0f} COOKIES")
    print("="*60)
    
    start_time = time.time()
    
    finder = OptimalPathFinder(goal)
    sequence, total_time, combination = finder.find_optimal_path()
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*60)
    print("🎉 OPTIMAL PATH FOUND!")
    print("="*60)
    
    if sequence:
        print(f"\n📦 COMBINATION: {combination}")
        print(f"⏱️  TOTAL TIME: {format_time(total_time)}")
        print(f"🔢 PURCHASES: {len(sequence)}")
        
        final_state = combination.get_final_state()
        cps = final_state.total_cpms_with_clicks() * 1000
        print(f"⚡ FINAL CPS: {cps:.1f}")
        
        print(f"\n📋 PURCHASE SEQUENCE:")
        print("-" * 40)
        
        # Show all purchases with nice formatting
        for i, p in enumerate(sequence):
            time_sec = p.time_purchased / 1000
            print(f"   {i+1:2d}. {p}  (t={time_sec:6.2f}s, bank=${p.bank_before:7.0f})")
        
        # Verification for small goals
        if goal <= 10000:
            print(f"\n🔍 VERIFYING WITH PERFECT SIMULATION...")
            sim_time = GameSimulator.simulate(sequence, goal)
            error = abs(total_time - sim_time)
            error_pct = (error / total_time * 100) if total_time > 0 else 0
            
            print(f"   Calculated: {format_time(total_time)}")
            print(f"   Simulated:  {format_time(sim_time)}")
            print(f"   Error: {error:.2f}ms ({error_pct:.4f}%)")
            
            if error_pct < 0.1:
                print(f"   ✅ Verification passed (error < 0.1%)")
    
    else:
        clicks_needed = math.ceil(goal / CURSOR_BASE_CLICK_VALUE)
        time_needed = clicks_needed * CLICK_COOLDOWN
        print(f"\n⚠️  No purchases needed - just click the big cookie!")
        print(f"   Time required: {format_time(time_needed)}")
        print(f"   Clicks required: {clicks_needed}")
    
    print(f"\n⏱️  COMPUTATION TIME: {elapsed:.2f} seconds")
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()