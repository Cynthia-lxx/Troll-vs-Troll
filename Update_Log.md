# Troll-vs-Troll 项目更新日志

## 版本 1.1.0 (2025-12-28)
- 完成UNIHIKER M10基准测试程序开发
- 实现翻页UI系统展示板载传感器数据
- 测试加速度计、光传感器、显示组件、音频系统
- 测量计算性能（每秒循环速度）
- 创建完整的benchmark.py程序
- 优化性能：移除主循环中的延时以准确测量最大性能
- 添加requirements.txt依赖文件
- 添加机器学习模块用于侧翻预测
- 实现基于传感器数据的侧翻风险预测算法
- 创建ml目录及rollover_prediction.py模块
- 使用scikit-learn实现异常检测模型
- 创建传感器数据处理模块
- 实现传感器数据过滤和特征提取功能
- 添加差速控制系统模块
- 实现基于ML预测的实时控制算法
- 创建differential_controller.py模块
- 创建传感器数据生成器模块
- 实现符合实际场景的传感器数据模拟
- 添加开题报告纯文本版本
- 状态：待测试

## 版本 1.0.1 (2025-12-28)
- 完成项目初始化和基本结构搭建
- 创建项目目录结构 (src/sensors, src/control, src/utils, src/main, tests, config)
- 添加开发者指南 (Developer_Guidelines.md)
- 整理硬件文档 (UNIHIKER M10 Python API文档)
- 建立项目开发规范和流程
- 添加版本日志管理规范
- 配置基本的Python模块结构和placeholder文件
- 完成开题报告文档整理

## 版本 1.0.0 (2025-12-28)
- 项目初始创建
- 确定项目目标：Trolley-Anti-Troll电子差速防侧翻系统
- 选择UNIHIKER M10作为硬件平台
- 建立基本的README文档