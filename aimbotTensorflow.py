from absl import app
import cv2
import tensorflow as tf
from assets.yolov3_tf2.models import (
    YoloV3Tiny
)
from assets.yolov3_tf2.dataset import transform_images
from assets.yolov3_tf2.utils import draw_outputs, get_class_colors
import os
import numpy as np
from mss import mss
import pyautogui
import ctypes, pynput, math

clear = lambda: os.system('cls')



SendInput = ctypes.windll.user32.SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]
class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]
class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]
class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]
class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


def set_pos(pos):
    x, y = pos
    x = 1 + int(x * 65536./screenWidth)
    y = 1 + int(y * 65536./screenHeight)
    extra = ctypes.c_ulong(0)
    ii_ = pynput._util.win32.INPUT_union()
    ii_.mi = pynput._util.win32.MOUSEINPUT(x, y, 0, (0x0001 | 0x8000), 0, ctypes.cast(ctypes.pointer(extra), ctypes.c_void_p))
    command=pynput._util.win32.INPUT(ctypes.c_ulong(0), ii_)
    SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))


pyautogui.PAUSE = 0

fovSize = 128
screenWidth = 1920
screenHeight = 1080

class_names = ['ct','ct_head','t', 't_head']

def getCenterPoint(pt1, pt2):
    x1, y1 = pt1
    x2, y2 = pt2
    return(int((x1+x2)/2)+ screenWidth/2 - fovSize/2,int((y1+y2)/2)+ screenHeight/2 - fovSize/2)

def checkPointInRectangle(point, top_left, bottom_right):
    x_point, y_point = point
    x1, y1 = top_left
    x2, y2 = bottom_right
    if x_point > x1 and x_point < x2 and y_point > y1 and y_point < y2:
        return True
    return False

def getOpponentPositionGPU(frame, sess, yolo):
    frame_in = frame.copy()
    frame_in = cv2.resize(frame_in, (fovSize, fovSize))
    frame_in = np.expand_dims(frame_in, 0) / 255.0
    boxes, objectness, classes, nums = sess.run(
                yolo.output, 
                feed_dict={yolo.input: frame_in}, 
                options=None, 
                run_metadata=None)
    boxes, objectness, classes, nums = boxes[0], objectness[0], classes[0], nums[0]
    wh = np.flip(frame.shape[0:2])
    headBoxes = []
    bodyBoxes = []
    for i in range(nums):
        class_name = class_names[int(classes[i])]
        if 'head' in class_name:
            box = np.array(boxes[i]) * wh[0]
            headBoxes.append(box)
        else:
            box = np.array(boxes[i]) * wh[0]
            bodyBoxes.append(box)
    return headBoxes, bodyBoxes
    
def getClosestTarget(mousePoint, headBoxes):
    distance = math.sqrt( ((mousePoint[0]-headBoxes[0][0])**2)+((mousePoint[1]-headBoxes[0][1])**2) )
    closestBbox = headBoxes[0]
    if len(headBoxes) > 1:
        for bbox in headBoxes:
            if math.sqrt( ((mousePoint[0]-bbox[0])**2)+((mousePoint[1]-bbox[1])**2) ) < distance:
                distance = math.sqrt( ((mousePoint[0]-bbox[0])**2)+((mousePoint[1]-bbox[1])**2) )
                closestBbox = bbox
    return closestBbox

def triggerCheck(top_left, bottom_right):
    crosshair_x, crosshair_y = pyautogui.position()
    x1, y1 = top_left
    x2, y2 = bottom_right
    # print(crosshair_x > x1 , crosshair_x < x2 , crosshair_y > y1 , crosshair_y < y2)
    # exit()
    if crosshair_x > x1 and crosshair_x < x2 and crosshair_y > y1 and crosshair_y < y2:
        pyautogui.click()

def main(_argv):
    sess = tf.keras.backend.get_session()


    physical_devices = tf.config.experimental.list_physical_devices('DML')
    if len(physical_devices) > 0:
        tf.config.experimental.set_memory_growth(physical_devices[0], True)
    yolo = YoloV3Tiny(classes=4)
    try:
        yolo.load_weights('./assets/checkpoints/config_yolov3_final.tf')
    except:
        clear()
        print('Error\n-----\n')
        print('Download tensorflow weights from repository and extract them to assets folder.')
        input('Press enter to launch CPU version...')
        exit(0)
    class_names = ['ct', 'ct_head', 't', 't_head']
    # class_colors = [(51,255,255), (0,244,244), (255,51,51), (204,0,0)]

    monitor = {"top": int(screenHeight/2-fovSize/2), "left": int(screenWidth/2-fovSize/2), "width": fovSize, "height": fovSize}

    sct = mss()
    clear()
    print('Launching aimbot on GPU...')
    print('Aimbot Enabled')
    print('FOV Size: ' + str(fovSize) + 'x' + str(fovSize))
    while True:
        
        frame = sct.grab(monitor)
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGBA2RGB)
        headBoxes, bodyBoxes = getOpponentPositionGPU(frame, sess, yolo)
        if len(headBoxes) > 0:
            closestBox = getClosestTarget(pyautogui.position(),headBoxes)
            top_left = tuple((np.array(closestBox[0:2])).astype(np.int32))
            bottom_right = tuple((np.array(closestBox[2:4])).astype(np.int32))
            centerPoint = getCenterPoint(top_left, bottom_right)
            set_pos(centerPoint)
            triggerCheck(top_left, bottom_right)

        

if __name__ == "__main__":
    try:
        app.run(main)
    except SystemExit:
        pass

