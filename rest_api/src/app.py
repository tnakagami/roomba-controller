from flask import Flask, jsonify, request
from time import sleep
import numpy as np
from pyroombaadapter import PyRoombaAdapter
import os

# create app
app = Flask('REST API')
# create adapter
adapter = PyRoombaAdapter('/dev/ttyUSB0')
# command list
commands = {
    'full': lambda xs: adapter.change_mode_to_full(),
    'passive': lambda xs: adapter.change_mode_to_passive(),
    'safe': lambda xs: adapter.change_mode_to_safe(),
    'cleaning': lambda xs: adapter.start_cleaning(),
    'move': lambda xs: adapter.move(xs[0], np.rad2deg(int(xs[1]))),
}


@app.route('/', methods=['GET'])
def get_command():
    ret = {
        'commands': list(commands.keys()),
        'args': ['move command is velocity(arg1) and yaw rate(arg2)'],
    }

    return jsonify(ret), 200

@app.route('/', methods=['POST'])
def execute_command():
    try:
        cmd = request.json['command']
        args = request.json['args']
        # execute
        commands[cmd](args)
        message = 'execute {}, {}'.format(cmd, ','.join([str(value) for value in args]))
    except Exception as e:
        status_code = 500
        message = e

    return jsonify({'message': message}), status_code

if __name__ == '__main__':
    port = os.getenv('SERVER_PORT', 10080)
    app.run(host='0.0.0.0', port=port, debug=True)
