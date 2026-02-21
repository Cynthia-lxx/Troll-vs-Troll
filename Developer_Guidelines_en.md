# UNIHIKER M10 Troll-vs-Troll Project Developer Guidelines

## 📋 Document Overview

This document provides complete development guidelines for the UNIHIKER M10 Troll-vs-Troll project. **Development must strictly follow official documentation**, and all API calls and functionality implementations should be based on official documentation.

> ⚠️ **Important Declaration**: This project strictly follows UNIHIKER M10 official documentation standards. Documentation is the sole authoritative source. All development work must be based on official documentation. Self-speculation or deviation from official standards is prohibited.

## 📚 Core Technical Specifications

### Screen and Coordinate System Standards
- **Resolution**: Strictly use 240×320 pixels
- **Coordinate System**: Origin at top-left corner (0,0), right as positive x-direction, down as positive y-direction
- **Alignment Positions**: Support 9 alignment methods (north/south/east/west/top/bottom/left/right/center)
- **Color Representation**: Support RGB values (color=(255,0,0)), hex values (color="#ff00ff"), fixed colors (color="red")

### unihiker Library Usage Standards
- **Import Method**: `from unihiker import GUI`
- **Initialization**: `gui = GUI()`
- **Parameter Calling**: **Must use named parameters**, position parameters are prohibited
  - ✅ Correct: `gui.add_button(x=0, y=10, w=20, h=20, text="Button")`
  - ❌ Wrong: `gui.add_button(0, 10, 20, 20, "Button")`
- **Widget Management**:
  - Update widget: `widget_object.config(parameter_name=value)`
  - Delete widget: `GUI_object.remove(widget_object)` (recommended) or `widget_object.remove()`
  - Clear all widgets: `GUI_object.clear()`

### pinpong Library Usage Standards
- **Import Method**: `from pinpong.board import Board, Pin`
- **Initialization**: `Board().begin()` (must be called before use)
- **Architecture Features**: Control onboard components and GPIO through coprocessor
- **Package Structure**: Support board, extension, libs three package classifications

### Onboard Resource Usage Standards
1. **L Light Control** (P25 pin)
   - Control method: `Pin(Pin.P25, Pin.OUT).write_digital(1/0)`
   - High level (1) lights up, low level (0) turns off

2. **Button A/B Usage**
   - Query mode: `button_a.is_pressed()` returns True/False
   - Callback mode: `button_a.irq(trigger=Pin.IRQ_RISING, handler=callback_function)`
   - **Note**: A/B buttons can also be called directly using keyboard events

3. **Sensor Usage**
   - Light sensor: `light.read()` returns 0-4095 values
   - Accelerometer: `accelerometer.get_x()`, `get_y()`, `get_z()`, `get_strength()`
   - Gyroscope: `gyroscope.get_x()`, `get_y()`, `get_z()`
   - Environmental sound: Use unihiker library `Audio().sound_level()`

4. **Buzzer Control**
   - Play music: `buzzer.play(buzzer.DADADADUM, buzzer.Once)`
   - Play note: `buzzer.pitch(494, 4)`

### GPIO Pin Standards
- **Digital IO**: All pins support 3.3V digital input/output
- **Analog Input (ADC)**: P0, P1, P2, P3, P4, P10, P21, P22 (12-bit precision)
- **PWM Output**: P0, P2, P3, P10, P16, P21, P22, P23 (10-bit precision)
  - **Important**: P8/P2 share one PWM channel, P9/P10 share one PWM channel
  - Pay attention to pin conflicts when using, only one can be used from the same group

### Advanced Interface Features
1. **UART Serial Port**: 1 hardware serial port (P0-RX, P3-TX)
2. **SPI Interface**: 2 channels (SPI0: P1,P10,P2; SPI1: P13,P14,P15)
3. **I2C Interface**: 2 PH2.0 interfaces + finger gold P19/P20
   - Address scanning command: `i2cdetect -y 4`

## ⚠️ Development Prohibitions

