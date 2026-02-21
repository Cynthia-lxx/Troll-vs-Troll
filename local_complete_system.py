#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Troll-vs-Troll 本地完整控制系统
版本: 1.4.0
基于UNIHIKER单文件上传限制的新架构设计

功能：
- 接收来自UNIHIKER的传感器数据
- 执行完整的数据处理、风险预测、差速控制
- 机器学习模型训练和优化
- 实时显示和用户界面
- 数据记录和分析
"""

import threading
import time
import sys
import os
import json
import serial
from collections import deque
import numpy as np
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ml.rollover_prediction import RolloverPredictor
from src.sensors.data_processor import SensorDataProcessor
from src.control.differential_controller import DifferentialController
from src.utils.data_generator import SensorDataGenerator
from src.ml.offline_trainer import OfflineTrainer

class EnhancedSerialCommunicator:
    """增强版串口通信管理器"""
    
    def __init__(self, port='COM3', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.connected = False
        self.receive_buffer = ""
        self.data_queue = deque(maxlen=100)
        
    def connect(self):
        """建立串口连接"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self.connected = True
            print(f"串口连接成功: {self.port} @ {self.baudrate}bps")
            return True
        except Exception as e:
            print(f"串口连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开串口连接"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.connected = False
        
    def send_command(self, command_type, data=None):
        """发送命令到UNIHIKER"""
        if not self.connected:
            return False
            
        try:
            packet = {
                'type': command_type,
                'data': data,
                'timestamp': time.time()
            }
            message = f"CMD_START{json.dumps(packet)}CMD_END"
            self.serial_conn.write(message.encode('utf-8'))
            return True
        except Exception as e:
            print(f"发送命令失败: {e}")
            return False
    
    def receive_data_packets(self):
        """接收数据包"""
        if not self.connected:
            return []
            
        try:
            if self.serial_conn.in_waiting > 0:
                data = self.serial_conn.read(self.serial_conn.in_waiting)
                self.receive_buffer += data.decode('utf-8', errors='ignore')
            
            packets = []
            while True:
                start_idx = self.receive_buffer.find("DATA_START")
                end_idx = self.receive_buffer.find("DATA_END")
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    message = self.receive_buffer[start_idx+10:end_idx]
                    self.receive_buffer = self.receive_buffer[end_idx+8:]
                    
                    try:
                        packet = json.loads(message)
                        packets.append(packet)
                    except json.JSONDecodeError:
                        continue
                else:
                    break
                    
            return packets
        except Exception as e:
            print(f"接收数据包失败: {e}")
            return []

class LocalControlSystem:
    """本地完整控制系统"""
    
    def __init__(self):
        self.communicator = None
        self.rollover_predictor = None
        self.sensor_processor = None
        self.differential_controller = None
        self.offline_trainer = None
        self.data_generator = None
        
        self.running = False
        self.current_sensor_data = None
        self.control_output = None
        self.risk_assessment = None
        self.system_stats = {
            'packets_received': 0,
            'processing_errors': 0,
            'last_update': None
        }
        
        # 物理参数配置
        self.bag_params = {
            'bag_length': 0.5,      # 米
            'bag_width': 0.3,       # 米
            'bag_height': 0.7,      # 米
            'center_of_gravity_height': 0.4,  # 米
            'wheel_radius': 0.1,    # 米
            'wheel_mass': 0.5,      # 千克
            'bag_total_mass': 5.0   # 千克
        }
    
    def initialize_system(self):
        """初始化完整系统"""
        print("正在初始化本地控制系统...")
        
        try:
            # 初始化核心组件
            self.rollover_predictor = RolloverPredictor(**self.bag_params)
            self.sensor_processor = SensorDataProcessor()
            self.differential_controller = DifferentialController(**self.bag_params)
            self.offline_trainer = OfflineTrainer()
            self.data_generator = SensorDataGenerator(seed=int(time.time()))
            
            print("核心组件初始化成功！")
            return True
            
        except Exception as e:
            print(f"系统初始化失败: {e}")
            return False
    
    def process_sensor_data(self, sensor_packet):
        """处理传感器数据包"""
        try:
            if sensor_packet.get('type') != 'sensor_data':
                return None
                
            sensor_data = sensor_packet.get('data', {})
            
            # 提取传感器数据
            accel_data = [
                sensor_data['acceleration']['x'],
                sensor_data['acceleration']['y'],
                sensor_data['acceleration']['z']
            ]
            gyro_data = [
                sensor_data['gyro']['x'],
                sensor_data['gyro']['y'],
                sensor_data['gyro']['z']
            ]
            
            # 处理传感器数据
            self.sensor_processor.add_accel_data(accel_data)
            self.sensor_processor.add_gyro_data(gyro_data)
            
            # 预测侧翻风险
            self.risk_assessment = self.rollover_predictor.predict_rollover_risk(accel_data, gyro_data)
            
            # 计算差速控制
            self.control_output = self.differential_controller.update_control(accel_data, gyro_data)
            
            # 在线学习更新
            processed_features = self.sensor_processor.get_processed_features()
            if processed_features:
                feature_vector = [
                    accel_data[0], accel_data[1], accel_data[2],
                    gyro_data[0], gyro_data[1], gyro_data[2],
                    processed_features['orientation']['pitch'],
                    processed_features['orientation']['roll']
                ]
                self.rollover_predictor.update_model(feature_vector)
            
            # 更新统计数据
            self.current_sensor_data = sensor_data
            self.system_stats['packets_received'] += 1
            self.system_stats['last_update'] = time.time()
            
            return {
                'sensor_data': sensor_data,
                'risk_assessment': self.risk_assessment,
                'control_output': self.control_output,
                'processed_features': processed_features
            }
            
        except Exception as e:
            self.system_stats['processing_errors'] += 1
            print(f"数据处理错误: {e}")
            return None
    
    def display_system_status(self):
        """显示系统状态"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 60)
        print("TROLL-VS-TROLL 本地控制系统 (版本 1.4.0)")
        print("=" * 60)
        
        # 系统状态
        conn_status = "已连接" if self.communicator and self.communicator.connected else "未连接"
        print(f"串口状态: {conn_status}")
        print(f"数据包接收: {self.system_stats['packets_received']}")
        print(f"处理错误: {self.system_stats['processing_errors']}")
        if self.system_stats['last_update']:
            print(f"最后更新: {datetime.fromtimestamp(self.system_stats['last_update']).strftime('%H:%M:%S')}")
        
        print("-" * 60)
        
        # 传感器数据
        if self.current_sensor_data:
            print("传感器数据:")
            sd = self.current_sensor_data
            print(f"  光线强度: {sd.get('light', 0)}")
            acc = sd['acceleration']
            print(f"  加速度: X={acc['x']:.2f}, Y={acc['y']:.2f}, Z={acc['z']:.2f}")
            gyro = sd['gyro']
            print(f"  陀螺仪: X={gyro['x']:.1f}, Y={gyro['y']:.1f}, Z={gyro['z']:.1f}")
        
        print("-" * 60)
        
        # 风险评估
        if self.risk_assessment:
            ra = self.risk_assessment
            print(f"风险评估: {ra['risk_level']} ({ra['risk_score']*100:.1f}%)")
            print(f"  倾斜角度: 俯仰={ra.get('pitch_angle', 0):.1f}°, 翻滚={ra.get('roll_angle', 0):.1f}°")
            print(f"  角速度: {ra.get('angular_velocity_magnitude', 0):.1f} °/s")
        
        print("-" * 60)
        
        # 控制输出
        if self.control_output:
            co = self.control_output
            print(f"差速控制: {'激活' if co['control_active'] else '待机'}")
            print(f"  左轮速度: {co['left_wheel_speed']:.3f}")
            print(f"  右轮速度: {co['right_wheel_speed']:.3f}")
            print(f"  速度差: {abs(co['left_wheel_speed'] - co['right_wheel_speed']):.3f}")
        
        print("-" * 60)
        
        # 训练数据统计
        if self.offline_trainer:
            stats = self.offline_trainer.get_training_statistics()
            print("训练数据统计:")
            print(f"  总片段数: {stats.get('total_segments', 0)}")
            print(f"  正样本: {stats.get('positive_samples', 0)}")
            print(f"  负样本: {stats.get('negative_samples', 0)}")
        
        print("=" * 60)
        print("按 Ctrl+C 退出系统")
    
    def data_processing_loop(self):
        """数据处理主循环"""
        print("数据处理循环启动")
        
        while self.running:
            try:
                # 接收数据包
                packets = self.communicator.receive_data_packets()
                
                for packet in packets:
                    # 处理每个数据包
                    result = self.process_sensor_data(packet)
                    if result:
                        # 可以在这里添加更多的处理逻辑
                        pass
                
                time.sleep(0.01)  # 10ms循环周期
                
            except Exception as e:
                print(f"数据处理循环错误: {e}")
                time.sleep(0.1)
    
    def start_with_unihiker(self, com_port='COM3'):
        """启动与UNIHIKER的连接"""
        # 初始化串口通信
        self.communicator = EnhancedSerialCommunicator(port=com_port, baudrate=115200)
        if not self.communicator.connect():
            print("串口连接失败，请检查：")
            print("1. UNIHIKER是否已通过USB连接到电脑")
            print("2. 是否安装了正确的USB转串口驱动")
            print("3. COM端口号是否正确")
            return False
        
        # 初始化系统
        if not self.initialize_system():
            return False
        
        self.running = True
        
        # 启动数据处理线程
        processing_thread = threading.Thread(target=self.data_processing_loop, daemon=True)
        processing_thread.start()
        
        print("本地控制系统启动成功！")
        print("正在等待来自UNIHIKER的数据...")
        
        try:
            # 主线程负责显示更新
            last_display_update = 0
            display_interval = 0.5  # 500ms更新显示
            
            while self.running:
                current_time = time.time()
                if current_time - last_display_update >= display_interval:
                    self.display_system_status()
                    last_display_update = current_time
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n收到停止信号")
        finally:
            self.stop()
        
        return True
    
    def start_simulation_mode(self):
        """启动纯模拟模式"""
        print("启动纯模拟测试模式...")
        
        if not self.initialize_system():
            return False
        
        self.running = True
        
        try:
            scenario_idx = 0
            scenarios = ["normal", "turning", "risky", "rollover_imminent"]
            last_display_update = 0
            display_interval = 0.5
            
            while self.running:
                current_time = time.time()
                
                # 切换测试场景
                if int(current_time) % 10 == 0:
                    scenario_idx = (scenario_idx + 1) % len(scenarios)
                    self.data_generator.set_scenario(scenarios[scenario_idx])
                    print(f"\n>>> 切换到场景: {scenarios[scenario_idx]}")
                
                # 生成模拟数据
                accel_data = self.data_generator.generate_accel_data()
                gyro_data = self.data_generator.generate_gyro_data()
                
                # 模拟数据包格式
                mock_packet = {
                    'type': 'sensor_data',
                    'data': {
                        'timestamp': current_time,
                        'light': np.random.randint(0, 4096),
                        'acceleration': {
                            'x': accel_data[0], 'y': accel_data[1], 'z': accel_data[2],
                            'strength': np.linalg.norm(accel_data)
                        },
                        'gyro': {
                            'x': gyro_data[0], 'y': gyro_data[1], 'z': gyro_data[2]
                        },
                        'buttons': {'A': False, 'B': False}
                    }
                }
                
                # 处理数据
                self.process_sensor_data(mock_packet)
                
                # 更新显示
                if current_time - last_display_update >= display_interval:
                    self.display_system_status()
                    last_display_update = current_time
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n模拟测试结束")
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """停止系统"""
        self.running = False
        if self.communicator:
            self.communicator.disconnect()
        print("本地控制系统已停止")

def main():
    """主函数"""
    print("=" * 60)
    print("TROLL-VS-TROLL 本地完整控制系统")
    print("版本 1.4.0 - 新架构设计")
    print("基于UNIHIKER单文件上传限制优化")
    print("=" * 60)
    
    system = LocalControlSystem()
    
    print("\n请选择运行模式：")
    print("1. 与UNIHIKER硬件连接（真实传感器数据）")
    print("2. 纯模拟模式（测试算法功能）")
    
    try:
        choice = input("\n请输入选择 (1 或 2): ").strip()
        
        if choice == "1":
            com_port = input("请输入COM端口号 (默认COM3): ").strip() or "COM3"
            system.start_with_unihiker(com_port)
        elif choice == "2":
            system.start_simulation_mode()
        else:
            print("无效选择")
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")

if __name__ == "__main__":
    main()