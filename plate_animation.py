import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation

# === Load Data ===
data = pd.read_csv('C:/Users/colto/Documents/GradSchool/Silicon/Harpy/body_frame_points.csv')

output_folder = r"C:/Users/colto/Documents/GradSchool/Silicon/Harpy/outputs"
os.makedirs(output_folder, exist_ok=True)

# Create time array (500Hz sampling)
dt = 1 / 500
time = np.arange(0, len(data) * dt, dt)

# Time window
t_start = 256
t_end = 288
start_idx = int(t_start / dt)
end_idx = int(t_end / dt)

time_window = time[start_idx:end_idx]
data_window = data.iloc[start_idx:end_idx]
z_foot = data_window['z_bfr'].values
z_plate = data_window['z_bfp'].values

# === Precompute Touch Points ===
plate_offset = 0.013  # offset applied to plate position
touch_threshold = 0.0015  # meters, sensitivity of touch detection

touch_times = []
touch_heights = []
for i in range(len(z_foot)):
    if abs(z_foot[i] - (z_plate[i] + plate_offset)) < touch_threshold:
        touch_times.append(time_window[i])
        touch_heights.append(z_foot[i])

# === Plot Setup ===
fig, ax = plt.subplots(figsize=(10, 6))
ax.grid(True)
ax.set_xlim(time_window[0], time_window[-1] + 0.05)
ax.set_ylim(min(z_plate.min(), z_foot.min()) - 0.05, max(z_plate.max(), z_foot.max()) + 0.05)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Z Position (m)')
ax.set_title('Z Position of Foot and Plate Over Time')

# Dot and trace for foot
foot_dot = ax.scatter([], [], c='b', s=50, label='Right Foot Z')
foot_trace, = ax.plot([], [], 'b-', linewidth=1, label='Right Foot Trace')

# Rectangle and trace for plate
plate_width = 1
plate_height = -0.005
plate_dot = Rectangle((0, -0.005), plate_width, plate_height, color='red', label='Plate Z')
ax.add_patch(plate_dot)
plate_trace, = ax.plot([], [], 'r-', linewidth=1, label='Plate Trace')

# X mark for contact
x_marks = ax.scatter([], [], c='black', marker='x', s=60, label='Touch Point')

ax.legend()

# === Animation Functions ===
def init():
    foot_dot.set_offsets(np.empty((0, 2)))
    foot_trace.set_data([], [])
    plate_dot.set_xy((0, 0))
    plate_trace.set_data([], [])
    x_marks.set_offsets(np.empty((0, 2)))
    return foot_dot, foot_trace, plate_dot, plate_trace, x_marks

def update(frame):
    x = time_window[frame]
    zf = z_foot[frame]
    zp = z_plate[frame]

    # Update current dot position
    foot_dot.set_offsets([[x, zf]])

    # Update trace lines
    foot_trace.set_data(time_window[:frame+1], z_foot[:frame+1])
    plate_trace.set_data(time_window[:frame+1], z_plate[:frame+1])

    # Center the rectangle at (x, zp)
    plate_dot.set_xy((x - plate_width / 2, zp - plate_height / 2))

    # Update X markers
    x_touches = [(t, h) for t, h in zip(touch_times, touch_heights) if t <= x]
    if x_touches:
        x_marks.set_offsets(x_touches)
    else:
        x_marks.set_offsets(np.empty((0, 2)))

    return foot_dot, foot_trace, plate_dot, plate_trace, x_marks

# === Animate ===
frames = range(0, len(data_window), 5)
ani = FuncAnimation(fig, update, frames=frames, init_func=init, interval=100, blit=True)

# Save GIF
writer = animation.PillowWriter(fps=7)
ani.save(os.path.join(output_folder, 'foot_animation.gif'), writer=writer)

plt.show()
