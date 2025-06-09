import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation as R

data = pd.read_csv('C:/Users/colto/Downloads/harpyV2_trotting_4_2025-05-16.csv')

qx = data['qx_h'].values
qy = data['qy_h'].values
qz = data['qz_h'].values
qw = data['qw_h'].values

xh = data['x_h'].values
yh = data['y_h'].values
zh = data['z_h'].values

xr = data['x_r'].values
yr = data['y_r'].values
zr = data['z_r'].values

xl = data['x_l'].values
yl = data['y_l'].values
zl = data['z_l'].values

xp = data['x_o'].values
yp = data['y_o'].values
zp = data['z_o'].values

wfl = np.column_stack((xl, yl, zl))  # shape (N, 3)
wfr = np.column_stack((xr, yr, zr))
wfp = np.column_stack((xp, yp, zp))
wfb = np.column_stack((xh, yh, zh))

quats = np.column_stack((qx, qy, qz, qw))  # shape (N, 4)
rb = R.from_quat(quats)
rb_inv = rb.inv()    

bfl = -rb_inv.apply(wfb - wfl)
bfr = -rb_inv.apply(wfb - wfr)
bfp  = -rb_inv.apply(wfb - wfp)

foot_centroid_offset = np.array([169.506, -277.68, 14.75])/1000  # shape (3,)

# Subtract this offset to align to actual contact point
bfl_corrected = bfl - foot_centroid_offset
bfr_corrected = bfr - foot_centroid_offset

plate_data = np.hstack((bfp, bfl_corrected, bfr_corrected))

# plate_data = np.hstack((bfp, bfl, bfr))
time_stamps = data["time_stamp"].values
time_stamps = time_stamps.reshape(-1, 1)
plate_data = np.hstack((plate_data, time_stamps))
columns = ["x_bfp", "y_bfp", "z_bfp", "x_bfl", "y_bfl", "z_bfl", "x_bfr", "y_bfr", "z_bfr", "time_stamps"]

df = pd.DataFrame(plate_data, columns=columns)
df.to_csv("body_frame_points.csv", index=False)