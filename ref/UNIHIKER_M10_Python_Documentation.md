# UNIHIKER M10 行空板 Python 模块详细文档

## 版本日志
- v1.0.0 2025-12-28: 初始版本 - 成功

## 1. unihiker库说明

为了便于行空板的使用，开发了一个Python库，名为unihiker，将行空板需要而第三方Python库没有或使用不便的功能集成于此库中。

- 为了方便屏幕显示和控制，在unihiker库中基于tkinter库封装了一个GUI类
- 为了方便麦克风和USB喇叭的使用，在unihiker库中封装了一个Audio类

## 2. 安装库

通过pip工具即可进行安装和更新

安装：
```
pip install unihiker
```

更新：
```
pip install -U unihiker
```

## 3. GUI类导入方法

```python
from unihiker import GUI   #导入包
gui=GUI()  #实例化GUI类
```

## 4. 通用知识和功能

[此部分在官方文档中存在但内容未显示]

## 5. 基础控件

[此部分在官方文档中存在但内容未显示]

## 6. 基础图形

[此部分在官方文档中存在但内容未显示]

## 7. 鼠标键盘侦测

[此部分在官方文档中存在但内容未显示]

## 8. 多线程

[此部分在官方文档中存在但内容未显示]

## 10. Audio类 录音及播放

[此部分在官方文档中存在但内容未显示]

## 11. 常见问题

| 问题 | 报错：TypeError: xxx() takes x positionaxl argument but x were given |
| --- | --- |
| 解决 | 检查函数的输入参数，需要带上参数名，例如gui.add_button(0,10,20,20,"按钮")错误，需要改为gui.add_button(x=0,y=10,w=20,h=20,text="按钮") |

## 附录：其他支持的库

### 预装的常用Python库
- pandas - 数据处理库
- OpenCV - 计算机视觉库
- sklearn - 机器学习库
- 以及其他超过230万扩展库

### 控制库
- PinPong库 - 允许使用Python直接控制UNIHIKER的内置传感器和各种连接的传感器和执行器

### AI和物联网相关库
- onnx, onnxruntime - 用于AI模型部署
- opencv-python - 计算机视觉处理
- uralytics - AI分析库

## 硬件接口支持

### 板载传感器
- 光线传感器
- 加速度传感器
- 麦克风
- 蜂鸣器

### 显示接口
- 2.8寸彩色触摸屏（240*320分辨率）

### 扩展接口
- 3Pin I/O口
- 4Pin I²C口
- 19路无冲突金手指接口
- USB Type-C/A接口
- microSD卡槽