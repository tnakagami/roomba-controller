from flask import Flask, jsonify, request
from flask_cors import CORS
from pyroombaadapter import PyRoombaAdapter
from picamera import PiCamera
from io import BytesIO
import logging
import logging.config as logconf
import base64
import os
import time

# setup logger
log_configure = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            'datefmt': '%Y/%m/%d %H:%M:%S',
        },
    },
    'handlers': {
        'timeRotate': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'default',
            'filename': '/var/log/access.log',
            'when': 'W2',
            'backupCount': 3,
        },
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['timeRotate', 'wsgi'],
    },
}
logconf.dictConfig(log_configure)

# PiCameraWrapper
class CameraWrapper():
    def __init__(self, resolution):
        self.__camera = PiCamera()
        self.__camera.resolution = resolution
        self.__camera.rotation = 90
        self.__stream = BytesIO()
        self.__camera.start_preview()
        time.sleep(2)

    def finalize(self):
        self.__camera.close()
        self.__stream.close()

    def capture(self):
        file_format = 'jpeg'
        # capture
        self.__stream.seek(0)
        self.__camera.capture(self.__stream, file_format)
        # get binary image
        self.__stream.seek(0)
        binary_image = self.__stream.getvalue()
        # convert binary image to string data encoded by base64
        response = 'data:image/{};base64,{}'.format(file_format, base64.b64encode(binary_image).decode())
        self.__stream.flush()

        return response

# create api
api = Flask('Manual Roomba Controller')
CORS(api)
# create adapter
adapter = PyRoombaAdapter('/dev/ttyUSB0')
# create picamera wrapier
camera = CameraWrapper((640, 360))
# command list
commands = {
    'full': lambda xs: adapter.change_mode_to_full(),
    'passive': lambda xs: adapter.change_mode_to_passive(),
    'safe': lambda xs: adapter.change_mode_to_safe(),
    'cleaning': lambda xs: adapter.start_cleaning(),
    'dock': lambda xs: adapter.start_seek_dock(),
    'wait': lambda xs: adapter.move(0, 0),
    'move': lambda xs: adapter.send_drive_cmd(*list(map(float, xs))),
}

@api.after_request
def after_request(response):
    allowed_url = os.getenv('ALLOWED_URL', '')
    response.headers.add('Access-Control-Allow-Origin', allowed_url)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

    return response

@api.route('/', methods=['GET'])
def get_command():
    ret = {
        'commands': list(commands.keys()),
        'args': ['move command requires velocity(arg1) and radius(args2)'],
    }

    return jsonify(ret), 200

@api.route('/', methods=['POST'])
def execute_command():
    try:
        cmd = request.json.get('command', '')
        args = request.json.get('args', [])
        # execute
        commands[cmd](args)
        # result
        status_code = 200
        message = 'execute {} {}'.format(cmd, ','.join([str(value) for value in args]))
    except Exception as e:
        status_code = 500
        message = e
        api.logger.warn('        {}'.format(message))

    return jsonify({'message': message}), status_code

@api.route('/capture', methods=['GET'])
def capture():
    try:
        status_code = 200
        message = camera.capture()
    except Exception as e:
        status_code = 500
        message = e
        api.logger.warn('        {}'.format(message))

    return jsonify({'message': message}), status_code

if __name__ == '__main__':
    port = os.getenv('SERVER_PORT', 10080)
    debug = True if os.getenv('DEBUG', 'false').lower() == 'true' else False

    try:
        adapter.change_mode_to_safe()
        api.run(host='0.0.0.0', port=port, debug=debug)
    except Exception as e:
        api.logger.warn('[main] {}'.format(e))
    finally:
        del adapter
        camera.finalize()
