# UNIHIKER M10 行空板 Python 模块详细API文档

## 版本日志
- v1.0.0 2025-12-28: 初始版本 - 成功

## 1. unihiker库概述

unihiker库是专门为行空板开发的Python库，将行空板需要而第三方Python库没有或使用不便的功能集成于此库中。主要包含两个核心类：

- **GUI类**：基于tkinter库封装，用于屏幕显示和控制
- **Audio类**：用于麦克风和USB喇叭的使用

## 2. GUI类详细API

### 2.1 导入和初始化
```python
from unihiker import GUI   #导入包
gui = GUI()  #实例化GUI类
```

### 2.2 坐标系统
- 屏幕分辨率：240 x 320
- 坐标原点：屏幕左上角
- x轴：向右为正方向
- y轴：向下为正方向

### 2.3 对齐位置（origin）
控件对象自身内部有9个对齐位置点，可采用以下方式标识：
- 东南西北（ESWN）：'top-left', 'top-center', 'top-right', 'center-left', 'center', 'center-right', 'bottom-left', 'bottom-center', 'bottom-right'
- 上下左右（top/bottom/left/right）

### 2.4 基础控件和图形方法

#### 2.4.1 draw_text - 绘制文本
```python
控件对象 = GUI对象.draw_text(x, y, text, w, h, origin, onclick, font_size, color)
```
- **x**: 横坐标
- **y**: 纵坐标
- **text**: 要显示的文本
- **w**: 宽度（可选）
- **h**: 高度（可选）
- **origin**: 对齐位置（可选，默认左上角）
- **onclick**: 点击时触发的回调函数（可选）
- **font_size**: 字体大小（可选）
- **color**: 颜色（可选）

#### 2.4.2 draw_image - 绘制图片
```python
控件对象 = GUI对象.draw_image(x, y, w, h, image, origin, onclick)
```
- **x**: 横坐标
- **y**: 纵坐标
- **w**: 图片的宽度（可选，按比例缩放）
- **h**: 图片的高度（可选，按比例缩放）
- **image**: 图片源（路径或image对象）
- **origin**: 对齐位置（可选，默认左上角）
- **onclick**: 点击时触发的回调函数（可选）

#### 2.4.3 draw_clock - 绘制时钟
```python
控件对象 = GUI对象.draw_clock(x, y, r, h, m, s, color, onclick)
```
- **x**: 横坐标
- **y**: 纵坐标
- **r**: 时钟半径
- **h**: 小时
- **m**: 分钟
- **s**: 秒
- **color**: 颜色（可选）
- **onclick**: 点击时触发的回调函数（可选）

### 2.5 按键处理方法

#### 2.5.1 on_a_click - A按键点击回调
```python
GUI对象.on_a_click(callback_function)
```
- **callback_function**: A按键被按下时的回调函数

#### 2.5.2 on_b_click - B按键点击回调
```python
GUI对象.on_b_click(callback_function)
```
- **callback_function**: B按键被按下时的回调函数

#### 2.5.3 on_key_click - 任意键点击回调
```python
GUI对象.on_key_click(key, callback_function)
```
- **key**: 键名（如'c', '<space>'等）
- **callback_function**: 按键被按下时的回调函数

### 2.6 控件更新方法

#### 2.6.1 config - 更新控件属性
```python
控件对象.config(属性=新值)
```
用于更新控件对象的属性，如文本、颜色等。

### 2.7 其他GUI类功能

#### 2.7.1 update - 更新GUI
```python
GUI对象.update()
```
注意：此函数仅在MAC系统下运行unihiker库时需要，用于在主线程中刷新界面，控制行空板时无需此函数。

## 3. Audio类详细API

### 3.1 导入和初始化
```python
from unihiker import Audio
audio = Audio()  #实例化Audio类
```

### 3.2 音频播放方法

#### 3.2.1 play - 播放音频
```python
audio.play(filename)
```
- **filename**: 音频文件名
- **功能**: 播放音频文件（同步，等待播放完成）

#### 3.2.2 start_play - 开始播放音频
```python
audio.start_play(filename)
```
- **filename**: 音频文件名
- **功能**: 开始播放音频文件（异步，不等待播放完成）

#### 3.2.3 pause_play - 暂停播放
```python
audio.pause_play()
```
- **功能**: 暂停当前播放的音频

#### 3.2.4 resume_play - 恢复播放
```python
audio.resume_play()
```
- **功能**: 恢复播放已暂停的音频

#### 3.2.5 stop_play - 停止播放
```python
audio.stop_play()
```
- **功能**: 停止当前播放的音频

#### 3.2.6 play_time_remain - 获取剩余播放时间
```python
remain_time = audio.play_time_remain()
```
- **返回值**: 剩余播放时间（秒）

## 4. 安装和更新

### 4.1 安装库
```bash
pip install unihiker
```

### 4.2 更新库
```bash
pip install -U unihiker
```

## 5. 常见问题

### 5.1 参数错误
- **问题**: TypeError: xxx() takes x positional argument but x were given
- **解决**: 检查函数的输入参数，需要带上参数名，例如：
  - 错误：`gui.add_button(0,10,20,20,"按钮")`
  - 正确：`gui.add_button(x=0,y=10,w=20,h=20,text="按钮")`

## 6. 其他支持的库

### 6.1 PinPong库
- 允许使用Python直接控制UNIHIKER的内置传感器和各种连接的传感器和执行器

### 6.2 预装Python库
- pandas - 数据处理库
- OpenCV - 计算机视觉库
- sklearn - 机器学习库
- 以及其他超过230万扩展库

### 6.3 AI和物联网相关库
- onnx, onnxruntime - 用于AI模型部署
- opencv-python - 计算机视觉处理
- uralytics - AI分析库