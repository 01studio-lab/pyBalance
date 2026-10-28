'''
实验名称：pyBalance平衡小车蓝牙遥控（pyBalance代码）
日期：2026.8
作者：01Studio
说明：pyController做蓝牙主机，pyBalance做从机，手柄搜索到'pyBal'后发起连接，然后控制。
'''
from neopixel import NeoPixel
from machine import Pin
from tftlcd import LCD15
import bluetooth,ble_simple_peripheral,time,_thread
import pyBalance

b = pyBalance.BALANCE() #构建平衡小车对象

speed_value = 4 #速度值,范围[1,5] ,5最快
b.speed(speed_value) #设置小车速度

########################
# 构建1.5寸LCD对象并初始化
########################
d = LCD15(portrait=2) #默认方向竖屏

#定义红、绿、蓝三种颜色
RED=(255,0,0)
GREEN=(0,255,0)
BLUE=(0,0,255)
WHITE=(255,255,255)
BLACK=(0,0,0)

#定义RGB灯珠
pin = Pin(45, Pin.OUT)
NUM_LEDS = 4
np = NeoPixel(pin, NUM_LEDS)

#普通车灯模式，车头灯白色，车尾灯红色。
def rgb_normal(): 

    np[0]=WHITE 
    np[1]=WHITE
    np[2]=RED 
    np[3]=RED
    np.write()

rgb_normal()

# ---------------- 全局控制 ----------------

running = True                   # 线程运行标志

# ---------------- 工具函数 ----------------

def hsv_to_rgb(h, s=1.0, v=1.0):
    """HSV转RGB，h范围0~1，返回0~255的(r,g,b)元组"""
    i = int(h * 6.0)
    f = h * 6.0 - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if   i == 0: r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    else:        r, g, b = v, p, q
    return (int(r * 255), int(g * 255), int(b * 255))

# ---------------- 彩虹线程函数 ----------------

def rainbow_thread():
    speed = 0.01
    offset = 0.0
    while running:                          # 检查标志位
        for i in range(NUM_LEDS):
            hue = ((i / NUM_LEDS) + offset) % 1.0
            np[i] = hsv_to_rgb(hue, 1.0, 1.0)
        np.write()
        offset = (offset + 1.0 / 256) % 1.0
        time.sleep(speed)
    # 线程退出前熄灭灯珠
    np.fill((0, 0, 0))
    np.write()

# ---------------- 线程启停控制函数 ----------------

def start_rainbow():
    """启动彩虹线程"""
    global running
    running = True
    _thread.start_new_thread(rainbow_thread, ())
    print("彩虹线程已启动")

def stop_rainbow():
    """终止彩虹线程（等其自行退出）"""
    global running
    running = False                        # 置标志位
    time.sleep(0.1)                        # 等待线程检测到并退出
    print("彩虹线程已停止")

fl_node = 0
bl_node = 0
no_key = 0
rgb_node = 0

#接收到蓝牙数据处理函数
def on_rx(text):
    
    global fl_node,bl_node,speed_value,no_key,rgb_node
    
    control_data = [None]*2
    
    #接收的蓝牙数据
    print("RX:", text)
    
    #对收到的手柄8字节数据进行判断
    for i in range(len(text)):
        print(i,text[i])
        
    #将摇杆值转化为飞控控制值。      
    for i in range(2):
        if  100 < text[i+2] < 155 :
            control_data[i] = 0
            
        elif text[i+2] <= 100 :      
            control_data[i] = text[i+2] - 100
            
        else:
            control_data[i] = text[i+2] - 155
    
    print('control:',control_data)
            
    #rol:[-100:100],rol:[-100:100],yaw:[-100:100],thr:[-100:100]
    b.control(pit = control_data[0], yaw = control_data[1])
    
    #控制速度调试
    if text[5] ==  0: #上键按下
        
        
        if no_key == 1:
            
            no_key = 0 
            
            speed_value = speed_value + 1
            if speed_value > 5:
                speed_value = 5
            
            b.speed(speed_value) #调速
            
   #控制速度调试
    if text[5] ==  4: #下键按下
        
        if no_key == 1:
            
            no_key = 0 
            
            speed_value = speed_value - 1
            
            if speed_value < 1:
                speed_value = 1
                
            b.speed(speed_value) #调速    

    
    #检测X/Y/A/B按键
    if text[5] == 24: #Y键按下
        
        print('Y')
        b.start() #启动                 
 
        
    if text[5] == 72: #A键按下
        
        print('A')
        
        if no_key == 1:
            
            no_key = 0
            
            bl_node = not bl_node #灯光取反变化
            
            if bl_node:
        
                np[2]=RED 
                np[3]=RED
                np.write()
            
            else:
                
                np[2]=BLACK 
                np[3]=BLACK
                np.write()                    
 
    if text[5] == 40: #B键按下，可以自己添加功能。
        
        print('B')
        
        if no_key == 1:
            
            no_key = 0
                
            rgb_node = rgb_node + 1
            if rgb_node > 2:
                rgb_node = 0
            
            if rgb_node == 0:
                rgb_normal()                
                
            elif rgb_node == 1:
                start_rainbow()                
            
            elif rgb_node == 2:
                stop_rainbow()
                        

        
    if text[5] == 136: #X键按下,紧急停止
        print('X')
        #降落，不允许control
        b.stop()
        
    if text[5] ==  8: #无按键按下
        
        no_key = 1
        
    #读取四轴状态信息
    states = b.read_states()
    print('states: ',states)
    state_buf = [None]*16
    for i in range(8):
        for j in range(2):
            if j == 0:
                state_buf[i*2+j] = int((states[i]+32768)/256)
            else:
                state_buf[i*2+j] = int((states[i]+32768)%256)
                
    p.send(bytes(state_buf)) #蓝牙回传四轴姿态等数据
    

