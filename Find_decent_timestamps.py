import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# === CONFIG ===
FILE_PATH = "C:/Users/colto/Downloads/harpyV2_trotting_4_2025-05-16.csv"
SAMPLING_RATE = 500  # Hz
SPEED_THRESHOLD = 0.025  # m/s (adjustable)
SMOOTH_WINDOW = 10  # number of frames for smoothing

# === Load data ===
# Use headers if known
headers = None
df = pd.read_csv(FILE_PATH, names=headers, header=0)

dt = 1 / SAMPLING_RATE
time = np.arange(0, len(df) * dt, dt)

# === Compute foot velocities in x-z plane ===
left_dx = np.gradient(df['x_l'], dt)
left_dz = np.gradient(df['z_l'], dt)
right_dx = np.gradient(df['x_r'], dt)
right_dz = np.gradient(df['z_r'], dt)

left_speed = np.sqrt(left_dx**2 + left_dz**2)
right_speed = np.sqrt(right_dx**2 + right_dz**2)

# === Motion detection based on threshold ===
is_moving = (left_speed > SPEED_THRESHOLD) | (right_speed > SPEED_THRESHOLD)

# Optional: smooth with moving average
is_moving_smoothed = pd.Series(is_moving).rolling(window=SMOOTH_WINDOW, center=True).max().fillna(0).astype(bool)

# === Detect motion time segments ===
movement_times = []
in_motion = False
for i, moving in enumerate(is_moving_smoothed):
    if moving and not in_motion:
        in_motion = True
        start_time = i * dt
    elif not moving and in_motion:
        in_motion = False
        end_time = i * dt
        movement_times.append((start_time, end_time))

# Handle case if motion ends at last frame
if in_motion:
    movement_times.append((start_time, len(is_moving_smoothed) * dt))

# === Output detected motion times ===
print("Detected motion time ranges (s):")
for start, end in movement_times:
    duration = end - start
    if duration >= 5:
            print(f"  From {start:.2f} to {end:.2f} (Duration: {end - start:.2f} s)")

test_number = df['test_number'].to_numpy()
test_change_indices = np.where(np.diff(test_number) > 0)[0] + 1  # +1 because diff shifts index

test_change_times = test_change_indices * dt

print("Times when a new test started (s):")
for i, t in enumerate(test_change_times):
    print(f"  Test {test_number[test_change_indices[i]]} started at {t:.2f} s")

# === Plot foot speeds ===
plt.figure(figsize=(12, 4))
plt.plot(time[:len(left_speed)], left_speed, label='Left Foot Speed', alpha=0.7)
plt.plot(time[:len(right_speed)], right_speed, label='Right Foot Speed', alpha=0.7)
plt.axhline(SPEED_THRESHOLD, color='k', linestyle='--', label='Threshold')
plt.xlabel('Time (s)')
plt.ylabel('Speed (m/s)')
plt.title('Left and Right Foot Speeds Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
