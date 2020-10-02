import cv2, math, time, win32gui, win32api, win32con
import pynput
from win32gui import PumpMessages, PostQuitMessage
import numpy as np
# from pyautogui import moveTo, position, click, moveRel, PAUSE
from mss import mss
import pyautogui, os
import ctypes
from ctypes import windll
import pygame



screenWidth = 1920
screenHieght = 1080

x = 0
y = 0
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

fpsClock = pygame.time.Clock()
pygame.init()
screen = pygame.display.set_mode((1920, 1080), pygame.HWSURFACE) # For borderless, use pygame.NOFRAME
done = False
fuchsia = (255, 0, 128)  # Transparency color
dark_red = (139, 0, 0)
blue = (0,0,255)
red = (255,0,0)
green = (0,255,0)
# Set window transparency color
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                       win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)

SetWindowPos = windll.user32.SetWindowPos

NOSIZE = 1
NOMOVE = 2
TOPMOST = -1
NOT_TOPMOST = -2

def alwaysOnTop(yesOrNo):
    zorder = (NOT_TOPMOST, TOPMOST)[yesOrNo] # choose a flag according to bool
    hwnd = pygame.display.get_wm_info()['window'] # handle to the window
    SetWindowPos(hwnd, zorder, 0, 0, 0, 0, NOMOVE|NOSIZE)

alwaysOnTop(True)


font = pygame

SendInput = ctypes.windll.user32.SendInput

def set_pos(x, y):
    x = 1 + int(x * 65536./screenWidth)
    y = 1 + int(y * 65536./screenHieght)
    extra = ctypes.c_ulong(0)
    ii_ = pynput._util.win32.INPUT_union()
    ii_.mi = pynput._util.win32.MOUSEINPUT(x, y, 0, (0x0001 | 0x8000), 0, ctypes.cast(ctypes.pointer(extra), ctypes.c_void_p))
    command=pynput._util.win32.INPUT(ctypes.c_ulong(0), ii_)
    SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))


def drawText(text, x, y, backgroundColor=green, textColor=blue, textSize=16):
    font = pygame.font.Font('freesansbold.ttf', textSize) 
    # create a text suface object, 
    # on which text is drawn on it. 
    fontText = font.render(text, True, textColor, backgroundColor) 
    # create a rectangular object for the 
    # text surface object 
    textRect = fontText.get_rect()  
    # set the center of the rectangular object. 
    textRect.center = (x, y) 
    screen.blit(fontText, textRect)

def drawBox(bboxes, boxText='', boxColor=green, textColor=blue):
    boxColorList = list(boxColor)
    pygame.draw.rect(screen, [0, 255, 0], [880, 460, 160, 160], 1)
    for box in bboxes:
        x, y ,w ,h = int(box[0]), int(box[1]), int(box[2]), int(box[3])
        if boxText != '':
            drawText(boxText, x+25 + (screenWidth/2 - 80), y-10 + (screenHieght/2 - 80), backgroundColor=boxColor, textColor=textColor)
        pygame.draw.rect(screen, boxColorList, [x + (screenWidth/2 - 80), y + (screenHieght/2 - 80), w, h], 3)



pyautogui.PAUSE = 0




classesNames = ['ct', 'ct_head']

net = cv2.dnn.readNetFromDarknet('config.cfg', 'model.weights')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

def getOpponentPosition(frame, outputs, fovWidth=150, fovHeight=150):
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
            if confidence > 0.8:
                w, h = int(det[2] * wT), int(det[3] * hT)
                x, y = int((det[0]*wT) - (w / 2)), int((det[1] * hT) - (h/2))
                bbox.append([x,y,w,h])
                classIds.append(classId)
                confs.append(float(confidence))
    indices = cv2.dnn.NMSBoxes(bbox, confs, 0.8, 0.3)
    for i in indices:
        i = i[0]
        box = bbox[i]
        x, y, w, h = box[0], box[1], box[2], box[3]
        if classIds[i] == 0:
            bodyBoxes.append([x,y,w,h])
        elif classIds[i] == 1:
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

        
aimTarget = True
shootLockedTarget = True
monitor = {"top": int(screenHieght/2-80), "left": int(screenWidth/2-80), "width": 160, "height": 160}
sct = mss()
while True:


    screen.fill(fuchsia)

    pygame.draw.rect(screen, [0, 255, 0], [880, 460, 160, 160], 1)

    timer = cv2.getTickCount()


    
    frame = sct.grab(monitor)

    cur_x, cur_y= pyautogui.position()
    currentPositionPoint = [cur_x, cur_y]

    frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGBA2RGB)
    

    blob = cv2.dnn.blobFromImage(frame, 1/127, (160,160), [0,0,0], 1, crop=False)
    net.setInput(blob)


    layerNames = net.getLayerNames()
    outputNames = [layerNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    outputs = net.forward(outputNames)

    headBoxes, bodyBoxes = getOpponentPosition(frame, outputs)
    allBboxes = []
    if bodyBoxes is not None:
        drawBox(bodyBoxes, boxColor=blue)
    if headBoxes is not None:
        drawBox(headBoxes, boxText='Head', boxColor=red, textColor=green)
        closestBbox = getClosestTarget(currentPositionPoint, headBoxes)
        x, y, w, h= closestBbox[0], closestBbox[1], closestBbox[2], closestBbox[3]
        set_pos(int(x+(w/2)+ (screenWidth/2 - 80)), int(y+(h/2) + (screenHieght/2-80)))
        if cur_x > x+(screenWidth/2 - 80) and cur_x < x+(screenWidth/2 - 80)+w and cur_y > y+(screenHieght/2 - 80) and cur_y < y+(screenHieght/2 - 80)+h and shootLockedTarget == True:
            pyautogui.click()
    fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
    drawText('Detection FPS: ' + str(int(fps)),150,25,backgroundColor=fuchsia, textColor=green, textSize=32)
    pygame.display.update()
    cv2.waitKey(1)