#按键1
KEY1=Pin(0,Pin.IN,Pin.PULL_UP) #构建KEY对象
key1_node = 0

def key1(KEY1):
    
    global key1_node
    
    if KEY1.value()==0: #确认按键被按下    
        time.sleep_ms(10) #消除抖动
        if KEY1.value()==0: #确认按键被按下
            print('KEY1')
            key1_node = 1
            
            while not KEY1.value(): #松开检测
                pass

KEY1.irq(key1,Pin.IRQ_FALLING) #定义中断，下降沿触发


#按键2
KEY2=Pin(21,Pin.IN,Pin.PULL_UP) #构建KEY对象
key2_node = 0

def key2(KEY2):
    
    global key2_node
    
    if KEY2.value()==0: #确认按键被按下
        time.sleep_ms(10) #消除抖动
        if KEY2.value()==0: #确认按键被按下
            print('KEY2')
            key2_node = 1
            
            while not KEY2.value(): #松开检测
                pass

KEY2.irq(key2,Pin.IRQ_FALLING) #定义中断，下降沿触发


item = 0 #项目

#判断是否已经校准，如果未校准，则进入校准模式。
#校准说明：将平衡车水平于地方放置，按下按键KEY2即可校准。相关数据会保存到根目录cal_data.txt文件
if not b.cal_states(): 
    
    item = 3
    key2_node = 1
    d.Picture(0,0,"/picture/calibrate.jpg")
    time.sleep_ms(1000)

else:
    
    d.Picture(0,0,"/picture/normal.jpg")    
    
