# -*- coding:utf-8 -*-
# @Time     : 2020/06/10
# @Author   : Wu Wen Jie(6692776@qq.com)
# @FileName : mpython_conn.py
# @Description : A transfer protocol between mPython board and PC python
# @Version  : 0.3.2
from serial.tools.list_ports import comports as list_serial_ports
from serial import Serial
import threading
import time
import atexit
import unicodedata
import inspect
import ctypes
import sys


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
 

def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


class controller():

    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(controller, cls).__new__(cls, *args, **kw)
        return cls._instance

    SENSORS = {
        'A': 0,
        'B': 0,
        'P': 0,
        'Y': 0,
        'T': 0,
        'H': 0,
        'O': 0,
        'N': 0,
        'L': 0,
        'S': 0,
        'E': 0,
        'aX': 0,
        'aY': 0,
        'aZ': 0,
        'dir': '',
        'pinD': [0] * 17,
        'pinA': [0, 0, 0],
        'G': 0    # 姿态 0正常 1摇晃 2抛起
    }

    def analysis_data(self, data):
        if data[0] == '{':
            try:
                data = eval(data)
                d = ("0000000" + str(bin(data['d']))[2:])[-8:]
                sys.stdout.flush()
                
                if self.SENSORS['A'] != ('1' == d[6]):
                    if self.SENSORS['A']:
                        threading.Thread(target=self.on_a_released).start()
                    else:
                        threading.Thread(target=self.on_a_pressed).start()
                    self.SENSORS['A'] = ('1' == d[6])

                if self.SENSORS['B'] != ('1' == d[7]):
                    if self.SENSORS['B']:
                        threading.Thread(target=self.on_b_released).start()
                    else:
                        threading.Thread(target=self.on_b_pressed).start()
                    self.SENSORS['B'] = ('1' == d[7])

                if self.SENSORS['P'] != ('1' == d[0]):
                    if self.SENSORS['P']:
                        threading.Thread(target=self.on_p_released).start()
                    else:
                        threading.Thread(target=self.on_p_pressed).start()
                    self.SENSORS['P'] = ('1' == d[0])

                if self.SENSORS['Y'] != ('1' == d[1]):
                    if self.SENSORS['Y']:
                        threading.Thread(target=self.on_y_released).start()
                    else:
                        threading.Thread(target=self.on_y_pressed).start()
                    self.SENSORS['Y'] = ('1' == d[1])

                if self.SENSORS['T'] != ('1' == d[2]):
                    if self.SENSORS['T']:
                        threading.Thread(target=self.on_t_released).start()
                    else:
                        threading.Thread(target=self.on_t_pressed).start()
                    self.SENSORS['T'] = ('1' == d[2])

                if self.SENSORS['H'] != ('1' == d[3]):
                    if self.SENSORS['H']:
                        threading.Thread(target=self.on_h_released).start()
                    else:
                        threading.Thread(target=self.on_h_pressed).start()
                    self.SENSORS['H'] = ('1' == d[3])

                if self.SENSORS['O'] != ('1' == d[4]):
                    if self.SENSORS['O']:
                        threading.Thread(target=self.on_o_released).start()
                    else:
                        threading.Thread(target=self.on_o_pressed).start()
                    self.SENSORS['O'] = ('1' == d[4])

                if self.SENSORS['N'] != ('1' == d[5]):
                    if self.SENSORS['N']:
                        threading.Thread(target=self.on_n_released).start()
                    else:
                        threading.Thread(target=self.on_n_pressed).start()
                    self.SENSORS['N'] = ('1' == d[5])
                    
                if self.SENSORS['G'] != data['t']:
                    if 1 == data['t']:
                        threading.Thread(target=self.on_shaken).start()
                    elif 2 == data['t']:
                        threading.Thread(target=self.on_jumped).start()
                    self.SENSORS['G'] = data['t']

                self.SENSORS['L'] = data['l']
                self.SENSORS['S'] = data['s']
                self.SENSORS['E'] = data['e']
                self.SENSORS['aX'] = data['x']
                self.SENSORS['aY'] = data['y']
                self.SENSORS['aZ'] = data['z']
                
                if data['x'] < -0.3:
                    if 'F' != self.SENSORS['dir']:
                        self.SENSORS['dir'] = 'F'
                        threading.Thread(target=self.on_tilt_forward).start()
                elif data['x'] > 0.3:
                    if 'B' != self.SENSORS['dir']:
                        self.SENSORS['dir'] = 'B'
                        threading.Thread(target=self.on_tilt_back).start()
                elif data['y'] < -0.3:
                    if 'R' != self.SENSORS['dir']:
                        self.SENSORS['dir'] = 'R'
                        threading.Thread(target=self.on_tilt_right).start()
                elif data['y'] > 0.3:
                    if 'L' != self.SENSORS['dir']:
                        self.SENSORS['dir'] = 'L'
                        threading.Thread(target=self.on_tilt_left).start()
                else:
                    if '' != self.SENSORS['dir']:
                        self.SENSORS['dir'] = ''
                        threading.Thread(target=self.on_tilt_none).start()

                if 'd0' in data: self.SENSORS['pinD'][0] = (1 == data['d0'])
                if 'd1' in data: self.SENSORS['pinD'][1] = (1 == data['d1'])
                if 'd2' in data: self.SENSORS['pinD'][2] = (1 == data['d2'])
                if 'd8' in data: self.SENSORS['pinD'][8] = (1 == data['d8'])
                if 'd9' in data: self.SENSORS['pinD'][9] = (1 == data['d9'])
                if 'd10' in data: self.SENSORS['pinD'][10] = (1 == data['d10'])
                if 'd13' in data: self.SENSORS['pinD'][13] = (1 == data['d13'])
                if 'd14' in data: self.SENSORS['pinD'][14] = (1 == data['d14'])
                if 'd15' in data: self.SENSORS['pinD'][15] = (1 == data['d15'])
                if 'd16' in data: self.SENSORS['pinD'][16] = (1 == data['d16'])

                if 'a0' in data: self.SENSORS['pinA'][0] = data['a0']
                if 'a1' in data: self.SENSORS['pinA'][1] = data['a1']
                if 'a2' in data: self.SENSORS['pinA'][2] = data['a2']

            except:
                pass

    def find_device(self):
        ports = list_serial_ports()
        for port in ports:
            if "VID:PID=10C4:EA60" in port[2].upper():
                return port[0]
        return None

    def on_serial_read(self):
        while True:
            try:
                if self._serial.in_waiting:
                    s = self._serial.readline().decode('utf-8')
                    self.analysis_data( s )
            except:
                if self.enable: print("serial error")
                break

    def break_first(self):
        for i in range(3):
            self._serial.write(b'\r\x03')
            time.sleep(0.01)
        time.sleep(0.1)

    def reboot(self):
        for i in range(3):
            self._serial.write(b'\r\x03')
            time.sleep(0.01)
        self._serial.write(b'\x04')
        
    def disconnect(self):        
        self.enable = False
        for i in range(3):
            self._serial.write(b'\r\x03')
            time.sleep(0.01)
        self.send("import os;os.rename('main.bak','main.py')")
        self._serial.write(b'\x04')
        time.sleep(0.5)
        stop_thread(self.read_thread)
        if self._serial.isOpen(): self._serial.close()

    def send(self, message):
        if self._serial is None:  return
        message = message + "\r\n"
        message = message.encode("utf-8")
        self._serial.write(message)
        time.sleep(0.11 + len(message)/512)
        
    
    def __init__(self, port=''):
        if '' == port:
            port = self.find_device()
        self._port = port
        self._serial = Serial(port, 115200, timeout=1, parity='N')
        self._serial.setDTR(True)
        self._serial.setRTS(True)
        self.enable = True

        self.read_thread = threading.Thread(target=self.on_serial_read)
        self.read_thread.start()

        self.break_first()
        self.send("import os;os.rename('main.py','main.bak')")
        self._serial.write(b'\x04')
        time.sleep(0.5)
        self.send("import mpython_online")

    def __del__(self):
        print("Disconnected")


    ## 指令
    def set_digital(self, pin, value):
        """
        @param pin: 0, 1, 8, 9, 13, 14, 15, 16
        @param value: 0, 1
        """
        if not pin in [0, 1, 8, 9, 13, 14, 15, 16]: return
        command = "MPythonPin({},PinMode.OUT).write_digital({})".format(pin, value)
        self.send(command)

    def set_analog(self, pin, value):
        """
        @param pin: 0, 1, 8, 9, 13, 14, 15, 16
        @param value: 0~1023
        """
        if not pin in [0, 1, 8, 9, 13, 14, 15, 16]: return
        command = "MPythonPin({},PinMode.PWM).write_analog({})".format(pin, value)
        self.send(command)

    def set_servo(self, pin, value):
        """
        @param pin: 0, 1, 8, 9, 13, 14, 15, 16
        """
        if not pin in [0, 1, 8, 9, 13, 14, 15, 16]: return
        command = "Servo({}).write_angle({})".format(pin, value)
        self.send(command)

    def set_rgb(self, r, g, b, index=-1):
        """
        @param index: 0, 1, 2, -1(代表全部，可不填)
        """
        if index in [0, 1, 2]:
            command = "rgb[{}]=({},{},{});rgb.write();time.sleep_ms(1)".format(index, r, g, b)
        else:
            command = "rgb.fill(({},{},{}));rgb.write();time.sleep_ms(1)".format(r, g, b)
        self.send(command)

    def set_rgb_off(self, index=-1):
        """
        @param index: 0, 1, 2, -1(代表全部，可不填)
        """
        if index in [0, 1, 2]:
            command = "rgb[{}]=(0,0,0);rgb.write();time.sleep_ms(1)".format(index)
        else:
            command = "rgb.fill((0,0,0));rgb.write();time.sleep_ms(1)"
        self.send(command)

    def to_unicode(self, text):
        text = unicodedata.normalize('NFKC', text)
        ret = ''
        for v in text:
            if '\u4e00' <= v <= '\u9fff':
                ret = ret + hex(ord(v)).upper().replace('0X', '\\u')
            else:
                ret = ret + v
        return ret

    def oled_clear(self):
        command = "oled.fill(0);oled.show()"
        self.send(command)

    def oled_clear_line(self, line):
        """
        @param pin: 1, 2, 3, 4
        """
        if not line in [1, 2, 3, 4]: return
        command = "oled.fill_rect(0,{},128,16,0);oled.show()".format((line-1) * 16)
        self.send(command)

    def oled_display_line(self, text, line):
        """
        @param pin: 1, 2, 3, 4
        """
        if not line in [1, 2, 3, 4]: return
        command = "oled.DispChar('{}',0,{},1);oled.show()".format(self.to_unicode(text), (line-1) * 16)
        self.send(command)

    def oled_display_text(self, text, x, y):
        command = "oled.DispChar('{}',{},{},1);oled.show()".format(self.to_unicode(text), x, y)
        self.send(command)

    def oled_draw_point(self, x, y, mode=1):
        """
        @param mode: 1绘制(默认) 0擦除
        """
        command = "oled.pixel({},{},{});oled.show()".format(x, y, mode)
        self.send(command)

    def oled_draw_line(self, x1, y1, x2, y2, mode=1):
        """
        @param mode: 1绘制(默认) 0擦除
        """
        command = "oled.line({},{},{},{},{});oled.show()".format(x1, y1, x2, y2, mode)
        self.send(command)

    def oled_draw_vhline(self, x, y, len, dir='h', mode=1):
        """
        @param dir: h水平 v垂直
        @param mode: 1绘制(默认) 0擦除
        """
        command = "oled.{}line({},{},{},{});oled.show()".format(dir, x, y, len, mode)
        self.send(command)

    def oled_draw_rectangle(self, x, y, w, h, fill=0, mode=1):
        """
        @param fill: 1实心 0空心(默认)
        @param mode: 1绘制(默认) 0擦除
        """
        fill_mode = "fill_" if 1 == fill else ""
        command = "oled.{}rect({},{},{},{},{});oled.show()".format(fill_mode, x, y, w, h, mode)
        self.send(command)

    def oled_draw_circle(self, x, y, r, fill=0, mode=1):
        """
        @param fill: 1实心 0空心(默认)
        @param mode: 1绘制(默认) 0擦除
        """
        fill_mode = "fill_" if 1 == fill else ""
        command = "oled.{}circle({},{},{},{});oled.show()".format(fill_mode, x, y, r, mode)
        self.send(command)

    def oled_draw_triangle(self, x1, y1, x2, y2, x3, y3, fill=0, mode=1):
        """
        @param fill: 1实心 0空心(默认)
        @param mode: 1绘制(默认) 0擦除
        """
        fill_mode = "fill_" if 1 == fill else ""
        command = "oled.{}triangle({},{},{},{},{},{},{});oled.show()".format(fill_mode, x1, y1, x2, y2, x3, y3, mode)
        self.send(command)

    def stop_music(self):
        """
        停止播放音乐
        """
        command = "music.pitch(4)\r\nmusic.stop()"
        self.send(command)

    def play_tone(self, pitch=131):
        """
        播放连续音调
        @param pitch: 频率，例: 131
        """
        command = "music.pitch({})".format(pitch)
        self.send(command)

    def play_note(self, note='C3:1'):
        """
        播放单个音符
        @param note: 音符，例: C3:1
        """
        command = "music.play('{}')".format(note)
        self.send(command)

    def set_motor_power(self, motor_id=1, power=100):
        """
        驱动掌控宝M1、M2马达
        @motor_id: 马达序号，取值1(默认)或2
        @power: 马达能量，取值-100～100，大于0正转，小于0反转，0停止
        """
        motor_id = 1 if motor_id == 1 else 2
        power = int(power)
        if power > 100: power = 100
        if power < 100: power = -100
        command = "import parrot;parrot.set_speed({},{})".format(motor_id, power)
        self.send(command)

    def set_motor_stop(self, motor_id=1):
        """
        停止掌控宝M1、M2马达
        @motor_id: 马达序号，取值1(默认)或2
        """
        motor_id = 1 if motor_id == 1 else 2
        command = "import parrot;parrot.set_speed({},0)".format(motor_id)
        self.send(command)

    ## 属性
    def get_digital(self, pin):
        """
        @param pin: 0, 1, 2, 8, 9, 10, 13, 14, 15, 16
        """
        if not pin in [0, 1, 2, 8, 9, 10, 13, 14, 15, 16]: return 0
        command = "_pind[{}]=1".format(pin)
        self.send(command)
        return self.SENSORS['pinD'][pin]

    def get_analog(self, pin):
        """
        @param pin: 0, 1, 2
        """
        if not pin in [0, 1, 2]: return 0
        command = "_pina[{}]=1".format(pin)
        self.send(command)
        return self.SENSORS['pinA'][pin]

    def get_button(self, button):
        button = button.upper()
        if not button in ['P', 'Y', 'T', 'H', 'O', 'N', 'A', 'B']: return False
        return self.SENSORS[button]

    def get_acceleration(self, axis):
        axis = axis.upper()
        if not axis in ['X', 'Y', 'Z']: return 0
        return self.SENSORS['a' + axis]

    def get_light(self):
        return self.SENSORS['L']

    def get_sound(self):
        return self.SENSORS['S']

    def get_ext(self):
        return self.SENSORS['E']

    ## 事件
    def on_a_pressed(self): pass
    def on_a_released(self): pass
    def on_b_pressed(self): pass
    def on_b_released(self): pass
    def on_p_pressed(self): pass
    def on_p_released(self): pass
    def on_y_pressed(self): pass
    def on_y_released(self): pass
    def on_t_pressed(self): pass
    def on_t_released(self): pass
    def on_h_pressed(self): pass
    def on_h_released(self): pass
    def on_o_pressed(self): pass
    def on_o_released(self): pass
    def on_n_pressed(self): pass
    def on_n_released(self): pass
    def on_shaken(self): pass
    def on_jumped(self): pass
    def on_tilt_forward(self):pass
    def on_tilt_back(self):pass
    def on_tilt_right(self):pass
    def on_tilt_left(self):pass
    def on_tilt_none(self):pass


@atexit.register
def atexit_fun():
    controller().disconnect()