⚠️ **Strictly Prohibited Behaviors**:
1. Speculating API usage without consulting official documentation
2. Using positional parameters to call unihiker library functions
3. Ignoring pinpong library initialization requirements
4. Using multiple pins from the same PWM shared pin group simultaneously
5. Connecting high-current devices directly to onboard interfaces
6. Using multiple devices with the same address on I2C bus
7. Considering functionality complete without testing

## Version Log
- v1.0.0 2025-12-28: Initial version - Success
- v1.0.1 2025-12-18 to 2026-01: Differential processing kernel development - Test failed (unfamiliar with M10 API)
- v1.1.0 2025-12-28: Completed benchmark, machine learning, differential control, data generation modules - Pending test
- v1.2.0 2026-02-17: Completed local development environment and web interface - Success
- v1.3.0 2026-02-17: Added machine learning enhancement features - Testing
- v1.3.1 2026-02-17: Major system architecture upgrade - Pending test

## 1. Project Overview

Troll-vs-Troll (Pull Rod Vehicle Anti-Rollover System) is an electronic differential anti-rollover safety system based on UNIHIKER M10 board, designed to enhance the stability of pull rod vehicles (such as luggage) during turning by real-time wheel speed monitoring, preventing rollover accidents.

## 2. Development Environment Configuration

### 2.1 Hardware Requirements
- UNIHIKER M10 Board
- Related sensors (such as wheel speed sensors, accelerometers, etc.)
- Motor control modules (if needed)

### 2.2 Software Requirements
- Python 3.7 or higher (recommended upgrade to Python 3.12)
- unihiker library: `pip install unihiker` (pre-installed on UNIHIKER M10)
- pinpong library: `pip install pinpong` (pre-installed on UNIHIKER M10)
- Other dependencies installed according to specific functional requirements

## 3. Development Standards

### 3.1 Code Style
- Follow PEP 8 Python code style guidelines
- Use meaningful variable names and function names
- Maintain consistent indentation (4 spaces)
- Functions and classes must include docstrings

### 3.2 Module Import Standards
- **Must read and review API documentation**: Before introducing any third-party modules during development, must first thoroughly read their API documentation to understand functionality, parameters, and return values
- Briefly explain the purpose and key usage of imported modules in code comments
- Avoid importing unnecessary modules to keep code clean

### 3.3 TODO Management Procedures
- **Must strictly follow the procedure of writing TODO first, then completing programs according to TODO**:
  - Before starting new feature development, first add TODO comments in code to clarify functional requirements
  - TODO format: `# TODO: [function description] - [priority] - [responsible person]`
  - Priority: HIGH, MEDIUM, LOW
- **Only eliminate TODO when a function is completely tested and passed**:
  - Function must pass unit tests and integration tests
  - Requires code review
  - Confirm function works as expected without side effects

## 4. Code Structure

### 4.1 Project Directory Structure
```
Troll-vs-Troll/
├── README.md
├── Developer_Guidelines.md
├── requirements.txt
├── Update_Log.md
├── convert_docx_to_txt.py
├── ref/
│   ├── 吴佳泽_开题报告_1.0.docx
│   ├── 吴佳泽_开题报告_1.0.txt
│   ├── UNIHIKER_M10_Python_Documentation.md
│   └── UNIHIKER_M10_Detailed_API_Documentation.md
├── src/
│   ├── main/
│   │   ├── __init__.py
│   │   └── benchmark.py
│   ├── sensors/
│   │   ├── __init__.py
│   │   └── data_processor.py
│   ├── control/
│   │   ├── __init__.py
│   │   └── differential_controller.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── data_generator.py
│   └── ml/
│       ├── __init__.py
│       └── rollover_prediction.py
└── tests/
    └── __init__.py
```

