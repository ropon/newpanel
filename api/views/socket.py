#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/8/7 10:21
# @Author  : Ropon
# @File    : socket.py

from flask import Blueprint
from flask_socketio import send, emit
from api import socketio

socket_bp = Blueprint("socket_bp", __name__, url_prefix="/api/v1")


@socketio.on('message')
def handle_message(message):
    print('message')
    send(message)
    # emit('my response')


@socketio.on('json')
def handle_json(json):
    print('json')
    # send(json, json=True)


@socketio.on('my event')
def handle_my_custom_event(json):
    print(json)


@socketio.on('connect', namespace='/chat')
def test_connect():
    emit('my response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/chat')

def test_disconnect():
    print('Client disconnected')
