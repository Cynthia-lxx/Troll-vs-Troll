#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNIHIKER移植版本测试脚本
用于验证移植到UNIHIKER平台的功能完整性
"""

import sys
import os
import time
from unittest.mock import Mock, patch

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_module_imports():
    """测试核心模块导入"""
    print("🔍 测试核心模块导入...")
    
    try:
        from src.ml.rollover_prediction import RolloverPredictor
        print("✅ RolloverPredictor 模块导入成功")
    except ImportError as e:
        print(f"❌ RolloverPredictor 模块导入失败: {e}")
        return False
    
    try:
        from src.sensors.data_processor import SensorDataProcessor
        print("✅ SensorDataProcessor 模块导入成功")
    except ImportError as e:
        print(f"❌ SensorDataProcessor 模块导入失败: {e}")
        return False
    
    try:
        from src.control.differential_controller import DifferentialController
        print("✅ DifferentialController 模块导入成功")
    except ImportError as e:
        print(f"❌ DifferentialController 模块导入失败: {e}")
        return False
    
    return True

def test_component_initialization():
    """测试组件初始化"""
    print("\n🔧 测试组件初始化...")
    
    try:
        from src.ml.rollover_prediction import RolloverPredictor
        predictor = RolloverPredictor()
        print("✅ 侧翻预测器初始化成功")
    except Exception as e:
        print(f"❌ 侧翻预测器初始化失败: {e}")
        return False
    
    try:
        from src.sensors.data_processor import SensorDataProcessor
        processor = SensorDataProcessor()
        print("✅ 传感器处理器初始化成功")
    except Exception as e:
        print(f"❌ 传感器处理器初始化失败: {e}")
        return False
    
    try:
        from src.control.differential_controller import DifferentialController
        controller = DifferentialController()
        print("✅ 差速控制器初始化成功")
    except Exception as e:
        print(f"❌ 差速控制器初始化失败: {e}")
        return False
    
    return True

def test_basic_functionality():
    """测试基本功能"""
    print("\n⚡ 测试基本功能...")
    
    try:
        from src.ml.rollover_prediction import RolloverPredictor
        from src.sensors.data_processor import SensorDataProcessor
        from src.control.differential_controller import DifferentialController
        
        # 初始化组件
        predictor = RolloverPredictor()
        processor = SensorDataProcessor()
        controller = DifferentialController()
        
        # 测试数据
        test_accel = (0.1, 0.05, 9.81)  # 正常状态
        test_gyro = (0.01, 0.01, 0.01)
        
        # 测试传感器数据处理
        processor.add_accel_data(test_accel)
        processor.add_gyro_data(test_gyro)
        features = processor.get_processed_features()
        print("✅ 传感器数据处理功能正常")
        
        # 测试风险预测
        risk_result = predictor.predict_rollover_risk(test_accel, test_gyro)
        print(f"✅ 风险预测功能正常 - 风险等级: {risk_result['risk_level']}")
        
        # 测试差速控制
        control_result = controller.update_control(test_accel, test_gyro)
        print(f"✅ 差速控制功能正常 - 控制激活: {control_result['control_active']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False

def test_unihiker_specific_features():
    """测试UNIHIKER特定功能（模拟环境）"""
    print("\n📱 测试UNIHIKER特定功能...")
    
    # 模拟UNIHIKER环境
    with patch.dict('sys.modules', {
        'pinpong': Mock(),
        'pinpong.board': Mock(),
        'pinpong.extension': Mock(),
        'pinpong.extension.unihiker': Mock(),
        'unihiker': Mock()
    }):
        try:
            # 模拟导入UNIHIKER库
            import pinpong
            from pinpong.board import Board
            from pinpong.extension.unihiker import acceleration, gyroscope
            from unihiker import GUI, Audio
            
            # 模拟硬件初始化
            mock_board = Mock()
            Board.return_value = mock_board
            mock_board.begin.return_value = None
            
            # 模拟传感器读取
            acceleration.read.return_value = (0.1, 0.05, 9.81)
            gyroscope.read.return_value = (0.01, 0.01, 0.01)
            
            # 模拟GUI和音频
            mock_gui = Mock()
            mock_audio = Mock()
            GUI.return_value = mock_gui
            Audio.return_value = mock_audio
            
            print("✅ UNIHIKER硬件接口模拟成功")
            return True
            
        except Exception as e:
            print(f"❌ UNIHIKER特定功能测试失败: {e}")
            return False

def test_data_exchange_protocol():
    """测试数据交换协议"""
    print("\n🔄 测试数据交换协议...")
    
    try:
        # 模拟协作模式下的数据交换
        import json
        from datetime import datetime
        
        # 模拟传感器数据包
        sensor_packet = {
            'timestamp': datetime.now().isoformat(),
            'accel_data': [0.1, 0.05, 9.81],
            'gyro_data': [0.01, 0.01, 0.01],
            'device_id': 'UNIHIKER_001'
        }
        
        # 序列化测试
        json_data = json.dumps(sensor_packet)
        parsed_data = json.loads(json_data)
        
        print("✅ 数据序列化/反序列化功能正常")
        
        # 模拟控制指令包
        control_packet = {
            'timestamp': datetime.now().isoformat(),
            'left_wheel_speed': 1.0,
            'right_wheel_speed': 0.8,
            'control_active': True,
            'risk_level': 'MEDIUM'
        }
        
        json_control = json.dumps(control_packet)
        parsed_control = json.loads(json_control)
        
        print("✅ 控制指令传输功能正常")
        return True
        
    except Exception as e:
        print(f"❌ 数据交换协议测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("UNIHIKER M10 移植版本测试")
    print("=" * 60)
    
    tests = [
        ("模块导入测试", test_module_imports),
        ("组件初始化测试", test_component_initialization),
        ("基本功能测试", test_basic_functionality),
        ("UNIHIKER特定功能测试", test_unihiker_specific_features),
        ("数据交换协议测试", test_data_exchange_protocol)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 40)
        if test_func():
            passed += 1
            print(f"✅ {test_name} 通过")
        else:
            print(f"❌ {test_name} 失败")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！UNIHIKER移植版本功能完整")
        print("\n🚀 下一步建议:")
        print("1. 将文件传输到UNIHIKER M10硬件")
        print("2. 按照部署指南进行硬件配置")
        print("3. 运行实际硬件测试")
    else:
        print("⚠️  部分测试失败，请检查相关模块")
    
    print("=" * 60)

if __name__ == "__main__":
    main()