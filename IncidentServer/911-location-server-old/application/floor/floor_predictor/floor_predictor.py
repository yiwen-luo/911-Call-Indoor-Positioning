from pandas import DataFrame
from scipy.signal import savgol_filter
import math
from indoor_outdoor_classifier.indoor_outdoor_classifier import InOutClassifier
import matplotlib.pyplot as plt

AVG_FLOOR_HEIGHT_IN_METERS = 3

class FloorPredictor(object):
    """
    Predicts a floor for an altitude timeseries.
    """
    
    def __init__(self):
        # train in/out classifier to help id when we are indoors
        self.io_clf = InOutClassifier()
        
    """
    Label all points 
    """
    def fit(self, json):
        """
        Fits data to generate floor predictions.
        Input array of timeseries readings [{'time': time_since_epoch, 'alt':-20, ...}, {'time': time_since_epoch, 'alt':-20, ...}]
        return json results, the raw point data
        """
        df = self.json_to_dataframe(json)

        # make indoor/outdoor predictions before smoothing
        indoor_ranges = self.__find_indoor_ranges(df)
        
        df = self.remove_duplicate_indexes(df)
        df_raw = df.copy()
        
        # smooth and find floor changes
        df = self.smooth_data(df)
        points = self.find_major_inflection_points(df, indoor_ranges)
        predictions = self.generate_floor_predictions(points, indoor_ranges)
        return predictions, df_raw, indoor_ranges
    
    #-----------------------------------------------------
    # DATA PROCESSING
    #-----------------------------------------------------    
    def json_to_dataframe(self, json):
        """
        Makes DF from json.
        Pulls index and needed cols
        Change to json later on
        The relative altitude series needs to be named 'alt'
        """
        df = DataFrame(data=json)
        df = df.set_index(['time'])
    
        return df
  
  
    def remove_duplicate_indexes(self, df):
        """
        Removes rows that occur at the same time.
        Sensor data can sometimes happen multiple times per second
        """
        df = df.groupby(level=0)
        return df.last()
    
    
    def smooth_data(self, df):
        """
        Use savgol smoothing to clean data.
        If no smoothing happens, data are too noisy and min/max impossible
        """
        df = df.interpolate(method='linear')
        window_length = 81

        # make odd
        window_length = window_length + 1 if window_length %2==0 else window_length
    
        # apply filter
        alt = savgol_filter(df['alt'], window_length=window_length, polyorder=3)
        df['alt'] = alt

        return df  

    #-----------------------------------------------------
    # RESULT GENERATION
    #-----------------------------------------------------   
    def generate_floor_predictions(self, inflection_points, indoor_ranges):
        """
        Generates predictions metadata and estimates the floor height
        returns list of dictionaries
        """
        predictions = []
        seen_starting_indexes = set()
        for left, mid, right in inflection_points:
    
            # points to compare
            left_height = left[0]
            mid_height = mid[1]
            right_height = right[0]
            
            # id height cases
            ascended_permanently = left_height == mid_height
            descended_permanently = right_height == mid_height
            
            # results
            direction = None
            
            down = math.ceil((left_height - mid_height) / AVG_FLOOR_HEIGHT_IN_METERS)
            up = math.ceil((right_height - mid_height) / AVG_FLOOR_HEIGHT_IN_METERS)
            
            # format direction               
            if ascended_permanently:
                direction = 'up'
                down = None
                
            elif descended_permanently:
                direction = 'down'
                up = None
 
            else:
                direction = 'down up'
                
            prediction = {
            'floor_down': down,
            'floor_up': up,
            'direction':direction,
            'start_time': left.name,
            'start_alt': left_height,
            'end_time': right.name,
            'end_alt': right_height,
            'mid_time': mid[0],
            'mid_alt': mid[1]
            }
            
            # don't add duplicate results
            if not left.name in seen_starting_indexes:
                seen_starting_indexes.add(left.name)
                predictions.append(prediction)
    
        return predictions
    
    #-----------------------------------------------------
    # SIGNIFICANT INFLECTION POINT ALGORITHM
    #----------------------------------------------------- 
    def find_major_inflection_points(self, df, in_out_ranges):
        """
        For each indoor timeframe, runs the inflection point algorithm
        """
        all_key_inflection_points = []        
        for io_range in in_out_ranges:
            io_inflection_points = self.__find_major_inflection_points_in_io_range(df, io_range)
            all_key_inflection_points.extend(io_inflection_points)
        
        return all_key_inflection_points
        
    
    def __find_major_inflection_points_in_io_range(self, df, in_out_range):
        """
        For a given range
        1. Finds major min in left direction
        2. From that min, gradient ascends toward the middle and finds first major inflection point
        3. Measures alt change and tracks it if it was significant.
        4. Does the same on the right side until no more major changes are detected
        """
        inflection_points = []

        # areas of series that are already explored
        removed_ranges = []
    
        # run until the error reaches below a threshold
        significant_left_change = True
        significant_right_change = True
    
        error_threshold = 1.5
        starting_index = int(in_out_range[0] + math.floor(in_out_range[1] / 2))
    
        while significant_left_change or significant_right_change:
            
            # find next significant change on left side and track if one found
            significant_left_change, left_change_tuple = self._find_next_significant_area_in_direction(df, starting_index, 'left', error_threshold, removed_ranges)
            if significant_left_change:
                removed_ranges.append((left_change_tuple[0].name, left_change_tuple[2].name))
                
                # track change if partly indoors
                if self.__change_tuple_was_indoors(left_change_tuple,in_out_range):
                    inflection_points.append(left_change_tuple)
                    

            # find next significant change on right side and track if one found
            significant_right_change, right_change_tuple = self._find_next_significant_area_in_direction(df, starting_index, 'right', error_threshold, removed_ranges)
            if significant_right_change:
                removed_ranges.append((right_change_tuple[0].name, right_change_tuple[2].name))
                
                # track change if partly indoors                
                if self.__change_tuple_was_indoors(right_change_tuple,in_out_range):
                    inflection_points.append(right_change_tuple)
                    
        return inflection_points
     
    def __change_tuple_was_indoors(self, change_tuple, in_out_range):
        
        # in_range start/end
        start = in_out_range[0]
        end = start + in_out_range[1]
        
        # critical point start left and right edge
        left_time = change_tuple[0].name
        right_time = change_tuple[2].name
        
        left_in_range = left_time >= start and left_time <= end
        right_in_range = right_time >= start and right_time <= end
        
        return left_in_range or right_in_range
        
     
    def _find_next_significant_area_in_direction(self, df, starting_index, direction, error_threshold, removed_ranges):
        """
        Gradient descends to direction given until it finds the next significant gradient change
        """
        # from center of indoor range, find min in that direction
        # at that min, climb back up the opposite way to find the descent start
        next_min_in_direction = self.__find_first_min_in_direction(df, starting_index, direction, removed_ranges)
        
        # when no min is found, there isn't a valid range left            
        if next_min_in_direction[1] is None:
            return False, None

        first_max_to_left = self.find_max_in_direction('left', df, next_min_in_direction)
        first_max_to_right = self.find_max_in_direction('right', df, next_min_in_direction)

        # see if this altitude change is significant
        # if so, append to inflection_points
        poi_alt_change_left = first_max_to_left[0] - next_min_in_direction[1]
        poi_alt_change_right = first_max_to_right[0] - next_min_in_direction[1]
        significant_change_left = poi_alt_change_left > error_threshold
        significant_change_right = poi_alt_change_right > error_threshold
        
        # if significant return a tuple in the form (l_max, min, r_max)
        if significant_change_left or significant_change_right:
            return True, (first_max_to_left, next_min_in_direction, first_max_to_right)
        else:
            return False, None
            
    #-----------------------------------------------------
    # ALGO HELPERS
    #-----------------------------------------------------
            
    def is_in_valid_range(self, index, removed_ranges):
        """
        Parts of the series are blocked out to id the next min.
        This returns true if index is not within any of the blocked regions.
        """
        for left, right in removed_ranges:
            if index >= left and index <= right:
                return False
    
        return True
    
    
    def find_max_in_direction(self, direction, df, global_min):
        """
        Gradient ascent on the derivative until sign change.
        At sign change, we have a peak.
        """
        starting_index = global_min[0]
    
        # invert series if going left
        data = df[::-1] if direction is 'left' else df
    
        # starting gradient values
        initial_is_pos = True
        prev_value = global_min[1]
    
        # if reach end of series on either side, terminate
        terminating_side_index = 0 if direction is 'left' else -1
        terminating_side_point = df.iloc[terminating_side_index]
    
        for row, value in data.loc[starting_index:].iterrows():
            # calue under current inspection
            next_value = value[0]
    
            # calculate gradient
            gradient = (next_value - prev_value) / 2
    
            # offset to next point in sequence
            prev_value = next_value
    
            # if signs change, return this point.
            gradient_is_pos = gradient >= 0
            if initial_is_pos != gradient_is_pos:
                return value
    
            # if hit sides of series, return the end value
            if terminating_side_point.name == value.name:
                return value
    
        # no change of sign detected
        return None
    
    def __find_first_min_in_direction(self, df, starting_index, direction, removed_ranges):
        min_index = None
        data = df[::-1] if direction is 'left' else df
        min_altitude = 100000000
        min_index = None
        
        terminating_index = 0 if direction is 'left' else -1
        terminating_side_point = df.iloc[terminating_index]
        
        for index, current_point in data.loc[starting_index:].iterrows():
            if (self.is_in_valid_range(index, removed_ranges)): 
                current_value = current_point[0]          
                
                # value under current inspection
                altitude = current_value
                if altitude < min_altitude:
                    min_altitude = altitude
                    min_index = index
            
            if terminating_side_point.name == current_point.name:
                break
        
        if min_altitude == 100000000:
            return (None, None)
            
        return (min_index, min_altitude)

 
    #-----------------------------------------------------
    # INDOOR / OUTDOOR CLASSIFICATION
    #-----------------------------------------------------                   

    def __find_indoor_ranges(self, df):
        """
        Returns a list of (start, end) ranges for each chunk of indoor/outdoor activity
        """
        # only care about indoor activity above 20 seconds long
        min_indoor_duration_in_seconds = 20

        # hold tuples in the form (start_time, end_time, sequence_count)
        start_end_tuples = []
        
        # classify as outside or inside
        self.__classify_in_out(df)
        
        # find the in/out ranges
        is_counting = False
        current_count = 0
        start_index = None
        end_index = None
        for i, row in df.iterrows():
            
            # get index and prediction values
            time = row.name
            in_out = int(row[-1])
            
            # if it is indoors increase/make tuple
            if in_out == 1:
                if is_counting:
                    current_count +=1 
                else:
                    start_index = time
                    end_index = start_index + current_count
                    current_count = 1
                    is_counting = True
                    
            else:
                # stop counting if was counting and hit a 0
                if is_counting:
                    # track the range if it is above the threshold
                    if current_count > min_indoor_duration_in_seconds:
                        start_end_tuples.append((start_index, current_count, start_index + current_count))

                    # reset tuple info
                    is_counting = False
                    current_count = 0
                    start_index = None
                    end_index= None
                    
        # pull last tuple in case we finish the sequence indoors
        if is_counting:
            # track the range if it is above the threshold
            if current_count > min_indoor_duration_in_seconds:
                start_end_tuples.append((start_index, current_count, end_index + current_count))

  
        # sort results from highest to lowest
        return start_end_tuples

    def classify_in_out(self, json):
        
        # predict only last 10 items
        df = DataFrame(data=json)
        df = df[['gpsAccuracyHor', 'gpsAccuracyVert', 'gpsCourse', 'gpsSpeed']]
        df = df.tail(10)

        # classify as in_out
        points = df.as_matrix()        
        df['inOut'] = self.io_clf.predict(points)
        
        # use the last point as indicator of where we likely are now
        in_out = df.iloc[-1]['inOut']

        # average last 10 points for indoor/outdoor probability
        matches = 0
        for i, row in df.iterrows():
            if row.inOut == in_out:
                matches += 1

        prob = matches / float(len(df)) 

        # send the response alongside a probability
        in_out = 'indoors' if in_out == 1 else 'outdoors'
        result = {'location': in_out, 'confidence': prob}
        return result

    def __classify_in_out(self, df):
        """
        Uses only the gps data to classify whether someone is inside or outside
        """
        gps_df = df.ix[:,2:]
        points = gps_df.as_matrix()        
        df['inOut'] = self.io_clf.predict(points)
        
    #-----------------------------------------------------
    # PLOTTING
    #-----------------------------------------------------    
    def __plot_in_out_preds(self, df, ranges):
        """
        Plots the region predicted to be indoor or outdoors
        """
        print 'plotting in out...'
        df.plot(y='alt')
        for time, duration in ranges:
            for i in xrange(duration):
                plt.axvline(time + i, color=(0.7, 0.7, 0.7), linestyle='--')                
        print 'plot complete...'
        
        
    def plot(self, df, predictions, indoor_ranges):
        """
        Plots altitude series with all the significant changes in alt
        """
        print 'Building chart...'
        df.plot(y=['alt', 'inOut'])
        
        # plot predictions
        for i, prediction in enumerate(predictions):
            color_constant = (i+1.0)/len(predictions)
            edge_color = (color_constant, 0.7, color_constant)
            plt.axvline(prediction['start_time'], color=edge_color, linestyle='-')
            plt.axvline(prediction['mid_time'], color=edge_color, linestyle='--')
            plt.axvline(prediction['end_time'], color=edge_color, linestyle='-')
    
        print 'Chart built!'
    