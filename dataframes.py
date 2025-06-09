import pandas as pd
import numpy as np
import os

# Load the dataset (replace with the correct file path)
data = pd.read_csv('c:/Users/colto/Downloads/test1.csv')  # Replace with your actual file path

output_folder = r"C:/Users/colto/Documents/GradSchool/Silicon/Harpy/outputs"
os.makedirs(output_folder, exist_ok=True)

# Extract relevant columns (head, left foot, right foot positions)
head_positions = data[['x_h', 'y_h', 'z_h']].values  # Head positions: x, y, z
left_positions = data[['x_l', 'y_l', 'z_l']].values  # Left foot positions: x, y, z
right_positions = data[['x_r', 'y_r', 'z_r']].values  # Right foot positions: x, y, z
time_stamps = data['time_stamp'].values  # Time stamps

# Define movement detection threshold (adjust this value based on your needs)
movement_threshold = 0.01  # Change in position (meters)

# Initialize list to store the results
movement_data = []

# Loop through the data and check for movement
for i in range(1, len(data)):
    # Calculate the position differences between successive time points
    head_diff = np.linalg.norm(head_positions[i] - head_positions[i-1])  # Euclidean distance
    left_diff = np.linalg.norm(left_positions[i] - left_positions[i-1])  # Euclidean distance
    right_diff = np.linalg.norm(right_positions[i] - right_positions[i-1])  # Euclidean distance

    # If any position difference exceeds the movement threshold, consider it as movement
    if head_diff > movement_threshold or left_diff > movement_threshold or right_diff > movement_threshold:
        # Record the time and positions for when movement is detected
        movement_data.append([time_stamps[i], head_positions[i][0], head_positions[i][1], head_positions[i][2], 
                              left_positions[i][0], left_positions[i][1], left_positions[i][2], 
                              right_positions[i][0], right_positions[i][1], right_positions[i][2]])

# Convert the movement data to a DataFrame
movement_df = pd.DataFrame(movement_data, columns=['time_stamp', 'head_x', 'head_y', 'head_z',
                                                   'left_x', 'left_y', 'left_z',
                                                   'right_x', 'right_y', 'right_z'])

# Save the data to CSV
movement_df.to_csv(os.path.join(output_folder, 'movement1.csv'), index=False)

print("Movement data saved to 'movement_positions.csv'")
