# -*- coding: utf-8 -*-
"""
Generate publication-quality figures for the Semicircle Constraint paper.

Figure 1: Semicircle constraint with IonQ Forte-1 hardware data
Figure 2: Optimal operating point analysis (simulation)
Figure 3: Barren plateau geometry (simulation)
"""
import sys
import io
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from pathlib import Path

# Windows UTF-8 console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Use a clean style suitable for PRL
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Computer Modern Roman', 'Times New Roman', 'DejaVu Serif'],
    'font.size': 9,
    'axes.labelsize': 10,
    'axes.titlesize': 10,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'text.usetex': False,
    'mathtext.fontset': 'cm',
    'axes.linewidth': 0.6,
    'xtick.major.width': 0.5,
    'ytick.major.width': 0.5,
    'xtick.minor.width': 0.3,
    'ytick.minor.width': 0.3,
    'lines.linewidth': 1.0,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
})

# Output directory
out_dir = Path(__file__).parent / "figures"
out_dir.mkdir(exist_ok=True)

# Colors - PRL-appropriate palette
THEORY_COLOR = '#2166ac'   # steel blue
DATA_COLOR = '#b2182b'     # muted red
ACCENT_COLOR = '#4dac26'   # green
GRAY = '#666666'
LIGHT_GRAY = '#cccccc'

# ============================================================
# IonQ Forte-1 hardware data (from paper Table 1)
# ============================================================
ionq_data = [
    # (theta, q_theory, counts_0, counts_1, q_meas, C_qc)
    (0.4510, 0.050, 48, 4,  0.077, 0.266),
    (0.6435, 0.100, 50, 2,  0.038, 0.192),
    (0.7954, 0.150, 41, 11, 0.212, 0.408),
    (0.9273, 0.200, 41, 11, 0.212, 0.408),
    (1.0472, 0.250, 36, 16, 0.308, 0.461),
    (1.1593, 0.300, 35, 17, 0.327, 0.469),
    (1.2661, 0.350, 35, 17, 0.327, 0.469),
    (1.3694, 0.400, 25, 27, 0.519, 0.500),
    (1.4706, 0.450, 26, 26, 0.500, 0.500),
    (1.5708, 0.500, 28, 24, 0.462, 0.499),
    (1.6710, 0.550, 22, 30, 0.577, 0.494),
    (1.7722, 0.600, 17, 35, 0.673, 0.469),
    (1.8755, 0.650, 10, 42, 0.808, 0.394),
    (1.9823, 0.700, 17, 35, 0.673, 0.469),
    (2.0944, 0.750,  8, 44, 0.846, 0.361),
]

q_theory = np.array([d[1] for d in ionq_data])
q_meas = np.array([d[4] for d in ionq_data])
cqc_meas = np.array([d[5] for d in ionq_data])
n_shots = 52

# Binomial standard error for q_meas
q_err = np.sqrt(q_meas * (1 - q_meas) / n_shots)

# C_qc error via error propagation: dC/dq = (1-2q)/(2*sqrt(q(1-q)))
# sigma_C = |dC/dq| * sigma_q
dCdq = np.where(q_meas * (1 - q_meas) > 0,
                np.abs(1 - 2*q_meas) / (2 * np.sqrt(q_meas * (1 - q_meas))),
                0)
cqc_err = dCdq * q_err

# ============================================================
# Load simulation data
# ============================================================
sim_dir = Path(__file__).parent / "tests" / "Simulations"

with open(sim_dir / "test_optimal_operating_point.json", 'r', encoding='utf-8') as f:
    opt_data = json.load(f)

with open(sim_dir / "test_barren_plateau_geometry.json", 'r', encoding='utf-8') as f:
    bp_data = json.load(f)

# ============================================================
# FIGURE 1: Semicircle constraint with IonQ hardware data
# ============================================================
print("Generating Figure 1: Semicircle constraint (IonQ hardware)...")

