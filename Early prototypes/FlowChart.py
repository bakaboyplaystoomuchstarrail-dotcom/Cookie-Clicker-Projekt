import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import ConvexHull

# Building parameters (from your IA)
base = {'Cursor': 15, 'Grandma': 100, 'Farm': 1100}
scale = 1.15

def cost(n, base_price):
    """Total cost of n buildings of a given type using geometric series."""
    if n == 0:
        return 0
    return base_price * (scale**n - 1) / (scale - 1)

# Goal (total cookies available) – adjust to get a nice number of points
GOAL = 50000

# Estimate maximum possible number of each building type
max_c = int(np.log(1 + GOAL * (scale-1)/base['Cursor']) / np.log(scale))
max_g = int(np.log(1 + GOAL * (scale-1)/base['Grandma']) / np.log(scale))
max_f = int(np.log(1 + GOAL * (scale-1)/base['Farm']) / np.log(scale))

print(f"Searching up to: Cursors {max_c}, Grandmas {max_g}, Farms {max_f}")

# Generate all feasible triples (c, g, f) and keep Pareto-optimal (maximal) ones
points = []
for c in range(max_c + 1):
    for g in range(max_g + 1):
        for f in range(max_f + 1):
            total = cost(c, base['Cursor']) + cost(g, base['Grandma']) + cost(f, base['Farm'])
            if total <= GOAL:
                # Check if adding one more of any type would exceed the goal
                next_c = cost(c+1, base['Cursor']) + cost(g, base['Grandma']) + cost(f, base['Farm']) > GOAL
                next_g = cost(c, base['Cursor']) + cost(g+1, base['Grandma']) + cost(f, base['Farm']) > GOAL
                next_f = cost(c, base['Cursor']) + cost(g, base['Grandma']) + cost(f+1, base['Farm']) > GOAL
                if next_c and next_g and next_f:
                    points.append([c, g, f])

points = np.array(points)
print(f"Number of Pareto-optimal points: {len(points)}")

# Create 3D plot
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# Scatter plot of points
ax.scatter(points[:,0], points[:,1], points[:,2], c='blue', s=30, alpha=0.8, label='Pareto-optimal points')

# Compute convex hull to show neighbour connections
if len(points) >= 4:  # Need at least 4 points for a 3D hull
    hull = ConvexHull(points)
    # Draw edges of the hull (each simplex is a triangle)
    for simplex in hull.simplices:
        # Each simplex is a triangle, we draw its three edges
        for i in range(3):
            edge = [simplex[i], simplex[(i+1)%3]]
            ax.plot(points[edge, 0], points[edge, 1], points[edge, 2], 'r-', linewidth=1, alpha=0.5)

# Mark the corners (extreme points) with bright green stars
idx_max_c = np.argmax(points[:,0])
idx_max_g = np.argmax(points[:,1])
idx_max_f = np.argmax(points[:,2])

# Use large green stars with black edges for maximum visibility
ax.scatter(*points[idx_max_c], color='lime', s=200, marker='*', 
           edgecolor='black', linewidth=0.5, label='Max Cursors', zorder=10)
ax.scatter(*points[idx_max_g], color='lime', s=200, marker='*', 
           edgecolor='black', linewidth=0.5, label='Max Grandmas', zorder=10)
ax.scatter(*points[idx_max_f], color='lime', s=200, marker='*', 
           edgecolor='black', linewidth=0.5, label='Max Farms', zorder=10)

# Labels and title
ax.set_xlabel('Cursors', fontsize=12)
ax.set_ylabel('Grandmas', fontsize=12)
ax.set_zlabel('Farms', fontsize=12)
ax.set_title(f'Pareto Frontier for Cursors, Grandmas, Farms (Goal = {GOAL} cookies)', fontsize=14)

# Legend and viewing angle
ax.legend(loc='upper left', fontsize=10)
ax.view_init(elev=25, azim=-60)  # Adjust for a good view

plt.tight_layout()
plt.show()