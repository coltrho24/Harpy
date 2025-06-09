import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation
from matplotlib.patches import Circle
import matplotlib.gridspec as gridspec

# Read the foot position CSV file
data = pd.read_csv('C:/Users/colto/Downloads/result_best_3step.csv', header=None, 
                   names=['left_x', 'left_y', 'left_z', 'right_x', 'right_y', 'right_z'])

# # Read the thrust data for pitch angle
# dynamics_data = pd.read_csv('thrust_best_3step.csv', header=None)

# # Read Raibert controller data
# raibert_data = pd.read_csv('raibert_best_3step.csv', header=None)

# Create time array (500Hz sampling)
dt = 1/500
time = np.arange(0, len(data) * dt, dt)

# Find indices for t=305.2s to t=307.4s
t_start = 305.2
t_end = 307.4
start_idx = int(t_start / dt)
end_idx = int(t_end / dt)

# Extract data for the time window
time_window = time[start_idx:end_idx]
data_window = data.iloc[start_idx:end_idx]
# pitch_values = dynamics_data.iloc[start_idx:end_idx, 18].values  # Pitch values
# swing_x = raibert_data.iloc[start_idx:end_idx, 0].values  # Swing distance

# Set up the figure with GridSpec
fig = plt.figure(figsize=(15, 8))
gs = gridspec.GridSpec(2, 2, width_ratios=[1, 1], wspace=0.1, hspace=0.4)

# Create axes
ax_main = fig.add_subplot(gs[:, 0])  # Main plot on the left
ax_pitch = fig.add_subplot(gs[0, 1])  # Pitch plot top right
ax_swing = fig.add_subplot(gs[1, 1])  # Swing plot bottom right

# Initialize main plot elements
left_foot = ax_main.scatter([], [], c='r', s=50, label='Left Foot')
right_foot = ax_main.scatter([], [], c='b', s=50, label='Right Foot')
left_trace, = ax_main.plot([], [], 'r-', alpha=0.3, label='Left Foot Trace')
right_trace, = ax_main.plot([], [], 'b-', alpha=0.3, label='Right Foot Trace')

# Initialize pendulum elements
pendulum_height = 0.3  # Height of COM above feet
com_radius = 0.02  # Smaller COM circle
pendulum_line, = ax_main.plot([], [], 'k-', linewidth=2, label='Pendulum')
com_point = Circle((0, 0), com_radius, color='black', fill=True)
ax_main.add_patch(com_point)

# Setup main plot
ax_main.grid(True)
ax_main.set_xlabel('X Position (m)')
ax_main.set_ylabel('Z Position (m)')
ax_main.set_aspect('equal')
ax_main.set_title('Foot End Positions with Inverted Pendulum')
ax_main.legend()

# Set axis limits for main plot
margin = 0.3
x_min = min(data_window['left_x'].min(), data_window['right_x'].min())
x_max = max(data_window['left_x'].max(), data_window['right_x'].max())
z_min = min(data_window['left_z'].min(), data_window['right_z'].min())
z_max = max(data_window['left_z'].max(), data_window['right_z'].max())
ax_main.set_xlim(x_min - 0.2, x_max + 0.2)
ax_main.set_ylim(z_min - margin, z_max + margin)

# Initialize pitch and swing plots
line_pitch, = ax_pitch.plot([], [], 'b-', label='Pitch')
ax_pitch.set_title('Pitch Angle')
ax_pitch.set_ylabel('Pitch (deg)')
ax_pitch.grid(True)
ax_pitch.legend()

line_swing, = ax_swing.plot([], [], 'r-', label='Swing Distance')
ax_swing.set_title('Swing Distance')
ax_swing.set_xlabel('Time (s)')
ax_swing.set_ylabel('Distance (m)')
ax_swing.grid(True)
ax_swing.legend()

# Set axis limits and ticks for pitch and swing plots
time_min, time_max = time_window[0], time_window[-1]
ax_pitch.set_xlim(time_min, time_max)
ax_swing.set_xlim(time_min, time_max)

# Set number of ticks for better spacing
n_ticks = 5
time_ticks = np.linspace(time_min, time_max, n_ticks)
ax_pitch.set_xticks(time_ticks)
ax_swing.set_xticks(time_ticks)

# Format tick labels
ax_pitch.set_xticklabels([])  # Remove x-axis labels from pitch plot
ax_swing.set_xticklabels([f'{t:.1f}' for t in time_ticks])

# ax_pitch.set_ylim(min(pitch_values), max(pitch_values))
# ax_swing.set_ylim(min(swing_x), max(swing_x))

pre_pitch = 0
switch = False
stance_x = 0  # Fixed position for stance foot
stance_z = 0

def update(frame):
    global pre_pitch, switch, stance_x, stance_z
    
    # Get current foot positions
    left_x = data_window['left_x'].iloc[frame]
    left_z = data_window['left_z'].iloc[frame]
    right_x = data_window['right_x'].iloc[frame]
    right_z = data_window['right_z'].iloc[frame]
    
    # pitch = np.deg2rad(pitch_values[frame]) - pre_pitch
    
    # Determine which foot is stance foot based on Z position
    if left_z < right_z:  # Left foot is stance
        if switch:  # Just switched to left foot stance
            switch = False
            # pre_pitch = pitch
            stance_x = left_x
            stance_z = left_z
        
        # Calculate offsets
        offset_x = left_x - stance_x
        offset_z = left_z - stance_z
        base_x = stance_x
        base_z = stance_z
    else:  # Right foot is stance
        if not switch:  # Just switched to right foot stance
            switch = True
            # pre_pitch = pitch
            stance_x = right_x
            stance_z = right_z
        
        # Calculate offsets
        offset_x = right_x - stance_x
        offset_z = right_z - stance_z
        base_x = stance_x
        base_z = stance_z
    
    # Update foot positions relative to fixed stance foot
    left_foot.set_offsets(np.c_[left_x - offset_x, left_z - offset_z])
    right_foot.set_offsets(np.c_[right_x - offset_x, right_z - offset_z])
    
    # Update traces
    left_trace.set_data(data_window['left_x'].iloc[:frame] - offset_x,
                       data_window['left_z'].iloc[:frame] - offset_z)
    right_trace.set_data(data_window['right_x'].iloc[:frame] - offset_x,
                        data_window['right_z'].iloc[:frame] - offset_z)
    
    # Calculate COM position relative to fixed stance foot
    # com_x = base_x + pendulum_height * np.sin(pitch)
    # com_z = base_z + pendulum_height * np.cos(pitch)
    
    # # Update pendulum line and COM
    # pendulum_line.set_data([base_x, com_x], [base_z, com_z])
    # com_point.center = (com_x, com_z)
    
    # Update pitch and swing plots
    # line_pitch.set_data(time_window[:frame], pitch_values[:frame])
    # line_swing.set_data(time_window[:frame], swing_x[:frame])
    
    # Update title
    # ax_main.set_title(f'Robot Motion (t={time_window[frame]:.2f}s))
    
    return left_foot, right_foot, left_trace, right_trace, 
# pendulum_line, com_point, line_pitch, line_swing

# Create animation (1/8 speed)
frames = range(0, len(data_window), 8)
ani = FuncAnimation(fig, update, frames=frames, interval=100, blit=True)

# Save animation
writer = animation.PillowWriter(fps=7)
ani.save('foot_xz_pendulum_motion.gif', writer=writer)

# Adjust layout
plt.subplots_adjust(right=0.98, left=0.08, top=0.95, bottom=0.1)
plt.show()
