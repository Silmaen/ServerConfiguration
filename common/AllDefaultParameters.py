"""
gathering of all default parameters
"""
import os

# base path of the maintenance system
local_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# folder for logging
log_dir = os.path.join(local_path, "log")
# folder for disk data
data_dir = os.path.join(local_path, "data")

# constant for the logging system
default_logfile = "maintenance"
full_logfile = os.path.join(log_dir, default_logfile + ".log")
