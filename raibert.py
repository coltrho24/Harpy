import pandas as pd
import numpy as np
import os

# Load your dataset
data = pd.read_csv('c:/Users/colto/Downloads/test4.csv')  # Replace with your CSV file

output_folder = r"C:/Users/colto/Documents/GradSchool/Silicon/Harpy/outputs"
os.makedirs(output_folder, exist_ok=True)

# Define the time window for analysis
dt = 1 / 500  # Assuming 500 Hz sampling rate (adjust if needed)
time = np.arange(0, len(data) * dt, dt)

# Extract foot position columns
left_x = data['x_l']
left_z = data['z_l']
right_x = data['x_r']
right_z = data['z_r']

# Initialize variables for swing detection
swing_data = []
last_left_swing_time = None
last_right_swing_time = None

# Loop through the dataset to find swing events
for i in range(1, len(data)):
    # Find when the foot switches from stance to swing (Z position increases)
    if left_z[i] > left_z[i-1]:  # Left foot in swing phase
        if last_left_swing_time is None or time[i] - last_left_swing_time > 0.1:  # New swing phase
            if last_left_swing_time is not None:
                step_length = np.sqrt((left_x[i] - left_x[last_left_swing_time_index])**2 + 
                                      (left_z[i] - left_z[last_left_swing_time_index])**2)
                step_duration = time[i] - last_left_swing_time
                swing_data.append([time[i], 'left', left_x[i], left_z[i], step_length, step_duration])
            last_left_swing_time = time[i]
            last_left_swing_time_index = i
    elif right_z[i] > right_z[i-1]:  # Right foot in swing phase
        if last_right_swing_time is None or time[i] - last_right_swing_time > 0.1:  # New swing phase
            if last_right_swing_time is not None:
                step_length = np.sqrt((right_x[i] - right_x[last_right_swing_time_index])**2 + 
                                      (right_z[i] - right_z[last_right_swing_time_index])**2)
                step_duration = time[i] - last_right_swing_time
                swing_data.append([time[i], 'right', right_x[i], right_z[i], step_length, step_duration])
            last_right_swing_time = time[i]
            last_right_swing_time_index = i

# Convert swing data to a DataFrame
swing_df = pd.DataFrame(swing_data, columns=['time', 'swing_leg', 'x', 'z', 'step_length', 'step_duration'])
swing_df.to_csv(os.path.join(output_folder, 'raibert_output4.csv'), index=False)
