# Floor predictor module
Returns a list of predictions for a given user.   

Example result. A red line means the bottom of an ascent. Other lines mean the top of that ascent. 
<img src="https://github.com/williamFalcon/911/blob/master/MLServer/floor/Example_graph.png" width="40%" /> 

[Example result](https://github.com/williamFalcon/911/blob/master/MLServer/floor/sample_result.json)   

## Usage
```python
from floor_predictor.floor_predictor import FloorPredictor

json = load_data() # get json data somehow
predictor = FloorPredictor()
predictions, df = predictor.fit(json)

print predictions
```   