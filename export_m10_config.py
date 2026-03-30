#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M10 配置导出工具
版本：1.5.0 - 2026/3/30

将训练好的模型参数和优化后的控制参数导出为轻量级配置文件，
供 M10 离线数据采集使用。
"""

import json
import os
from datetime import datetime

def export_m10_config(
    model_params=None,
    control_params=None,
    risk_thresholds=None,
    sampling_config=None,
    output_file='m10_config.json'
):
    """
    导出 M10 配置文件
    
    Args:
        model_params (dict): 机器学习模型参数
        control_params (dict): 控制参数
        risk_thresholds (dict): 风险阈值
        sampling_config (dict): 采样配置
        output_file (str): 输出文件名
    """
    # 默认参数
    if model_params is None:
        model_params = {
            'feature_weights': [1.0] * 17,
            'threshold': 0.3,
            'version': '1.0'
        }
    
    if control_params is None:
        control_params = {
            'gravity_strength': 0.08,
            'damping_factor': 0.1,
            'max_wheel_diff': 0.5,
            'control_threshold': 0.3
        }
    
    if risk_thresholds is None:
        risk_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8
        }
    
    if sampling_config is None:
        sampling_config = {
            'sampling_rate': 100,  # Hz
            'buffer_size': 1000,
            'heartbeat_interval': 5.0  # seconds
        }
    
    # 构建配置字典
    config = {
        'version': '1.5.0',
        'export_timestamp': datetime.now().isoformat(),
        'description': 'M10 离线数据采集配置',
        'model_params': model_params,
        'control_params': control_params,
        'risk_thresholds': risk_thresholds,
        'sampling_config': sampling_config,
        'device_info': {
            'target': 'UNIHIKER_M10',
            'mode': 'offline_data_collection',
            'firmware': 'unihiker_sensor_collector.py'
        }
    }
    
    # 保存到文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 配置文件导出成功：{output_file}")
        print(f"\n配置详情:")
        print(f"  版本号：{config['version']}")
        print(f"  导出时间：{config['export_timestamp']}")
        print(f"  采样率：{sampling_config['sampling_rate']} Hz")
        print(f"  缓存大小：{sampling_config['buffer_size']} 条")
        print(f"  心跳间隔：{sampling_config['heartbeat_interval']} 秒")
        print(f"\n风险阈值:")
        print(f"  低风险：{risk_thresholds['low']}")
        print(f"  中风险：{risk_thresholds['medium']}")
        print(f"  高风险：{risk_thresholds['high']}")
        print(f"\n控制参数:")
        for key, value in control_params.items():
            print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置导出失败：{e}")
        return False


def load_from_system_config(system_config_file='system_config.json'):
    """
    从现有系统配置加载参数
    
    Args:
        system_config_file (str): 系统配置文件路径
    """
    try:
        with open(system_config_file, 'r', encoding='utf-8') as f:
            sys_config = json.load(f)
        
        # 提取相关参数
        control_params = sys_config.get('control_parameters', {})
        ml_params = sys_config.get('ml_parameters', {})
        sensor_params = sys_config.get('sensor_parameters', {})
        
        # 构建 M10 配置
        m10_config = {
            'control_params': {
                'gravity_strength': control_params.get('gravity_strength', 0.08),
                'damping_factor': control_params.get('damping_factor', 0.1),
                'max_wheel_diff': 0.5,
                'control_threshold': control_params.get('rollover_threshold', 0.3)
            },
            'risk_thresholds': {
                'low': 0.3,
                'medium': 0.6,
                'high': 0.8
            },
            'sampling_config': {
                'sampling_rate': sensor_params.get('sampling_rate', 100),
                'buffer_size': 1000,
                'heartbeat_interval': 5.0
            },
            'model_params': {
                'feature_names': ml_params.get('feature_names', []),
                'threshold': 0.3,
                'version': '1.0'
            }
        }
        
        return m10_config
        
    except Exception as e:
        print(f"⚠️ 无法加载系统配置：{e}，使用默认参数")
        return None


def main():
    """主函数"""
    print("=" * 60)
    print("M10 配置导出工具")
    print("版本：1.5.0")
    print("=" * 60)
    print()
    
    # 尝试从系统配置加载
    print("正在检查系统配置...")
    if os.path.exists('system_config.json'):
        custom_config = load_from_system_config()
        if custom_config:
            print("✅ 找到系统配置，使用自定义参数")
            export_m10_config(
                model_params=custom_config['model_params'],
                control_params=custom_config['control_params'],
                risk_thresholds=custom_config['risk_thresholds'],
                sampling_config=custom_config['sampling_config']
            )
            return
    
    print("⚠️ 未找到系统配置，使用默认参数")
    export_m10_config()


if __name__ == "__main__":
    main()
