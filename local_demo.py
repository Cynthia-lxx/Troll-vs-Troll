"""
Local Demo for Troll-vs-Troll Project
A complete system that integrates learning, detection, and differential control
with a web-based sensor simulator for testing purposes.

This script runs a local demonstration of the entire system without
requiring the UNIHIKER M10 hardware.
"""

import threading
import time
import sys
import os
import json
import serial
from collections import deque
from src.ml.rollover_prediction import RolloverPredictor
from src.sensors.data_processor import SensorDataProcessor
from src.control.differential_controller import DifferentialController
from src.utils.data_generator import SensorDataGenerator

class SerialCommunicator:
    """本地程序串口通信管理器"""
    
    def __init__(self, port='COM3', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.connected = False
        self.receive_buffer = ""
        
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
        
    def send_control_signal(self, control_signal):
        """发送控制信号到UNIHIKER"""
        if not self.connected:
            return False
            
        try:
            data = {
                'control_signal': float(control_signal),
                'timestamp': time.time()
            }
            message = f"START{json.dumps(data)}END"
            self.serial_conn.write(message.encode('utf-8'))
            return True
        except Exception as e:
            print(f"发送控制信号失败: {e}")
            return False
    
    def receive_sensor_data(self):
        """接收来自UNIHIKER的传感器数据"""
        if not self.connected:
            return None
            
        try:
            if self.serial_conn.in_waiting > 0:
                data = self.serial_conn.read(self.serial_conn.in_waiting)
                self.receive_buffer += data.decode('utf-8')
                
            # 解析完整消息
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
            print(f"接收传感器数据失败: {e}")
            return None

def run_web_server():
    """Import and run the web server in a separate thread."""
    from web_server import run_server
    run_server()

def run_local_system():
    """Run the complete local system with simulated data."""
    print("启动Troll-vs-Troll本地演示系统...")
    
    # Initialize all components with default physical parameters
    bag_params = {
        'bag_length': 0.5,  # meters
        'bag_width': 0.3,   # meters
        'bag_height': 0.7,  # meters
        'center_of_gravity_height': 0.4,  # meters
        'wheel_radius': 0.1,  # meters
        'wheel_mass': 0.5,    # kg
        'bag_total_mass': 5.0  # kg
    }
    
    rollover_predictor = RolloverPredictor(**bag_params)
    sensor_processor = SensorDataProcessor()
    differential_controller = DifferentialController(**bag_params)
    data_generator = SensorDataGenerator(seed=int(time.time()))
    
    print("系统初始化完成！")
    print("组件状态：")
    print(f"- 侧翻预测器: {'就绪' if rollover_predictor else '错误'}")
    print(f"- 传感器处理器: {'就绪' if sensor_processor else '错误'}")
    print(f"- 差速控制器: {'就绪' if differential_controller else '错误'}")
    print(f"- 数据生成器: {'就绪' if data_generator else '错误'}")
    
    print("\n使用说明：")
    print("- 运行Web服务器以通过网页界面模拟传感器输入")
    print("- 或使用随机数据生成器进行自动测试")
    
    # Ask user for input method
    print("\n请选择输入模式：")
    print("1. Web界面（通过浏览器拖动滑块）")
    print("2. 随机数据生成器（自动测试）")
    print("3. M10硬件协作模式（与UNIHIKER程序协同工作）")
    
    try:
        choice = input("请输入选择 (1 或 2): ").strip()
        
        if choice == "1":
            # Start web server in a separate thread
            server_thread = threading.Thread(target=run_web_server, daemon=True)
            server_thread.start()
            print("\nWeb服务器已在后台启动...")
            print("请访问 http://localhost:8080 查看传感器模拟器")
            print("按 Ctrl+C 退出程序\n")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n正在关闭系统...")
                return
                
        elif choice == "2":
            print("\n使用随机数据生成器进行自动测试...")
            print("按 Ctrl+C 退出程序\n")
            
        elif choice == "3":
            print("\n启动M10硬件协作模式...")
            print("此模式将与UNIHIKER上的协同工作程序协同工作")
            print("请确保已运行 unihiker_collaborative.py 程序")
            print("按 Ctrl+C 退出程序\n")
            
            try:
                # 初始化串口通信
                communicator = SerialCommunicator(port='COM3', baudrate=115200)
                if not communicator.connect():
                    print("串口连接失败，请检查：")
                    print("1. UNIHIKER是否已通过USB连接到电脑")
                    print("2. 是否安装了正确的USB转串口驱动")
                    print("3. COM端口号是否正确（Windows设备管理器中查看）")
                    return
                
                # 初始化协作模式组件
                from src.ml.offline_trainer import OfflineTrainer
                trainer = OfflineTrainer()
                
                print("协作模式组件初始化完成！")
                print("功能说明：")
                print("- 本地程序：处理复杂计算、模型训练、数据分析")
                print("- UNIHIKER程序：实时传感器读取、快速响应控制")
                print("- 通信方式：通过串口进行实时数据交换")
                
                # 检查是否有训练数据
                training_stats = trainer.get_training_statistics()
                print(f"\n当前训练数据统计：")
                print(f"  总片段数: {training_stats.get('total_segments', 0)}")
                print(f"  正样本数: {training_stats.get('positive_samples', 0)}")
                print(f"  负样本数: {training_stats.get('negative_samples', 0)}")
                print(f"  最后训练: {training_stats.get('last_training', '从未训练')}")
                
                print("\n等待接收来自UNIHIKER的传感器数据...")
                
                # 协作模式主循环
                last_update_time = 0
                update_interval = 0.1  # 100ms更新间隔
                
                while True:
                    current_time = time.time()
                    
                    # 接收来自UNIHIKER的传感器数据
                    sensor_data = communicator.receive_sensor_data()
                    
                    if sensor_data:
                        try:
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
                            sensor_processor.add_accel_data(accel_data)
                            sensor_processor.add_gyro_data(gyro_data)
                            
                            # 获取处理后的特征
                            processed_features = sensor_processor.get_processed_features()
                            
                            # 预测侧翻风险
                            risk_assessment = rollover_predictor.predict_rollover_risk(accel_data, gyro_data)
                            
                            # 更新控制器
                            control_result = differential_controller.update_control(accel_data, gyro_data)
                            
                            # 发送控制信号到UNIHIKER
                            control_signal = control_result['left_wheel_speed'] - control_result['right_wheel_speed']
                            communicator.send_control_signal(control_signal)
                            
                            # 显示结果
                            if current_time - last_update_time >= update_interval:
                                print(f"\n[{time.strftime('%H:%M:%S')}] 协作模式状态:")
                                print(f"  光线强度: {sensor_data.get('light', 0)}")
                                print(f"  加速度: X={accel_data[0]:.2f}, Y={accel_data[1]:.2f}, Z={accel_data[2]:.2f}")
                                print(f"  陀螺仪: X={gyro_data[0]:.2f}, Y={gyro_data[1]:.2f}, Z={gyro_data[2]:.2f}")
                                print(f"  风险等级: {risk_assessment['risk_level']} ({risk_assessment['risk_score']*100:.1f}%)")
                                print(f"  控制激活: {'是' if control_result['control_active'] else '否'}")
                                print(f"  轮速: 左={control_result['left_wheel_speed']:.3f}, 右={control_result['right_wheel_speed']:.3f}")
                                print(f"  控制信号: {control_signal:.3f}")
                                
                                last_update_time = current_time
                            
                            # 模型在线学习
                            if processed_features:
                                feature_vector = [
                                    accel_data[0], accel_data[1], accel_data[2],  # accel
                                    gyro_data[0], gyro_data[1], gyro_data[2],    # gyro
                                    processed_features['orientation']['pitch'],   # pitch
                                    processed_features['orientation']['roll']     # roll
                                ]
                                rollover_predictor.update_model(feature_vector)
                                
                        except KeyError as e:
                            print(f"传感器数据格式错误: 缺少字段 {e}")
                        except Exception as e:
                            print(f"数据处理错误: {e}")
                    
                    time.sleep(0.01)  # 10ms循环周期
                    
            except KeyboardInterrupt:
                print("\n正在关闭协作模式...")
                if 'communicator' in locals():
                    communicator.disconnect()
                return
            except Exception as e:
                print(f"协作模式运行出错: {e}")
                if 'communicator' in locals():
                    communicator.disconnect()
                return
            
            try:
                scenario_idx = 0
                scenarios = ["normal", "turning", "risky", "rollover_imminent"]
                
                while True:
                    # Switch scenarios periodically
                    if int(time.time()) % 10 == 0:  # Change scenario every 10 seconds
                        scenario_idx = (scenario_idx + 1) % len(scenarios)
                        data_generator.set_scenario(scenarios[scenario_idx])
                    
                    # Generate sensor data
                    accel_data = data_generator.generate_accel_data()
                    gyro_data = data_generator.generate_gyro_data()
                    
                    # Process sensor data
                    sensor_processor.add_accel_data(accel_data)
                    sensor_processor.add_gyro_data(gyro_data)
                    
                    # Get processed features
                    processed_features = sensor_processor.get_processed_features()
                    
                    # Predict rollover risk
                    risk_assessment = rollover_predictor.predict_rollover_risk(accel_data, gyro_data)
                    
                    # Update controller
                    control_result = differential_controller.update_control(accel_data, gyro_data)
                    
                    # Display results
                    print(f"\n[{time.strftime('%H:%M:%S')}] 当前状态:")
                    print(f"  场景: {data_generator.scenario}")
                    print(f"  加速度: X={accel_data[0]:.2f}, Y={accel_data[1]:.2f}, Z={accel_data[2]:.2f}")
                    print(f"  陀螺仪: X={gyro_data[0]:.2f}, Y={gyro_data[1]:.2f}, Z={gyro_data[2]:.2f}")
                    print(f"  风险等级: {risk_assessment['risk_level']} ({risk_assessment['risk_score']*100:.1f}%)")
                    print(f"  控制激活: {'是' if control_result['control_active'] else '否'}")
                    print(f"  轮速: 左={control_result['left_wheel_speed']:.3f}, 右={control_result['right_wheel_speed']:.3f}")
                    
                    # Update model with new data (simulating online learning)
                    if processed_features:
                        feature_vector = [
                            accel_data[0], accel_data[1], accel_data[2],  # accel
                            gyro_data[0], gyro_data[1], gyro_data[2],    # gyro
                            processed_features['orientation']['pitch'],   # pitch
                            processed_features['orientation']['roll']     # roll
                        ]
                        rollover_predictor.update_model(feature_vector)
                    
                    time.sleep(1)  # Update every second
                    
            except KeyboardInterrupt:
                print("\n正在关闭系统...")
                return
                
        else:
            print("无效选择，退出...")
            return
            
    except KeyboardInterrupt:
        print("\n正在关闭系统...")
        return

def main():
    """Main function to run the local demo."""
    print("=" * 60)
    print("Troll-vs-Troll 本地演示系统")
    print("面向拉杆载具的电子差速防侧翻安全系统")
    print("=" * 60)
    
    run_local_system()

if __name__ == "__main__":
    main()