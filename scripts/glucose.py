from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from scipy.integrate import simps


def simulate_cumulative_glucose(events, total_hours=6):
    # This version models glucose using a basic differential equation:
    # dG/dt = -k_insulin * (G - baseline) + carb_input(t) - activity_effect(t)
    # where:
    # - G is glucose level
    # - baseline is 100 mg/dL
    # - k_insulin controls how quickly the body returns glucose to baseline
    # - carb_input(t) is the carb absorption curve
    # - activity_effect(t) is the exercise glucose-lowering effect

    times = np.arange(0, total_hours * 60 + 1, 5)
    glucose_levels = np.zeros_like(times, dtype=float)
    glucose_levels[0] = 100  # starting baseline

    #strating variables
    baseline = 100
    k_insulin = 0.06  # profiles: unknown yet
    

    # For each time step, calculate cumulative glucose based on all past events
    # This uses Euler's method to get dt and also dG and add cumulatively
    for i, t in enumerate(times[1:], start=1):
        dt = times[i] - times[i - 1]
        glucose = glucose_levels[i - 1]
        carb_input = 0
        activity_burn = 0
        for event in events:
            t_event = (event["timestamp"] - events[0]["timestamp"]).total_seconds() / 60
            t_since_event = t - t_event
            if t_since_event >= 0:
                carbs = event["carbs"] or 0
                carb_input += min(carbs, 80) * 1.0 * np.exp(-t_since_event / 30) #max 80g carbs; exp decay
                if event["activity"] in ["walk", "jog", "run", "bike"]:
                    duration = min(event["duration"] or 0, 60) 
                    activity_burn += duration * 1.0 * np.exp(-t_since_event / 40) #max 60min; exp decay

        # Uses Euler's method to plot the next point
        dG = -k_insulin * (glucose - baseline) + carb_input - activity_burn
        # glucose - baseline: pulls things to baseline 
        # g(t) would be (glucose-baseline) * e^((-k_insulin)(t)) and models exponential decay to baseline
        glucose_levels[i] = max(glucose + dG * dt / 5, 40)  # Prevent values below 40
    
    plot_glucose(times, glucose_levels)
    return times, glucose_levels

def display_calculus(glucose_levels, times):
    t = sp.Symbol('t')
    
    # Uses computer to fit a 5-degree polynomial
    coeffs = np.polyfit(times, glucose_levels, deg=min(len(times) - 1, 5))
    
    G = sum(c * t**i for i, c in enumerate(reversed(coeffs)))
    print("\n\n\nComputer-generated Symbolic Glucose Function:")
    sp.pprint(G, use_unicode=True)
    
    dG = sp.diff(G, t)
    print("Computer-generated Derivative (Glucose Rate of Change):")
    sp.pprint(dG, use_unicode=True)

    # Integrals
    total_exposure = simps(glucose_levels, times)
    print(f"\nTotal glucose exposure (integral) over {int(times[-1])} min: {int(total_exposure)} mg·min/dL\n")
    print(f"Average glucose exposure (integral / time) over {int(times[-1])} min: {int(total_exposure) / 360} mg·min/dL")
    # very importnat for: assessing diabetes risk and risks for low/high blood sugar and insluin production 
    
    # Crit points 
    critical_points = sp.solve(dG, t)
    real_critical_points = [] # by default critical_points includes complex numbers?
    for pt in critical_points:
        if pt.is_real:
            val = pt.evalf() # turns to float
            if 0 <= val <= times[-1]:
                real_critical_points.append(val)
    print("\nCritical points (where dG/dt = 0) within time range:")
    for pt in real_critical_points:
        print(f"t = {pt:.2f} minutes") 
    # very important for assessing dips but important also critical points of max/mins where blood sugar reaches peaks 
    
    print("\n")

# legacy
"""
# --- Glucose simulation and plotting ---
def simulate_glucose(carbs, activity, duration):
    # Simple parameters
    base_glucose = 100
    carb_effect = carbs * 3  # Each gram raises glucose by 3
    activity_burn = duration * 1.5 if activity in ["walk", "jog", "run", "bike"] else 0

    # Time in minutes
    times = np.arange(0, 121, 5)
    glucose_levels = []

    for t in times:
        # Exponential decay for carbs
        carb_curve = carb_effect * np.exp(-t / 30)
        # Exponential decay for activity burn
        activity_curve = activity_burn * np.exp(-t / 40)
        glucose = base_glucose + carb_curve - activity_curve
        glucose_levels.append(glucose)

    return times, glucose_levels


def display_glucose_equation(carbs, activity, duration):
    t = sp.symbols('t')
    base = 100
    C = carbs * 3
    A = duration * 1.5 if activity in ["walk", "jog", "run", "bike"] else 0

    G = base + C * sp.exp(-t/30) - A * sp.exp(-t/40)
    dG = sp.diff(G, t)

    print("Symbolic glucose function:")
    sp.pprint(G)
    print("\nRate of change (derivative):")
    sp.pprint(dG)
    return G

"""

def plot_glucose(times, glucose_levels):
    glucose_levels = np.array(glucose_levels)  # error fix

    plt.plot(times, glucose_levels, label="Glucose Level", linewidth=2)
    # Threshold lines
    plt.axhline(y=180, color='red', linestyle='--', label='Hyperglycemia (180 mg/dL)')
    plt.axhline(y=70, color='blue', linestyle='--', label='Hypoglycemia (70 mg/dL)')
    # Shaded zones
    plt.fill_between(times, 180, glucose_levels, where=(glucose_levels >= 180), color='red', alpha=0.1)
    plt.fill_between(times, 70, glucose_levels, where=(glucose_levels <= 70), color='blue', alpha=0.1)
    # Draw the peak glucose level
    max_g = max(glucose_levels)
    max_t = times[np.argmax(glucose_levels)]
    plt.plot(max_t, max_g, 'ro')
    plt.annotate(f'Peak: {int(max_g)} mg/dL',
                 (max_t, max_g),
                 textcoords="offset points", xytext=(0,10), ha='center')
    # Labels
    plt.title("Simulated Blood Glucose Over Time")
    plt.xlabel("Time (minutes)")
    plt.ylabel("Glucose (mg/dL)")
    plt.grid(True)
    plt.legend()
    plt.show()