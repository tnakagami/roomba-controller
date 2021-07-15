from flask import Flask, jsonify, request
from time import sleep
import numpy as np
from pyroombaadapter import PyRoombaAdapter
import os

# create app
app = Flask('REST API')
# create adapter
adapter = PyRoombaAdapter('/dev/ttyUSB0')

@app.route('/', methods=['GET'])
def get_command():
    return jsonify({'command': ''}), 200

if __name__ == '__main__':
    port = os.getenv('SERVER_PORT', 10080)
    app.run(port=port, debug=True)
