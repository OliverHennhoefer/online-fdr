import sys
import random
import matplotlib.pyplot as plt

from online_fdr.investing.addis.addis import Addis
from online_fdr.investing.lond.lond import Lond
from online_fdr.investing.lord.dependent import LordDependent
from online_fdr.investing.lord.mem_decay import LORDMemoryDecay
from online_fdr.investing.lord.three import LordThree
from online_fdr.investing.saffron.saffron import Saffron

p_vals = [random.random() for _ in range(1000)]
p_vals[100] = sys.float_info.min
p_vals[250] = sys.float_info.min
p_vals[800] = sys.float_info.min

lond_dep = Lond(alpha=0.05, original=True, dependent=True)
lond_dep_traj: [float] = []

lond = Lond(alpha=0.05, original=True, dependent=False)
lond_traj: [float] = []

lord3 = LordThree(alpha=0.05, wealth=0.025, reward=0.025)
lord3_traj = []

memlord =  LORDMemoryDecay(alpha=0.05, wealth=0.025, delta = 0.99, eta = 1)
memlord_traj = []

saffron = Saffron(alpha=0.05, wealth=0.025, lambda_=0.5)
saffron_traj = []

addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)
addis_traj = []

for p_val in p_vals:

    # Dependent LOND
    lond_dep.test_one(p_val)
    lond_dep_traj.append(lond_dep.alpha)

    # Default LOND
    lond.test_one(p_val)
    lond_traj.append(lond.alpha)

    # LORD 3
    lord3.test_one(p_val)
    lord3_traj.append(lord3.alpha)

    # memLORD
    memlord.test_one(p_val)
    memlord_traj.append(memlord.alpha)

    # SAFFRON
    saffron.test_one(p_val)
    saffron_traj.append(saffron.alpha)

    # ADDIS
    addis.test_one(p_val)
    addis_traj.append(addis.alpha)

name = ['LOND_dep', 'LOND', 'LORD', 'memLORD', 'SAFFRON', 'ADDIS']
data = [lond_dep_traj, lond_traj, lord3_traj, memlord_traj, saffron_traj, addis_traj]

num_plots = len(data)
rows = min(3, (num_plots + 2) // 3)  # Ensure rows are 1-3
cols = min(3, num_plots)  # Ensure cols are 1-3

# Create subplots
fig, axes = plt.subplots(rows, cols, figsize=(15, 10))
axes = axes.flatten()  # Flatten to handle as a 1D array

# Plot each list in its own subplot
for idx, (lst, method) in enumerate(zip(data, name)):
    axes[idx].plot(lst, label=f'{method}')
    axes[idx].set_title(f'{method}')
    axes[idx].set_xlabel('Index')
    axes[idx].set_ylabel('Value')
    axes[idx].set_ylim(0, 0.012)
    axes[idx].legend()
    axes[idx].grid(True)

# Hide any unused subplots
for ax in axes[num_plots:]:
    ax.axis('off')

# Adjust layout to prevent overlap
plt.tight_layout()

# Show the plot
plt.show()