#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNIHIKER M10 主程序
专门为UNIHIKER M10硬件平台设计的电子差速防侧翻系统
遵循官方文档规范，仅运行单个文件
"""

import time
import math
from collections import deque
import numpy as np
from pinpong.board import Board
from pinpong.extension.unihiker import *
from unihiker import GUI, Audio

# 导入项目模块
from src.ml.rollover_prediction import RolloverPredictor
from src.sensors.data_processor import SensorDataProcessor
from src.control.differential_controller import DifferentialController

class UNIHIKERSystem:
    """UNIHIKER M10系统主类"""
    
    def __init__(self):
        """初始化UNIHIKER系统"""
        print("初始化UNIHIKER电子差速防侧翻系统...")
        
        # 初始化硬件
        self._initialize_hardware()
        
        # 初始化GUI和音频
        self.gui = GUI()
        self.audio = Audio()
        
        # 初始化核心算法组件
        self._initialize_components()
        
        # 系统状态
        self.system_running = True
        self.current_mode = "NORMAL"  # NORMAL, WARNING, EMERGENCY
        self.warning_threshold = 0.4
        self.emergency_threshold = 0.7
        
        # 数据缓冲区
        self.accel_buffer = deque(maxlen=50)
        self.gyro_buffer = deque(maxlen=50)
        
        # 控制变量
        self.left_wheel_speed = 1.0
        self.right_wheel_speed = 1.0
        self.control_active = False
        
        print("UNIHIKER系统初始化完成")
    
    def _initialize_hardware(self):
        """初始化硬件组件"""
        try:
            # 初始化Board（UNIHIKER M10必需）
            Board().begin()
            print("硬件初始化成功")
        except Exception as e:
            print(f"硬件初始化失败: {e}")
            raise
    
    def _initialize_components(self):
        """初始化软件组件"""
        # 物理参数设置
        bag_params = {
            'bag_length': 0.5,      # 米
            'bag_width': 0.3,       # 米
            'bag_height': 0.7,      # 米
            'center_of_gravity_height': 0.4,  # 米
            'wheel_radius': 0.1,    # 米
            'wheel_mass': 0.5,      # 千克
            'bag_total_mass': 5.0   # 千克
        }
        
        # 初始化核心组件
        self.rollover_predictor = RolloverPredictor(**bag_params)
        self.sensor_processor = SensorDataProcessor(window_size=20)
        self.differential_controller = DifferentialController(**bag_params)
        
        print("软件组件初始化完成")
    
    def read_sensors(self):
        """读取传感器数据"""
        try:
            # 使用pinpong库读取加速度计数据（命名参数调用）
            accel_data = acceleration.read()
            # 使用pinpong库读取陀螺仪数据（如果可用）
            try:
                gyro_data = gyroscope.read()
            except:
                # 如果陀螺仪不可用，使用零值
                gyro_data = (0.0, 0.0, 0.0)
            
            return accel_data, gyro_data
            
        except Exception as e:
            print(f"传感器读取错误: {e}")
            # 返回默认值
            return (0.0, 0.0, 9.81), (0.0, 0.0, 0.0)
    
    def process_data(self, accel_data, gyro_data):
        """处理传感器数据"""
        # 添加到处理器
        self.sensor_processor.add_accel_data(accel_data)
        self.sensor_processor.add_gyro_data(gyro_data)
        
        # 获取处理后的特征
        features = self.sensor_processor.get_processed_features()
        
        # 预测侧翻风险
        risk_assessment = self.rollover_predictor.predict_rollover_risk(accel_data, gyro_data)
        
        # 更新差速控制
        control_result = self.differential_controller.update_control(accel_data, gyro_data)
        
        return features, risk_assessment, control_result
    
    def update_display(self, features, risk_assessment, control_result):
        """更新显示界面"""
        # 清屏（使用文本元素填充背景）
        self._clear_screen()
        
        # 显示标题
        self.gui.draw_text(x=120, y=20, text="Troll-vs-Troll", origin='center', font_size=16, color=(0, 255, 0))
        self.gui.draw_text(x=120, y=40, text="防侧翻安全系统", origin='center', font_size=12, color=(200, 200, 200))
        
        # 显示系统状态
        status_color = self._get_status_color(risk_assessment['risk_score'])
        self.gui.draw_text(x=120, y=60, text=f"状态: {self.current_mode}", origin='center', font_size=14, color=status_color)
        
        # 显示风险等级
        risk_text = f"风险: {risk_assessment['risk_level']} ({risk_assessment['risk_score']*100:.1f}%)"
        self.gui.draw_text(x=120, y=80, text=risk_text, origin='center', font_size=12, color=(255, 255, 255))
        
        # 显示传感器数据
        if features:
            accel = features['acceleration']
            orientation = features['orientation']
            
            self.gui.draw_text(x=120, y=100, text=f"加速度: X={accel['x']:.2f}", origin='center', font_size=10, color=(200, 200, 200))
            self.gui.draw_text(x=120, y=115, text=f"Y={accel['y']:.2f} Z={accel['z']:.2f}", origin='center', font_size=10, color=(200, 200, 200))
            self.gui.draw_text(x=120, y=130, text=f"倾角: 俯仰={orientation['pitch']:.1f}°", origin='center', font_size=10, color=(200, 200, 200))
            self.gui.draw_text(x=120, y=145, text=f"横滚={orientation['roll']:.1f}°", origin='center', font_size=10, color=(200, 200, 200))
        
        # 显示控制状态
        control_text = "控制激活" if control_result['control_active'] else "正常行驶"
        control_color = (0, 255, 0) if not control_result['control_active'] else (255, 165, 0)
        self.gui.draw_text(x=120, y=165, text=control_text, origin='center', font_size=12, color=control_color)
        
        # 显示轮速信息
        self.gui.draw_text(x=120, y=185, text=f"左轮: {control_result['left_wheel_speed']:.2f}", origin='center', font_size=10, color=(200, 200, 200))
        self.gui.draw_text(x=120, y=200, text=f"右轮: {control_result['right_wheel_speed']:.2f}", origin='center', font_size=10, color=(200, 200, 200))
        
        # 显示物理参数
        self.gui.draw_text(x=120, y=220, text=f"载具: {self.rollover_predictor.bag_width*100:.0f}cm宽", origin='center', font_size=10, color=(150, 150, 150))
        self.gui.draw_text(x=120, y=235, text=f"重心高: {self.rollover_predictor.center_of_gravity_height*100:.0f}cm", origin='center', font_size=10, color=(150, 150, 150))
        
        # 显示时间戳
        current_time = time.strftime("%H:%M:%S")
        self.gui.draw_text(x=120, y=260, text=current_time, origin='center', font_size=10, color=(100, 100, 100))
        
        # 显示警告信息（如有）
        if risk_assessment['risk_score'] > self.warning_threshold:
            warning_msg = "⚠️ 注意保持平衡!" if risk_assessment['risk_score'] < self.emergency_threshold else "🚨 立即减速!"
            warning_color = (255, 165, 0) if risk_assessment['risk_score'] < self.emergency_threshold else (255, 0, 0)
            self.gui.draw_text(x=120, y=280, text=warning_msg, origin='center', font_size=14, color=warning_color)
    
    def _clear_screen(self):
        """清屏函数"""
        # 使用黑色文本元素覆盖整个屏幕
        for y in range(0, 320, 15):
            for x in range(0, 240, 15):
                self.gui.draw_text(x=x+7, y=y+7, text=" ", origin='center', font_size=20, color=(0, 0, 0))
    
    def _get_status_color(self, risk_score):
        """根据风险分数获取状态颜色"""
        if risk_score < self.warning_threshold:
            return (0, 255, 0)  # 绿色 - 正常
        elif risk_score < self.emergency_threshold:
            return (255, 165, 0)  # 橙色 - 警告
        else:
            return (255, 0, 0)  # 红色 - 紧急
    
    def update_system_state(self, risk_score):
        """更新系统状态"""
        if risk_score < self.warning_threshold:
            self.current_mode = "NORMAL"
        elif risk_score < self.emergency_threshold:
            self.current_mode = "WARNING"
        else:
            self.current_mode = "EMERGENCY"
    
    def play_alert_sound(self, risk_level):
        """播放警报声音"""
        try:
            if risk_level == "HIGH":
                # 播放紧急警报音
                self.audio.play_tone(800, 0.5)  # 800Hz持续0.5秒
                time.sleep(0.1)
                self.audio.play_tone(600, 0.5)  # 600Hz持续0.5秒
            elif risk_level == "MEDIUM":
                # 播放警告音
                self.audio.play_tone(1000, 0.3)  # 1000Hz持续0.3秒
        except Exception as e:
            print(f"音频播放错误: {e}")
    
    def run(self):
        """主运行循环"""
        print("UNIHIKER系统开始运行...")
        print("按Ctrl+C退出程序")
        
        last_alert_time = 0
        alert_interval = 2.0  # 警报间隔2秒
        
        try:
            while self.system_running:
                # 读取传感器数据
                accel_data, gyro_data = self.read_sensors()
                
                # 处理数据
                features, risk_assessment, control_result = self.process_data(accel_data, gyro_data)
                
                # 更新系统状态
                self.update_system_state(risk_assessment['risk_score'])
                
                # 更新显示
                self.update_display(features, risk_assessment, control_result)
                
                # 播放警报音（如果需要）
                current_time = time.time()
                if (risk_assessment['risk_level'] in ['HIGH', 'MEDIUM'] and 
                    current_time - last_alert_time > alert_interval):
                    self.play_alert_sound(risk_assessment['risk_level'])
                    last_alert_time = current_time
                
                # 控制更新频率（约10Hz）
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n收到退出信号，正在关闭系统...")
            self.system_running = False
        except Exception as e:
            print(f"系统运行错误: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        print("正在清理系统资源...")
        try:
            # 重置显示
            self._clear_screen()
            self.gui.draw_text(x=120, y=160, text="系统已关闭", origin='center', font_size=16, color=(255, 0, 0))
            time.sleep(2)
            self._clear_screen()
        except Exception as e:
            print(f"清理过程中出现错误: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("UNIHIKER M10 电子差速防侧翻系统")
    print("Troll-vs-Troll Project")
    print("=" * 50)
    
    try:
        # 创建并运行系统
        system = UNIHIKERSystem()
        system.run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        print("请检查硬件连接和依赖库安装")

if __name__ == "__main__":
    main()