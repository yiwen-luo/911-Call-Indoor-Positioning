from floor_predictor.floor_predictor import FloorPredictor
import json
import os
import sys

JSON_DATA_FILE = 'tt.json'

"""
Module to demo functionality
"""
def run_demo(file_path):

    json = load_data(file_path)
    predictor = FloorPredictor()
    predictions, df, indoor_ranges = predictor.fit(json)
    print predictions
    predictor.plot(df, predictions, indoor_ranges)


def load_data(file_path):
    """
    Loads data from a csv
    Change to json later on
    The relative altitude series needs to be named 'alt'
    """
    data = None
    full_path = os.path.dirname(os.path.realpath(__file__)) + file_path
    with open(full_path) as data_file:    
        data = json.load(data_file)
    return data

if __name__ == '__main__':
    path = sys.argv[1]
    print path
    run_demo(path)
