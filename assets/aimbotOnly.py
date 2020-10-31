import cv2, math, time, win32gui, win32api, win32con
import pynput
from win32gui import PumpMessages, PostQuitMessage
import numpy as np
from mss import mss
import pyautogui, os
import ctypes
from ctypes import windll
import keyboard, mouse

clear = lambda: os.system('cls')

screenWidth = 1920
screenHieght = 1080



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



def set_pos(x, y):
    x = 1 + int(x * 65536./screenWidth)
    y = 1 + int(y * 65536./screenHieght)
    extra = ctypes.c_ulong(0)
    ii_ = pynput._util.win32.INPUT_union()
    ii_.mi = pynput._util.win32.MOUSEINPUT(x, y, 0, (0x0001 | 0x8000), 0, ctypes.cast(ctypes.pointer(extra), ctypes.c_void_p))
    command=pynput._util.win32.INPUT(ctypes.c_ulong(0), ii_)
    SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))


pyautogui.PAUSE = 0




classesNames = ['ct', 'ct_head', 't', 't_head']

net = cv2.dnn.readNetFromDarknet('../model/config.cfg', '../model/model.weights')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

def getOpponentPosition(frame, outputs, opponentTeam='t'):
    hT, wT, cT = frame.shape
    bbox = []
    classIds = []
    confs = []
    headBoxes = []
    bodyBoxes = []
    for output in outputs:
        for det in output:
            scores = det[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > 0.5:
                w, h = int(det[2] * wT), int(det[3] * hT)
                x, y = int((det[0]*wT) - (w / 2)), int((det[1] * hT) - (h/2))
                bbox.append([x,y,w,h])
                classIds.append(classId)
                confs.append(float(confidence))
    indices = cv2.dnn.NMSBoxes(bbox, confs, 0.5, 0.3)
    for i in indices:
        i = i[0]
        box = bbox[i]
        x, y, w, h = box[0], box[1], box[2], box[3]
        if opponentTeam == 'ct':
            if classIds[i] == 0:
                bodyBoxes.append([x,y,w,h])
            elif classIds[i] == 1:
                headBoxes.append([x, y, w, h])
        if opponentTeam == 't':
            if classIds[i] == 2:
                bodyBoxes.append([x,y,w,h])
            elif classIds[i] == 3:
                headBoxes.append([x, y, w, h])
    if len(headBoxes) > 0 and len(bodyBoxes) > 0:
        return headBoxes, bodyBoxes
    elif len(headBoxes) > 0:
        return headBoxes, None
    elif len(bodyBoxes) > 0:
        return None, bodyBoxes
    else:
        return None, None


def getClosestTarget(mousePoint, headBoxes):
    distance = math.sqrt( ((mousePoint[0]-headBoxes[0][0])**2)+((mousePoint[1]-headBoxes[0][1])**2) )
    closestBbox = headBoxes[0]
    if len(headBoxes) > 1:
        for bbox in headBoxes:
            if math.sqrt( ((mousePoint[0]-bbox[0])**2)+((mousePoint[1]-bbox[1])**2) ) < distance:
                distance = math.sqrt( ((mousePoint[0]-bbox[0])**2)+((mousePoint[1]-bbox[1])**2) )
                closestBbox = bbox
    return closestBbox


counter = 1
shotCounter = 0


clear()
toggleText = ''
fovWidth = 160
fovHeight = 160
shootLockedTarget = False
sniperRifle = False
headShotsOnly = True

opponentTeam = 'ct'

monitor = {"top": int(screenHieght/2-fovHeight/2), "left": int(screenWidth/2-fovWidth/2), "width": fovWidth, "height": fovHeight}
sct = mss()
while True:


    
    try:
        if keyboard.is_pressed('f8'):
            shootLockedTarget = not shootLockedTarget
            toggleText = 'TriggerBot = ' + str(shootLockedTarget)
            counter = 45
            cv2.waitKey(100)
        elif keyboard.is_pressed('f7'):
            sniperRifle = not sniperRifle
            toggleText = 'Sniper Aimbot = ' + str(sniperRifle)
            counter = 45
            cv2.waitKey(100)
        elif keyboard.is_pressed('f6'):
            drawOnScreen = not drawOnScreen
            toggleText = 'Drawing On Screen = ' + str(drawOnScreen)
            counter = 45
            cv2.waitKey(100)
        elif keyboard.is_pressed('f5'):
            headShotsOnly = not headShotsOnly
            toggleText = 'Headshot Only = ' + str(headShotsOnly)
            counter = 45
            cv2.waitKey(100)
        elif keyboard.is_pressed('f9'):
            if opponentTeam == 'ct':
                opponentTeam = 't'
                toggleText = 'Targeting Terrorists'
                counter = 45
                cv2.waitKey(100)
            else:
                opponentTeam = 'ct'
                toggleText = 'Targeting Counter-Terrorists'
                counter = 45
                cv2.waitKey(100)
    except:
        clear()

    
    frame = sct.grab(monitor)

    cur_x, cur_y= pyautogui.position()
    currentPositionPoint = [cur_x, cur_y]

    frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGBA2RGB)
    

    blob = cv2.dnn.blobFromImage(frame, 1/127, (fovWidth,fovHeight), [0,0,0], 1, crop=False)
    net.setInput(blob)


    layerNames = net.getLayerNames()
    outputNames = [layerNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    outputs = net.forward(outputNames)

    headBoxes, bodyBoxes = getOpponentPosition(frame, outputs, opponentTeam=opponentTeam)

    # if aimTarget == True:
    if headBoxes is not None:
        if sniperRifle == False:
            closestBbox = getClosestTarget(currentPositionPoint, headBoxes)
            x, y, w, h= closestBbox[0], closestBbox[1], closestBbox[2], closestBbox[3]
            set_pos(int(x+(w/2)+ (screenWidth/2 - fovWidth/2)), int(y+(h/2) + (screenHieght/2-fovHeight/2)))
            if cur_x > x+(screenWidth/2 - 80) and cur_x < x+(screenWidth/2 - 80)+w and cur_y > y+(screenHieght/2 - 80) and cur_y < y+(screenHieght/2 - 80)+h and shootLockedTarget == True:
                if shotCounter < 1:
                    pyautogui.click()
                    shotCounter = 10
    if bodyBoxes is not None:
        if sniperRifle == True:
            closestBbox = getClosestTarget(currentPositionPoint, bodyBoxes)
            x, y, w, h= closestBbox[0], closestBbox[1], closestBbox[2], closestBbox[3]
            set_pos(int(x+(w/2)+ (screenWidth/2 - fovWidth/2)), int(y+(h/2) - 10 + (screenHieght/2-fovHeight/2)))
            if cur_x > x+(screenWidth/2 - 80) and cur_x < x+(screenWidth/2 - 80)+w and cur_y > y+(screenHieght/2 - 80) and cur_y < y+(screenHieght/2 - 80)+h and shootLockedTarget == True:
                # pyautogui.click(button='right')
                # cv2.waitKey(50)
                # pyautogui.click()
                pyautogui.press('Q', presses=2, interval=0.1)
        elif headBoxes is None and headShotsOnly == False:
            closestBbox = getClosestTarget(currentPositionPoint, bodyBoxes)
            x, y, w, h= closestBbox[0], closestBbox[1], closestBbox[2], closestBbox[3]
            set_pos(int(x+(w/2)+ (screenWidth/2 - fovWidth/2)), int(y+(h/2) + (screenHieght/2-fovHeight/2)))
            if cur_x > x+(screenWidth/2 - 80) and cur_x < x+(screenWidth/2 - 80)+w and cur_y > y+(screenHieght/2 - 80) and cur_y < y+(screenHieght/2 - 80)+h and shootLockedTarget == True:
                pyautogui.click()
    cv2.waitKey(1)
    if shotCounter > 0:
        shotCounter -= 1
    
    
