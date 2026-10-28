# pyBalance

**English** | [中文](README_zh.md)

![banner](assets/banner.png)

## Introduction

MicroPython is a way to program all kinds of embedded hardware devices using Python. MicroPython is growing rapidly, and 01Studio has long been committed to embedded Python programming — that's why we created the pyBalance open-source project, aiming to make MicroPython even more popular. With MicroPython, you can easily implement a self-balancing robot's upright balancing, forward/backward movement, line following, ultrasonic obstacle avoidance, WiFi/BLE remote control, and more.

![banner](hardware/direction.png)

Example:
```python
import pyBalance

# Create a balancing robot object
b = pyBalance.BALANCE()

# Usage

# Start
b.start()

# Movement speed
b.speed(valnue = 4)

# Attitude control
d.control(pit = 0, yaw = 0)

# Stop
b.stop()

...
```

## Hardware Resources

pyBalance [click to buy>>](https://www.aliexpress.com/item/1005013485088460.html)

![img](hardware/overview.png)

| Specification | Details |
| :---: | --- |
| MCU | ESP32-S3-WROOM-1 (N16R8; Flash: 16 MBytes, RAM: 8 MBytes), supports WiFi/BLE |
| LED | x3 <br> ● Power indicator: red <br> ● Programmable LED1: blue <br> ● Programmable LED2: green |
| Buttons | x3 <br> ● Reset button <br> ● Programmable KEY1 <br> ● Programmable KEY2 |
| RGB LEDs | x4 <br> ● WS2812B / connected in series |
| 6-axis IMU | QMI8658A (3-axis accelerometer + 3-axis gyroscope) |
| Display | ● 1.54-inch color display <br> ● Resolution: 240x240 <br> ● Driver IC: ST7789 |
| GPIO | 2.54mm x 8P pin header |
| UART/I2C interface | PH-2.0mm-4P (adapter cable included) |
| Micro USB port | All-in-one for flashing / debugging |
| Motors | x2 <br> ● DC gear motors (with encoders) <br> ● Voltage: 6V <br> ● Speed: 620 r/min <br> ● Gear ratio: 1:9.2 |
| Wheels | ● Diameter: 70mm <br> ● Width: 27mm |
| Li-ion battery | 7.4V / 2 x 18650 cells in series (2200mAh each) / XH-2.54mm-3P connector |
| Frame | Acrylic frame + aluminum alloy motor brackets |

| Dimensions | Details |
| :---: | --- |
| Size | 200 x 70 x 115mm (L x W x H / whole unit) |
| Weight | 560g (battery included / whole unit) |

![img](hardware/size.png)

## Directory Structure

```
pyBalance/
├── examples/          # Example code
├── hardware/          # Hardware design resources (schematics, footprints, 3D models)
├── firmware/          # Firmware
├── app/               # Android app
├── CHANGELOG.md       # Changelog
├── LICENSE
├── README.md          # English documentation
└── README_zh.md       # Chinese documentation
```

## Development Resources

- [Wiki (Tutorials & Documentation)](https://wiki.01studio.cc/en/docs/pybalance/)
- [ESP32 Online Flashing](https://flash.01studio.cc)

## Changelog

Please refer to [CHANGELOG.md](CHANGELOG.md).

## Technical Support

If you run into any problems, you can get support through the following channel:

**Email**: Send an email to [support@01studio.cc](mailto:support@01studio.cc).
