#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNIHIKER M10 协同工作版本
基于官方文档的正确通信方式实现与本地程序的协作
"""

import time
import json
import threading
from collections import deque
import numpy as np

# UNIHIKER特定导入
try:
    from pinpong.board import Board, Pin, UART
    from unihiker import GUI
    UNIHIKER_AVAILABLE = True
except ImportError:
    print("警告: 无法导入UNIHIKER库，使用模拟模式")
    UNIHIKER_AVAILABLE = False

class UNIHikerCommunicator:
    """UNIHIKER通信管理器"""
    
    def __init__(self):
        self.uart = None
        self.connected = False
        self.send_queue = deque()
        self.receive_buffer = ""
        
    def initialize_uart(self, baud_rate=115200):
        """初始化串口通信"""
        if not UNIHIKER_AVAILABLE:
            print("模拟模式: 初始化虚拟串口")
            self.connected = True
            return True
            
        try:
            Board("UNIHIKER").begin()
            self.uart = UART()
            self.uart.init(baud_rate=baud_rate, bits=8, parity=0, stop=1)
            self.connected = True
            print(f"串口通信初始化成功，波特率: {baud_rate}")
            return True
        except Exception as e:
            print(f"串口初始化失败: {e}")
            return False
    
    def send_data(self, data_dict):
        """发送数据到本地程序"""
        if not self.connected:
            return False
            
        try:
            # 将数据转换为JSON格式
            json_data = json.dumps(data_dict)
            # 添加帧头帧尾便于解析
            message = f"START{json_data}END"
            
            if UNIHIKER_AVAILABLE and self.uart:
                # 实际串口发送
                self.uart.write([ord(c) for c in message])
            else:
                # 模拟发送（调试用）
                print(f"[发送] {message}")
                
            return True
        except Exception as e:
            print(f"发送数据失败: {e}")
            return False
    
    def receive_data(self):
        """接收来自本地程序的数据"""
        if not self.connected:
            return None
            
        try:
            if UNIHIKER_AVAILABLE and self.uart:
                # 读取串口数据
                if self.uart.any():
                    data = self.uart.read(self.uart.any())
                    if data:
                        self.receive_buffer += ''.join(chr(b) for b in data)
            else:
                # 模拟接收（调试用）
                pass
                
            # 解析完整的消息
            start_idx = self.receive_buffer.find("START")
            end_idx = self.receive_buffer.find("END")
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                message = self.receive_buffer[start_idx+5:end_idx]
                self.receive_buffer = self.receive_buffer[end_idx+3:]
                
                try:
                    return json.loads(message)
                except json.JSONDecodeError:
                    pass
                    
            return None
        except Exception as e:
            print(f"接收数据失败: {e}")
            return None

class UNIHikerSensorReader:
    """UNIHIKER传感器读取器"""
    
    def __init__(self):
        self.light_sensor = None
        self.accelerometer = None
        self.gyroscope = None
        self.button_a = None
        self.button_b = None
        
    def initialize_sensors(self):
        """初始化传感器"""
        if not UNIHIKER_AVAILABLE:
            print("模拟模式: 初始化虚拟传感器")
            return True
            
        try:
            from pinpong.extension.unihiker import *
            Board().begin()
            
            # 传感器已经在pinpong库中自动初始化
            self.light_sensor = light
            self.accelerometer = accelerometer
            self.gyroscope = gyroscope
            self.button_a = button_a
            self.button_b = button_b
            
            print("传感器初始化成功")
            return True
        except Exception as e:
            print(f"传感器初始化失败: {e}")
            return False
    
    def read_all_sensors(self):
        """读取所有传感器数据"""
        sensor_data = {}
        
        try:
            if UNIHIKER_AVAILABLE:
                # 实际传感器读取
                sensor_data.update({
                    'timestamp': time.time(),
                    'light': self.light_sensor.read() if self.light_sensor else 0,
                    'acceleration': {
                        'x': self.accelerometer.get_x() if self.accelerometer else 0,
                        'y': self.accelerometer.get_y() if self.accelerometer else 0,
                        'z': self.accelerometer.get_z() if self.accelerometer else 0,
                        'strength': self.accelerometer.get_strength() if self.accelerometer else 0
                    },
                    'gyro': {
                        'x': self.gyroscope.get_x() if self.gyroscope else 0,
                        'y': self.gyroscope.get_y() if self.gyroscope else 0,
                        'z': self.gyroscope.get_z() if self.gyroscope else 0
                    },
                    'buttons': {
                        'A': self.button_a.is_pressed() if self.button_a else False,
                        'B': self.button_b.is_pressed() if self.button_b else False
                    }
                })
            else:
                # 模拟传感器数据
                sensor_data.update({
                    'timestamp': time.time(),
                    'light': np.random.randint(0, 4096),
                    'acceleration': {
                        'x': np.random.uniform(-1, 1),
                        'y': np.random.uniform(-1, 1),
                        'z': np.random.uniform(-1, 1),
                        'strength': np.random.uniform(0, 2)
                    },
                    'gyro': {
                        'x': np.random.uniform(-500, 500),
                        'y': np.random.uniform(-500, 500),
                        'z': np.random.uniform(-500, 500)
                    },
                    'buttons': {
                        'A': False,
                        'B': False
                    }
                })
                
        except Exception as e:
            print(f"传感器读取错误: {e}")
            sensor_data['error'] = str(e)
            
        return sensor_data

class UNIHikerController:
    """UNIHIKER主控制器"""
    
    def __init__(self):
        self.communicator = UNIHikerCommunicator()
        self.sensor_reader = UNIHikerSensorReader()
        self.gui = None
        self.running = False
        self.control_signal = 0.0
        self.display_data = {}
        
    def initialize(self):
        """初始化所有组件"""
        print("正在初始化UNIHIKER协同工作系统...")
        
        # 初始化GUI
        if UNIHIKER_AVAILABLE:
            try:
                self.gui = GUI()
                print("GUI初始化成功")
            except Exception as e:
                print(f"GUI初始化失败: {e}")
        
        # 初始化通信
        if not self.communicator.initialize_uart():
            print("警告: 串口通信初始化失败")
        
        # 初始化传感器
        if not self.sensor_reader.initialize_sensors():
            print("警告: 传感器初始化失败")
        
        print("UNIHIKER协同工作系统初始化完成")
        return True
    
    def update_display(self):
        """更新显示屏内容"""
        if not self.gui:
            return
            
        try:
            # 清除屏幕
            self.gui.clear()
            
            # 显示状态信息
            y_pos = 10
            self.gui.draw_text(x=10, y=y_pos, text="UNIHIKER协同工作模式", font_size=16)
            y_pos += 25
            
            # 显示连接状态
            status = "已连接" if self.communicator.connected else "未连接"
            self.gui.draw_text(x=10, y=y_pos, text=f"通信状态: {status}", font_size=12)
            y_pos += 20
            
            # 显示控制信号
            self.gui.draw_text(x=10, y=y_pos, text=f"控制信号: {self.control_signal:.3f}", font_size=12)
            y_pos += 20
            
            # 显示传感器数据摘要
            if 'light' in self.display_data:
                self.gui.draw_text(x=10, y=y_pos, text=f"光线: {self.display_data['light']}", font_size=12)
                y_pos += 15
            
            if 'acceleration' in self.display_data:
                acc = self.display_data['acceleration']
                self.gui.draw_text(x=10, y=y_pos, text=f"加速度: ({acc['x']:.2f}, {acc['y']:.2f}, {acc['z']:.2f})", font_size=10)
                y_pos += 15
            
            # 显示按钮状态
            if 'buttons' in self.display_data:
                buttons = self.display_data['buttons']
                btn_status = f"A: {'按下' if buttons['A'] else '释放'}  B: {'按下' if buttons['B'] else '释放'}"
                self.gui.draw_text(x=10, y=y_pos, text=btn_status, font_size=12)
                
        except Exception as e:
            print(f"显示更新错误: {e}")
    
    def communication_thread(self):
        """通信处理线程"""
        print("通信线程启动")
        
        last_send_time = 0
        send_interval = 0.1  # 100ms发送间隔
        
        while self.running:
            try:
                current_time = time.time()
                
                # 接收控制信号
                received_data = self.communicator.receive_data()
                if received_data and 'control_signal' in received_data:
                    self.control_signal = received_data['control_signal']
                    print(f"接收到控制信号: {self.control_signal:.3f}")
                
                # 定期发送传感器数据
                if current_time - last_send_time >= send_interval:
                    sensor_data = self.sensor_reader.read_all_sensors()
                    sensor_data['control_signal'] = self.control_signal
                    
                    if self.communicator.send_data(sensor_data):
                        self.display_data = sensor_data
                        last_send_time = current_time
                
                time.sleep(0.01)  # 10ms循环周期
                
            except Exception as e:
                print(f"通信线程错误: {e}")
                time.sleep(0.1)
    
    def start(self):
        """启动协同工作系统"""
        if not self.initialize():
            return False
            
        self.running = True
        
        # 启动通信线程
        comm_thread = threading.Thread(target=self.communication_thread, daemon=True)
        comm_thread.start()
        
        print("UNIHIKER协同工作系统启动成功")
        print("等待与本地程序建立连接...")
        
        try:
            while self.running:
                # 更新显示
                self.update_display()
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n收到停止信号")
        finally:
            self.stop()
    
    def stop(self):
        """停止系统"""
        self.running = False
        print("UNIHIKER协同工作系统已停止")

def main():
    """主函数"""
    print("=" * 50)
    print("UNIHIKER M10 协同工作系统")
    print("基于官方文档的正确通信实现")
    print("=" * 50)
    
    controller = UNIHikerController()
    controller.start()

if __name__ == "__main__":
    main()