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
    """UNIHIKER 传感器数据采集器（离线批处理模式）"""
    
    def __init__(self, config_file='m10_config.json'):
        self.uart = None
        self.gui = None
        self.connected = False
        self.running = False
        self.sensor_data = {}
        self.display_data = {}
        self.config_file = config_file
        self.config = None
        self.data_buffer = deque(maxlen=1000)  # 数据缓存
        self.last_heartbeat = 0
        self.export_triggered = False
        
    def initialize_hardware(self):
        """初始化硬件组件并加载配置"""
        print("正在初始化 UNIHIKER 硬件...")
            
        # 加载配置文件
        self.load_config()
            
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
    
    def load_config(self):
        """从外部文件加载配置"""
        try:
            import os
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print(f"配置加载成功：{self.config_file}")
                print(f"  采样率：{self.config.get('sampling_rate', 100)} Hz")
                print(f"  风险阈值：{self.config.get('risk_thresholds', {})}")
            else:
                print("未找到配置文件，使用默认参数")
                self.config = {
                    'sampling_rate': 100,
                    'risk_thresholds': {'low': 0.3, 'medium': 0.6, 'high': 0.8}
                }
        except Exception as e:
            print(f"配置加载失败：{e}，使用默认参数")
            self.config = {
                'sampling_rate': 100,
                'risk_thresholds': {'low': 0.3, 'medium': 0.6, 'high': 0.8}
            }
    
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
        """将数据添加到缓存（不再实时发送）"""
        try:
            # 将数据添加到缓存
            self.data_buffer.append({
                'timestamp': time.time(),
                'data': data,
                'config_version': self.config.get('version', 'unknown') if self.config else 'none'
            })
            return True
        except Exception as e:
            print(f"数据缓存失败：{e}")
            return False
        
    def export_buffer_to_console(self):
        """导出缓存数据到控制台"""
        if not self.data_buffer:
            print("[EXPORT] 无数据可导出")
            return
            
        print("\n" + "="*50)
        print("DATA_EXPORT_START")
        print("="*50)
            
        export_data = {
            'device_id': 'UNIHIKER_M10_001',
            'export_timestamp': time.time(),
            'config_used': self.config,
            'total_readings': len(self.data_buffer),
            'sensor_readings': list(self.data_buffer)
        }
            
        print(json.dumps(export_data, ensure_ascii=False, indent=2))
            
        print("="*50)
        print("DATA_EXPORT_END")
        print("="*50)
        print("\n提示：请复制以上全部内容，粘贴到计算机端导入界面")
            
        # 导出后清空缓存
        self.data_buffer.clear()
        print(f"已清空缓存 ({len(self.data_buffer)} 条记录)")
    
    def update_display(self):
        """更新显示屏内容"""
        if not self.gui:
            return
            
        try:
            # 清除屏幕
            self.gui.clear()
            
            # 显示基本信息
            y_pos = 10
            self.gui.draw_text(x=10, y=y_pos, text="M10 数据采集器 (离线模式)", font_size=16)
            y_pos += 25
            
            # 显示连接状态
            status = "运行中" if self.running else "已停止"
            self.gui.draw_text(x=10, y=y_pos, text=f"状态：{status}", font_size=12)
            y_pos += 20
            
            # 显示缓存数据量
            buffer_size = len(self.data_buffer)
            max_size = self.data_buffer.maxlen
            self.gui.draw_text(x=10, y=y_pos, text=f"缓存：{buffer_size}/{max_size}", font_size=12)
            y_pos += 20
            
            # 显示传感器数据摘要
            if 'light' in self.display_data:
                self.gui.draw_text(x=10, y=y_pos, text=f"光线：{self.display_data['light']}", font_size=12)
                y_pos += 15
            
            if 'acceleration' in self.display_data:
                acc = self.display_data['acceleration']
                self.gui.draw_text(x=10, y=y_pos, text=f"加速度：({acc['x']:.1f}, {acc['y']:.1f}, {acc['z']:.1f})", font_size=10)
                y_pos += 15
            
            # 显示操作提示
            self.gui.draw_text(x=10, y=200, text="按 A 键导出数据", font_size=10, color="blue")
            
            # 显示时间
            current_time = time.strftime("%H:%M:%S")
            self.gui.draw_text(x=10, y=220, text=f"时间：{current_time}", font_size=10)
            
        except Exception as e:
            print(f"显示更新错误：{e}")
    
    def data_collection_loop(self):
        """数据采集主循环（离线批处理模式）"""
        print("数据采集循环启动（离线模式）")
        last_send_time = 0
        send_interval = 0.1  # 100ms 采样间隔
        heartbeat_interval = 5.0  # 5 秒心跳间隔
            
        while self.running:
            try:
                current_time = time.time()
                    
                # 读取传感器数据
                sensor_data = self.read_sensors()
                self.display_data = sensor_data
                    
                # 将数据添加到缓存（不再实时发送）
                if current_time - last_send_time >= send_interval:
                    self.send_data(sensor_data)
                    last_send_time = current_time
                    
                # 定期打印心跳日志
                if current_time - self.last_heartbeat >= heartbeat_interval:
                    buffer_size = len(self.data_buffer)
                    max_size = self.data_buffer.maxlen
                    print(f"[LIVE] Heartbeat: OK | 缓存：{buffer_size}/{max_size} | 运行正常")
                    self.last_heartbeat = current_time
                    
                # 检查导出触发（A 按钮）
                if UNIHIKER_AVAILABLE:
                    try:
                        from pinpong.extension.unihiker import button_a
                        if button_a.is_pressed():
                            print("\n检测到 A 按钮按下，准备导出数据...")
                            time.sleep(0.5)  # 消抖
                            if button_a.is_pressed():  # 确认按下
                                self.export_buffer_to_console()
                                time.sleep(1)  # 防止重复触发
                    except:
                        pass
                    
                # 短暂休眠
                time.sleep(0.05)
                    
            except Exception as e:
                print(f"数据采集循环错误：{e}")
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