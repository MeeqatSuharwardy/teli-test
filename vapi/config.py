# config.py
# this is a configuration file to import the latest file path
#needed to update the status dynamically on the csv

latest_file_path = None

def get_latest_file_location():
    global latest_file_path
    return latest_file_path

def set_latest_file_location(path):
    global latest_file_path
    latest_file_path = path