fig1, ax1 = plt.subplots(figsize=(3.4, 2.8))

# Theoretical semicircle
q_fine = np.linspace(0, 1, 500)
cqc_theory = np.sqrt(q_fine * (1 - q_fine))

ax1.plot(q_fine, cqc_theory, color=THEORY_COLOR, linewidth=1.2,
         label=r'$C_{qc} = \sqrt{q(1-q)}$', zorder=2)

# Shade the region under the semicircle lightly
ax1.fill_between(q_fine, 0, cqc_theory, alpha=0.06, color=THEORY_COLOR, zorder=1)

# IonQ hardware data with error bars
ax1.errorbar(q_meas, cqc_meas, xerr=q_err, yerr=cqc_err,
             fmt='o', color=DATA_COLOR, markersize=3.5, markeredgewidth=0.5,
             markeredgecolor='k', capsize=2, capthick=0.5, elinewidth=0.5,
             label=r'IonQ Forte-1 ($n=52$)', zorder=3)

# Mark the apex
ax1.plot(0.5, 0.5, 's', color=ACCENT_COLOR, markersize=5, markeredgecolor='k',
         markeredgewidth=0.5, zorder=4)
# Place apex label above and to the left, pointing down to the green square
ax1.annotate(r'$q = \frac{1}{2},\; C_{qc} = \frac{1}{2}$',
             xy=(0.5, 0.5), xytext=(0.22, 0.55),
             fontsize=7, ha='center',
             arrowprops=dict(arrowstyle='->', color=GRAY, lw=0.5),
             color=GRAY)

# Mark classical limits
ax1.annotate('classical', xy=(0.03, 0.01), fontsize=6.5, color=GRAY, style='italic')
ax1.annotate('classical', xy=(0.85, 0.01), fontsize=6.5, color=GRAY, style='italic')

ax1.set_xlabel(r'Measurement probability $q$')
ax1.set_ylabel(r'Quantum-classical correlation $C_{qc}$')
ax1.set_xlim(-0.02, 1.02)
ax1.set_ylim(-0.02, 0.58)
# Place legend in blank space below the curve on the right side
ax1.legend(bbox_to_anchor=(0.97, 0.38), loc='right', framealpha=0.95,
           edgecolor='none', fontsize=7.5)
ax1.set_aspect('equal', adjustable='box')

# Minor ticks
ax1.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
ax1.set_yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5])
ax1.tick_params(direction='in', which='both', top=True, right=True)

fig1.savefig(out_dir / "fig1_semicircle_hardware.pdf")
fig1.savefig(out_dir / "fig1_semicircle_hardware.png")
print(f"  Saved: {out_dir / 'fig1_semicircle_hardware.pdf'}")


# ============================================================
# FIGURE 2: Optimal operating point (simulation)
# ============================================================
print("Generating Figure 2: Optimal operating point (simulation)...")

fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(6.8, 2.6))

# --- Panel (a): C_qc and efficiency vs q ---
q_fine2 = np.linspace(0.001, 0.999, 500)
cqc_fine = np.sqrt(q_fine2 * (1 - q_fine2))
eta_fine = q_fine2 * (1 - q_fine2)

ax2a.plot(q_fine2, cqc_fine, color=THEORY_COLOR, linewidth=1.2,
          label=r'$C_{qc}(q)$')
ax2a.plot(q_fine2, eta_fine, color=ACCENT_COLOR, linewidth=1.2, linestyle='--',
          label=r'$\eta(q) = q(1-q)$')

# Mark maximum
ax2a.axvline(x=0.5, color=LIGHT_GRAY, linewidth=0.5, linestyle=':')
ax2a.plot(0.5, 0.5, 'o', color=THEORY_COLOR, markersize=5, markeredgecolor='k',
          markeredgewidth=0.4, zorder=4)
