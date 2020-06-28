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
# folder for configuration files
config_dir = os.path.join(local_path, "config")

# constant for the logging system
default_logfile = "maintenance"
full_logfile = os.path.join(log_dir, default_logfile + ".log")


def is_system_production():
    """
    check if the system is runing in production mode
    :return: True if the system is in installed directory
    """
    if local_path == "/var/maintenance":
        return True
    return False
