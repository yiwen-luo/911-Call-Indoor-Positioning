from flask import Flask
from application.floor.floor_predictor.floor_predictor import FloorPredictor
from application.views import application

## Elastic Beanstalk initalization
#application = Flask(__name__)
#
## change this to your own value
#application.secret_key = 'cC1YCIWOj9GgWspgNEo2'


if __name__ == '__main__':

    # attach floor predictor so app can use it
    with application.app_context():
        application.floor_predictor = FloorPredictor()

    application.run(debug=True, host= '127.0.0.1')