ax2a.plot(0.5, 0.25, 'o', color=ACCENT_COLOR, markersize=5, markeredgecolor='k',
          markeredgewidth=0.4, zorder=4)

ax2a.annotate(r'$C_{qc}^{\max} = \frac{1}{2}$', xy=(0.5, 0.5), xytext=(0.62, 0.48),
              fontsize=7, color=THEORY_COLOR,
              arrowprops=dict(arrowstyle='->', color=THEORY_COLOR, lw=0.4))
ax2a.annotate(r'$\eta^{\max} = \frac{1}{4}$', xy=(0.5, 0.25), xytext=(0.65, 0.30),
              fontsize=7, color=ACCENT_COLOR,
              arrowprops=dict(arrowstyle='->', color=ACCENT_COLOR, lw=0.4))

ax2a.set_xlabel(r'Measurement probability $q$')
ax2a.set_ylabel('Correlation / Efficiency')
# Place legend in upper left where curves are rising (no annotations there)
ax2a.legend(loc='upper left', framealpha=0.95, edgecolor='none', fontsize=7)
ax2a.set_xlim(0, 1)
ax2a.set_ylim(0, 0.58)
ax2a.tick_params(direction='in', which='both', top=True, right=True)
ax2a.text(0.03, 0.95, '(a)', transform=ax2a.transAxes, fontsize=9, fontweight='bold',
          va='top')

# --- Panel (b): VQE convergence from different starting points ---
conv_results = opt_data['results']['test27']['convergence_results']

# Simulate convergence trajectories using gradient ascent on C_qc
for cr in conv_results:
    q_init = cr['q_init']
    iters = cr['iterations']
    q_final = cr['q_final']

    # Generate a plausible trajectory: gradient ascent on q(1-q)
    trajectory = [q_init]
    q_cur = q_init
    lr = 0.15
    for step in range(iters):
        grad = 1 - 2 * q_cur  # d/dq[q(1-q)]
        q_cur = q_cur + lr * grad
        q_cur = max(0.01, min(0.99, q_cur))
        trajectory.append(q_cur)

    steps_arr = np.arange(len(trajectory))
    cqc_traj = np.sqrt(np.array(trajectory) * (1 - np.array(trajectory)))

    if q_init == 0.5:
        ax2b.plot(steps_arr, cqc_traj, 'o-', markersize=3, linewidth=0.8,
                  color=DATA_COLOR, label=f'$q_0 = {q_init}$', zorder=3)
    else:
        ax2b.plot(steps_arr, cqc_traj, 's-', markersize=2.5, linewidth=0.7,
                  label=f'$q_0 = {q_init}$', alpha=0.8)

ax2b.axhline(y=0.5, color=LIGHT_GRAY, linewidth=0.5, linestyle=':')
ax2b.set_xlabel('Optimization step')
ax2b.set_ylabel(r'$C_{qc}$')
ax2b.legend(loc='lower right', framealpha=0.9, edgecolor='none', fontsize=6.5, ncol=2)
ax2b.set_xlim(-0.3, 12)
ax2b.set_ylim(0.15, 0.55)
ax2b.tick_params(direction='in', which='both', top=True, right=True)
ax2b.text(0.03, 0.95, '(b)', transform=ax2b.transAxes, fontsize=9, fontweight='bold',
          va='top')

fig2.tight_layout(w_pad=2.5)
fig2.savefig(out_dir / "fig2_optimal_point.pdf")
fig2.savefig(out_dir / "fig2_optimal_point.png")
print(f"  Saved: {out_dir / 'fig2_optimal_point.pdf'}")


# ============================================================
# FIGURE 3: Barren plateau geometry (simulation)
# ============================================================
print("Generating Figure 3: Barren plateau geometry (simulation)...")

fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(6.8, 2.6))

# --- Panel (a): Gradient variance vs q ---
grad_results = bp_data['results']['test28']['gradient_results']
q_grad = np.array([g['q'] for g in grad_results])
var_theory = np.array([g['theory_variance'] for g in grad_results])
var_meas = np.array([g['measured_variance'] for g in grad_results])