while True:

    if key1_node: #按键1按下
        
        key1_node = 0 #清除按键标志位
        
        #项目加1
        item = item + 1
        if item == 4:
            item = 0
        
        if item == 0: 
            
            d.Picture(0,0,"/picture/normal.jpg")

        if item == 1:
            
            d.Picture(0,0,"/picture/control.jpg")
    
        if item == 2:
            
            d.Picture(0,0,"/picture/follow.jpg")
        
        if item == 3:
            
            d.Picture(0,0,"/picture/calibrate.jpg")
    
    if key2_node: #确认键按下
        
        key2_node = 0 #清除按键标志位
        
        d.fill(WHITE)
        
        if item == 0: #普通模式
            
            b.speed(4)
            b.start() #启动
            
            while True:
    
                data = b.read_states()
                #print(data)
                d.printStr('Normal Mode', 35, 10, BLACK, size=3)
                d.printStr('Angle:', 10, 60, BLUE, size=2)
                d.printStr(str(data[0]/10)+ ' '*5, 90, 60, RED, size=2)
                d.printStr('Speed:', 10, 90, BLUE, size=2)
                d.printStr(str('%.2f'%(data[1]/1000))+' m/s'+' '*3, 90, 90, RED, size=2)
                d.printStr('Distance:', 10, 120, BLUE, size=2)
                d.printStr(str(data[2])+' mm'+' '*3, 130, 120, RED, size=2)
                d.printStr('VBAT:', 10, 150, BLUE, size=2)
                d.printStr(str('%.2f'%(data[3]/100))+' V'+' '*3, 80, 150, RED, size=2)
                d.printStr('States:', 10, 180, BLUE, size=2)
                d.printStr(str(data[4]), 100, 180, RED, size=2)
                d.printStr('Contrl_Speed:', 10, 210, BLUE, size=2)
                d.printStr(str(data[5]), 170, 210, RED, size=2)
                time.sleep_ms(100)
                
                if key1_node: #返回
                   
                    item = item - 1 #返回功能页
                    
                    b.stop()
                    
                    break 
 
        elif item == 1: #遥控模式,使用pyController或app控制
            
            b.speed(4)
            b.start() #启动
            
            
            #初始化蓝牙BLE从机,广播名称为pyDrone
            ble = bluetooth.BLE()
            p = ble_simple_peripheral.BLESimplePeripheral(ble,name='pyBAL')
            
            #注册从机接收回调函数，收到数据会进入on_rx函数。#系统会自动广播, 连接断开后重新自动广播。
            p.on_write(on_rx)
            
            while True:
                
                data = b.read_states()
                #print(data)
                d.printStr('Control Mode', 25, 10, BLACK, size=3)
                d.printStr('Angle:', 10, 60, BLUE, size=2)
                d.printStr(str(data[0]/10)+ ' '*5, 90, 60, RED, size=2)
                d.printStr('Speed:', 10, 90, BLUE, size=2)
                d.printStr(str('%.2f'%(data[1]/1000))+' m/s'+' '*3, 90, 90, RED, size=2)
                d.printStr('Distance:', 10, 120, BLUE, size=2)
                d.printStr(str(data[2])+' mm'+' '*3, 130, 120, RED, size=2)
                d.printStr('VBAT:', 10, 150, BLUE, size=2)
                d.printStr(str('%.2f'%(data[3]/100))+' V'+' '*3, 80, 150, RED, size=2)
                d.printStr('States:', 10, 180, BLUE, size=2)
                d.printStr(str(data[4]), 100, 180, RED, size=2)
                d.printStr('Contrl_Speed:', 10, 210, BLUE, size=2)
                d.printStr(str(data[5]), 170, 210, RED, size=2)
                time.sleep_ms(100)
                
                if key1_node: #返回
                   
                    item = item - 1 #返回功能页
                    
                    b.stop()   
                    
                    for h in list(p._connections):
                        ble.gap_disconnect(h)
                    time.sleep_ms(100)    
                    ble.gap_advertise(None)   # 停止广播
                    
                    break 

            
        elif item == 2: #跟随模式
            
            #跟随模式时运动速度调为2
            b.speed(2)
            b.start()            
            
            target = 200 #跟随墓碑距离200mm
            
            count = 0
            while True:
    
                data = b.read_states()
                #print(data)
                if count == 10: #定时刷新
                    d.printStr('Follow Mode', 35, 10, BLACK, size=3)
                    d.printStr('Angle:', 10, 60, BLUE, size=2)
                    d.printStr(str(data[0]/10)+ ' '*5, 90, 60, RED, size=2)
                    d.printStr('Speed:', 10, 90, BLUE, size=2)
                    d.printStr(str('%.2f'%(data[1]/1000))+' m/s'+' '*3, 90, 90, RED, size=2)
                    d.printStr('Distance:', 10, 120, BLUE, size=2)
                    d.printStr(str(data[2])+' mm'+' '*3, 130, 120, RED, size=2)
                    d.printStr('VBAT:', 10, 150, BLUE, size=2)
                    d.printStr(str('%.2f'%(data[3]/100))+' V'+' '*3, 80, 150, RED, size=2)
                    d.printStr('States:', 10, 180, BLUE, size=2)
                    d.printStr(str(data[4]), 100, 180, RED, size=2)
                    d.printStr('Contrl_Speed:', 10, 210, BLUE, size=2)
                    d.printStr(str(data[5]), 170, 210, RED, size=2)
                    count = 0

                count = count + 1 
                distance = data[2]

                if distance > 0 and distance < 500: #有效运动范围
                    error = distance - target
                        
                    
                    pit = int(error * 0.6)  
    
                    if pit > 100:
                        pit = 100

                    if pit < -100:
                        pit = -100

                    b.control(pit=pit, yaw=0)                       
                
                time.sleep_ms(10)
                
                if key1_node: #返回
                    
                    b.stop()
                    
                    item = item - 1 #返回功能页
                    
                    break                

        elif item == 3: #校准模式
            
            while True:
                
                cal_data = b.read_cal_data()
                print(cal_data)
                d.printStr('Calibrate', 45, 10, BLACK, size=3)
                d.printStr('Angle: '+str('%.1f'%(cal_data[0]/10))+'   ', 10, 60, BLUE, size=2)
                d.printStr('GY(Offset): '+str('%.1f'%(cal_data[1]/10))+'   ', 10, 100, BLUE, size=2)
                d.printStr('Keep the Car Level', 10, 160, BLACK, size=2)
                d.printStr('Press KEY2 Confirm!', 10, 200, RED, size=2)
                time.sleep_ms(20)
                    
                if key2_node: #确认键按下
        
                    key2_node = 0 #清除按键标志位
                    
                    b.confirm_cal() #执行校准
                    
                    d.printStr('Success! Exit...   ', 10, 200, RED, size=2)
                    
                    time.sleep(2)
                    
                    #校准完成返回普通模式
                    item = item - 1 #返回功能页
                    key1_node = 1 
                    
                    break
                
                if key1_node: #返回
                   
                    item = item - 1 #返回功能页
                    
                    break 
            
            

