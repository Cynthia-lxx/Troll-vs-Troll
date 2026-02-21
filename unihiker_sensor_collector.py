#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNIHIKER M10 传感器数据采集器
版本: 1.4.0
基于UNIHIKER只能上传一个文件的限制，专门负责传感器数据采集和传输

功能：
- 实时读取UNIHIKER内置传感器数据
- 通过串口将数据传输到本地计算机
- 简单的状态显示
- 最小化的资源占用
"""

import time
import json
import threading
from collections import deque

# UNIHIKER特定导入
try:
    from pinpong.board import Board, Pin, UART
    from unihiker import GUI
    UNIHIKER_AVAILABLE = True
except ImportError:
    print("警告: 无法导入UNIHIKER库，使用模拟模式")
    UNIHIKER_AVAILABLE = False

class UNIHikerSensorCollector:
    """UNIHIKER传感器数据采集器"""
    
    def __init__(self):
        self.uart = None
        self.gui = None
        self.connected = False
        self.running = False
        self.sensor_data = {}
        self.display_data = {}
        
    def initialize_hardware(self):
        """初始化硬件组件"""
        print("正在初始化UNIHIKER硬件...")
        
        # 初始化串口通信
        if UNIHIKER_AVAILABLE:
            try:
                Board("UNIHIKER").begin()
                self.uart = UART()
                self.uart.init(baud_rate=115200, bits=8, parity=0, stop=1)
                self.connected = True
                print("串口通信初始化成功")
            except Exception as e:
                print(f"串口初始化失败: {e}")
                return False
        else:
            self.connected = True
            print("模拟模式: 串口通信初始化成功")
        
        # 初始化GUI显示
        if UNIHIKER_AVAILABLE:
            try:
                self.gui = GUI()
                print("GUI显示初始化成功")
            except Exception as e:
                print(f"GUI初始化失败: {e}")
        
        return True
    
    def read_sensors(self):
        """读取所有传感器数据"""
        try:
            if UNIHIKER_AVAILABLE:
                # 导入传感器模块
                from pinpong.extension.unihiker import *
                
                # 读取传感器数据
                sensor_data = {
                    'timestamp': time.time(),
                    'light': light.read() if 'light' in globals() else 0,
                    'acceleration': {
                        'x': accelerometer.get_x() if 'accelerometer' in globals() else 0,
                        'y': accelerometer.get_y() if 'accelerometer' in globals() else 0,
                        'z': accelerometer.get_z() if 'accelerometer' in globals() else 9.8,
                        'strength': accelerometer.get_strength() if 'accelerometer' in globals() else 9.8
                    },
                    'gyro': {
                        'x': gyroscope.get_x() if 'gyroscope' in globals() else 0,
                        'y': gyroscope.get_y() if 'gyroscope' in globals() else 0,
                        'z': gyroscope.get_z() if 'gyroscope' in globals() else 0
                    },
                    'buttons': {
                        'A': button_a.is_pressed() if 'button_a' in globals() else False,
                        'B': button_b.is_pressed() if 'button_b' in globals() else False
                    }
                }
            else:
                # 模拟传感器数据
                import numpy as np
                sensor_data = {
                    'timestamp': time.time(),
                    'light': int(np.random.randint(0, 4096)),
                    'acceleration': {
                        'x': float(np.random.uniform(-2, 2)),
                        'y': float(np.random.uniform(-2, 2)),
                        'z': float(np.random.uniform(8, 12)),
                        'strength': float(np.random.uniform(9, 13))
                    },
                    'gyro': {
                        'x': float(np.random.uniform(-100, 100)),
                        'y': float(np.random.uniform(-100, 100)),
                        'z': float(np.random.uniform(-100, 100))
                    },
                    'buttons': {
                        'A': False,
                        'B': False
                    }
                }
            
            return sensor_data
            
        except Exception as e:
            print(f"传感器读取错误: {e}")
            return {'timestamp': time.time(), 'error': str(e)}
    
    def send_data(self, data):
        """通过串口发送数据"""
        if not self.connected:
            return False
            
        try:
            # 构造传输数据包
            packet = {
                'type': 'sensor_data',
                'data': data,
                'device_id': 'UNIHIKER_M10_001'
            }
            
            # JSON序列化
            json_data = json.dumps(packet, ensure_ascii=False)
            message = f"DATA_START{json_data}DATA_END"
            
            if UNIHIKER_AVAILABLE and self.uart:
                # 实际串口发送
                self.uart.write([ord(c) for c in message])
            else:
                # 模拟发送（调试用）
                print(f"[发送] {message[:50]}...")
                
            return True
        except Exception as e:
            print(f"数据发送失败: {e}")
            return False
    
    def update_display(self):
        """更新显示屏内容"""
        if not self.gui:
            return
            
        try:
            # 清除屏幕
            self.gui.clear()
            
            # 显示基本信息
            y_pos = 10
            self.gui.draw_text(x=10, y=y_pos, text="UNIHIKER数据采集器", font_size=16)
            y_pos += 25
            
            # 显示连接状态
            status = "已连接" if self.connected else "未连接"
            self.gui.draw_text(x=10, y=y_pos, text=f"状态: {status}", font_size=12)
            y_pos += 20
            
            # 显示传感器数据摘要
            if 'light' in self.display_data:
                self.gui.draw_text(x=10, y=y_pos, text=f"光线: {self.display_data['light']}", font_size=12)
                y_pos += 15
            
            if 'acceleration' in self.display_data:
                acc = self.display_data['acceleration']
                self.gui.draw_text(x=10, y=y_pos, text=f"加速度: ({acc['x']:.1f}, {acc['y']:.1f}, {acc['z']:.1f})", font_size=10)
                y_pos += 15
            
            # 显示时间
            current_time = time.strftime("%H:%M:%S")
            self.gui.draw_text(x=10, y=220, text=f"时间: {current_time}", font_size=10)
            
        except Exception as e:
            print(f"显示更新错误: {e}")
    
    def data_collection_loop(self):
        """数据采集主循环"""
        print("数据采集循环启动")
        last_send_time = 0
        send_interval = 0.1  # 100ms发送间隔
        
        while self.running:
            try:
                current_time = time.time()
                
                # 读取传感器数据
                sensor_data = self.read_sensors()
                self.display_data = sensor_data
                
                # 定期发送数据
                if current_time - last_send_time >= send_interval:
                    self.send_data(sensor_data)
                    last_send_time = current_time
                
                # 短暂休眠
                time.sleep(0.05)
                
            except Exception as e:
                print(f"数据采集循环错误: {e}")
                time.sleep(0.1)
    
    def start(self):
        """启动数据采集器"""
        if not self.initialize_hardware():
            print("硬件初始化失败，退出程序")
            return False
        
        self.running = True
        
        # 启动数据采集线程
        collection_thread = threading.Thread(target=self.data_collection_loop, daemon=True)
        collection_thread.start()
        
        print("UNIHIKER传感器数据采集器启动成功")
        print("正在采集并传输传感器数据...")
        
        try:
            # 主线程负责显示更新
            while self.running:
                self.update_display()
                time.sleep(0.2)
                
        except KeyboardInterrupt:
            print("\n收到停止信号")
        finally:
            self.stop()
    
    def stop(self):
        """停止数据采集器"""
        self.running = False
        print("UNIHIKER传感器数据采集器已停止")

def main():
    """主函数"""
    print("=" * 50)
    print("UNIHIKER M10 传感器数据采集器")
    print("版本: 1.4.0")
    print("专为单文件上传限制设计")
    print("=" * 50)
    
    collector = UNIHikerSensorCollector()
    collector.start()

if __name__ == "__main__":
    main()