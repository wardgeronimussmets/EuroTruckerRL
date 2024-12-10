import json

def load_relative_regions_config(key):
    with open('config/image_relative_regions.json') as f:
        return json.load(f)[key]