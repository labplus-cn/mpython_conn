# coding=utf-8
from mpython_conn import controller
import turtle
import time

turtle.setup(640, 320)
t = turtle.Turtle(shape="turtle")
m = controller()
dir = ''

def forward():
    global dir
    dir = 'f'
    print("forward")
    while dir == 'f':
        t.forward(10)
        time.sleep(0.1)
    
def back():
    global dir
    dir = 'b'
    print("back")
    while dir == 'b':
        t.back(10)
        time.sleep(0.1)

def left():
    global dir
    dir = 'l'
    print("left")
    while dir == 'l':
        t.left(15)
        time.sleep(0.1)

def right():
    global dir
    dir = 'r'
    print("right")
    while dir == 'r':
        t.right(15)
        time.sleep(0.1)

def flat():
    global dir
    dir = ''
    print("flat")

m.on_tilt_forward = forward
m.on_tilt_back = back
m.on_tilt_left = left
m.on_tilt_right = right
m.on_tilt_none = flat

turtle.mainloop()