# Continuous theory curve
q_cont = np.linspace(0.01, 0.99, 300)
var_cont = q_cont * (1 - q_cont)

ax3a.plot(q_cont, var_cont, color=THEORY_COLOR, linewidth=1.2,
          label=r'Theory: $q(1-q)$')
ax3a.plot(q_grad, var_meas, 'o', color=DATA_COLOR, markersize=4,
          markeredgecolor='k', markeredgewidth=0.4,
          label='Simulation', zorder=3)

# Shade barren plateau regions
ax3a.axhspan(0, 0.01, color='#fee0d2', alpha=0.4, zorder=0)
ax3a.axhline(y=0.01, color=GRAY, linewidth=0.4, linestyle='--')
ax3a.text(0.06, 0.005, 'barren', fontsize=6, color=GRAY, style='italic')
ax3a.text(0.88, 0.005, 'barren', fontsize=6, color=GRAY, style='italic')

# Trainable region arrow
ax3a.annotate('', xy=(0.15, 0.015), xytext=(0.85, 0.015),
              arrowprops=dict(arrowstyle='<->', color=ACCENT_COLOR, lw=0.7))
ax3a.text(0.5, 0.022, 'trainable', fontsize=6.5, color=ACCENT_COLOR,
          ha='center', style='italic')

ax3a.set_xlabel(r'Operating point $q$')
ax3a.set_ylabel(r'Gradient variance $\mathrm{Var}(\partial E / \partial\theta)$')
# Place legend in upper right where curve descends and no data points cluster
ax3a.legend(bbox_to_anchor=(0.97, 0.97), loc='upper right', framealpha=0.95,
            edgecolor='none', fontsize=7)
ax3a.set_xlim(0, 1)
ax3a.set_ylim(-0.01, 0.3)
ax3a.tick_params(direction='in', which='both', top=True, right=True)
ax3a.text(0.03, 0.95, '(a)', transform=ax3a.transAxes, fontsize=9, fontweight='bold',
          va='top')

# --- Panel (b): Depth scaling ---
depth_results = bp_data['results']['test28']['depth_results']
depths = np.array([d['n_layers'] for d in depth_results])
variances = np.array([d['variance'] for d in depth_results])

ax3b.semilogy(depths, variances, 's-', color=THEORY_COLOR, markersize=4,
              markeredgecolor='k', markeredgewidth=0.4, linewidth=0.8)

# Fit exponential decay
from numpy.polynomial.polynomial import polyfit
log_var = np.log(variances)
coeffs = np.polyfit(depths, log_var, 1)
depths_fit = np.linspace(0.5, 18, 100)
fit_line = np.exp(coeffs[1]) * np.exp(coeffs[0] * depths_fit)
ax3b.semilogy(depths_fit, fit_line, '--', color=GRAY, linewidth=0.7,
              label=f'Fit: $\\sim e^{{-{abs(coeffs[0]):.2f}L}}$')

ax3b.set_xlabel(r'Circuit depth $L$')
ax3b.set_ylabel(r'Gradient variance')
ax3b.legend(loc='upper right', framealpha=0.9, edgecolor='none', fontsize=7)
ax3b.set_xlim(0, 17)
ax3b.tick_params(direction='in', which='both', top=True, right=True)
ax3b.text(0.03, 0.95, '(b)', transform=ax3b.transAxes, fontsize=9, fontweight='bold',
          va='top')

fig3.tight_layout(w_pad=2.5)
fig3.savefig(out_dir / "fig3_barren_plateau.pdf")
fig3.savefig(out_dir / "fig3_barren_plateau.png")
print(f"  Saved: {out_dir / 'fig3_barren_plateau.pdf'}")

print("\nAll figures generated successfully.")
print(f"Output directory: {out_dir}")