### 4.2 Module Organization
- Organize code by functional modules
- Sensor-related code placed in [sensors](file:///E:/Comp/特需/Troll-vs-Troll-main/Troll-vs-Troll-main/src/sensors) directory
- Control algorithm code placed in [control](file:///E:/Comp/特需/Troll-vs-Troll-main/Troll-vs-Troll-main/src/control) directory
- Utility functions placed in [utils](file:///E:/Comp/特需/Troll-vs-Troll-main/Troll-vs-Troll-main/src/utils) directory

## 5. Testing Standards

### 5.1 Unit Testing
- Write unit tests for each functional module
- Use Python standard library unittest framework
- Test coverage should reach 80% or above

### 5.2 Integration Testing
- Test module interfaces and interactions
- Perform end-to-end testing on actual hardware

### 5.3 Hardware Testing
- Test sensor data collection in real environments
- Verify real-time response performance of control algorithms

## 6. Version Control

### 6.1 Git Branch Strategy
- `main` branch: Stable versions
- `develop` branch: Development versions
- `feature/*` branches: Feature development
- `bugfix/*` branches: Bug fixes

### 6.2 Commit Message Standards
- Use clear, meaningful commit messages
- Format: `<type>: <subject>`
- Types include: feat (new feature), fix (bug fix), docs (documentation), style (formatting), refactor (refactoring), test (testing), chore (miscellaneous)

## 7. Documentation Requirements

### 7.1 Code Comments
- Functions and classes must have docstrings
- Add comments for complex algorithms
- Comment important business logic

### 7.2 Project Documentation
- Maintain README.md file
- Update developer guidelines
- Record API changes

### 7.3 Version Log Requirements
- Each program and file header must have its own version log
- Version log should declare what changes were made to the file and whether successful
- Each submodule file's version log only needs to maintain updates for that program itself, no need to include other modules' update information
- Version log format:
  ```
  ## Version Log
  - v1.0.0 [date]: Initial version - [Success/Failure]
  - v1.1.0 [date]: [specific change description] - [Success/Failure]
  ```

### 7.4 README Update Requirements
- Must update main README file whenever writing new features
- Declare new feature's purpose and usage in README
- Ensure README always reflects project's latest functional status

## 8. Security and Performance Considerations

### 8.1 Security
- Validate validity of sensor input data
- Implement exception handling mechanisms
- Prevent dangerous behaviors in abnormal situations

### 8.2 Performance
- Optimize algorithm execution efficiency
- Reasonably manage memory usage
- Implement appropriate error recovery mechanisms

## 9. Development Process

1. **Requirements Analysis**: Clarify functional requirements and performance indicators
2. **Design Phase**: Design system architecture and module interfaces
3. **Implementation Phase**:
   - Add TODO comments
   - Implement features
   - Write tests
4. **Testing Phase**: Unit testing, integration testing, hardware testing
5. **Review Phase**: Code review and functional verification
6. **Completion Phase**: Remove TODO markers

## 10. Reference Material Management

### 10.1 Reference File Storage
- All useful and necessary reference materials will be stored in [/ref](file:///E:/Comp/特需/Troll-vs-Troll-main/Troll-vs-Troll-main/ref) directory
- Including hardware documentation, API documentation, design documents, etc.
- New reference materials should be archived to this directory promptly
- **Special Note**: `/ref/UNIHIKER-M10-Documentation/` directory contains authoritative official documentation for the board, serving as the sole reference standard for all M10-related development

### 10.2 Module Compatibility
- Check compatibility with UNIHIKER M10 before introducing new modules
- Verify module operation under target Python version

### 10.3 Hardware Interfaces
- Strictly follow UNIHIKER M10 interface specifications when connecting sensors
- Pay attention to voltage level matching and electrical safety

### 10.4 UNIHIKER M10 Official Documentation Usage Standards
- **Must strictly refer to official documentation in /ref directory for development**
- All UNIHIKER M10-related code implementation must be based on API specifications in official documentation
- Must thoroughly read [UNIHIKER M10 Official Documentation - unihiker Library](./ref/UNIHIKER-M10-Documentation/行空板官方文档-unihiker库.html) and related chapters before using unihiker library
- Must thoroughly read [UNIHIKER M10 Official Documentation - pinpong Library](./ref/UNIHIKER-M10-Documentation/行空板官方文档 - pinpong库.html) before using pinpong library
- Strictly prohibited from speculating API usage without consulting official documentation
- Prioritize consulting FAQ and common issues sections in official documentation when encountering problems

---

This guide aims to ensure high-quality development and long-term maintainability of the project. All developers should be familiar with and follow these standards.