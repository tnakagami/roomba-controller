from flask import Flask, jsonify, request
from flask_cors import CORS
from time import sleep
from pyroombaadapter import PyRoombaAdapter
import os

# create app
app = Flask('REST API')
CORS(app)
# create adapter
adapter = PyRoombaAdapter('/dev/ttyUSB0')
# command list
commands = {
    'full': lambda xs: adapter.change_mode_to_full(),
    'passive': lambda xs: adapter.change_mode_to_passive(),
    'safe': lambda xs: adapter.change_mode_to_safe(),
    'cleaning': lambda xs: adapter.start_cleaning(),
    'dock': lambda xs: adapter.start_seek_dock(),
    'wait': lambda xs: adapter.move(0, 0),
    'move': lambda xs: adapter.send_drive_cmd(*list(map(int, xs))),
}

@app.after_request
def after_request(response):
    allowed_url = os.getenv('ALLOWED_URL', '')
    response.headers.add('Access-Control-Allow-Origin', allowed_url)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

    return response

@app.route('/', methods=['GET'])
def get_command():
    ret = {
        'commands': list(commands.keys()),
        'args': ['move command is velocity(arg1) and radius(args2)'],
    }

    return jsonify(ret), 200

@app.route('/', methods=['POST'])
def execute_command():
    try:
        cmd = request.json['command']
        args = request.json.get('args', [])
        # execute
        commands[cmd](args)
        # result
        status_code = 200
        message = 'execute {}, {}'.format(cmd, ','.join([str(value) for value in args]))
    except Exception as e:
        status_code = 500
        message = e

    return jsonify({'message': message}), status_code

if __name__ == '__main__':
    port = os.getenv('SERVER_PORT', 10080)
    debug = True if os.getenv('DEBUG', 'false').lower() == 'true' else False
    app.run(host='0.0.0.0', port=port, debug=debug)
