# CSGO-Aimbot-CNN
CS:GO Aimbot based on convolutional neural networks.</br>
![Showcase](https://github.com/ofeksadlo/CSGO-Aimbot-CNN/blob/main/ezgif-5-06587c2150ec.gif)</br>
# How it works
The program will capture 160x160 from the screen then it will</br>
detect whether a ct solider in the cropped frame. If there is it will</br>
aim to his head and shoot.</br>
The entire process will be displayed at your screen.</br>
At the top left you will see how many frames the model process in a second (The higher the better).
# How to make it work
1) You need to play on fullscreen windowed. For the overlays to show and for the frame capturing.
2) **Mouse raw input needs to be disabled** for the aimbot to work properly.
3) Resolution has to be 1920x1080. Otherwise you'll need to change screenWidth and screenHieght values.</br>
   Notice that fullscreen windowed mode just use native resolution.
4) Install all dependencies from reqiurements.txt file.
5) Open main.py and go to the game. Place an opponent in your FOV and he will die.</br>

# Keyboard Control
| Key | Action |
| ------ | ------ |
| F5 | Toggle Headshot only (Target heads only) |
| F6 | Toggle Drawing on screen |
| F7 | Toggle Sniper aimbot (Target body and right click before firing) |
| F8 | Toggle Triggerbot |

# Compatibility issues
*  The aimbot is good but not perfect it's based on a custom yolo-tiny model.</br>
   This verison of an aimbot is based completely on CPU. Which in CSGO is a big downside.</br>
   Because CSGO is based heavily on CPU the aimbot and CSGO ending up fighting for performance. So</br>
   consider typing in concole fps_max 60. The reason I don't use GPU for inferencing the model.</br>
   Is because I have AMD graphic card. And although there are some ports to use AMD GPU using</br>
   TensorFlow I've decided to simple develop this aimbot CPU only.</br>
   In theory this aimbot can be much more powerful with a decent</br>
   NVIDIA graphic card.</br>
*  In order to get a decent frames the model process in a second. I'v only used</br>
   the small fov for detecting opponents.</br>
*  The higher the sensetivity the more snappy the aimbot is.</br>
*  As of for now the model is only trained for ct opponents.</br> 
   So it's useless against terrorists.
*  The aimbot only tested on Window 10 with 1920x1080 resolution. But should work</br>
   for linux as well.

# Future plans
1) Adding support for aiming on terrorist opponents.
2) ~~Adding support for sniper rifles.~~ (Added)
3) Adding spray control that will target the head.
4) ~~Adding keyboard shortcut to toggle aimbot On / Off.~~ (Added)
5) Adding spray control crosshair.
6) Switching between Sniper aimbot to rifle aimbot to pistol aimbot</br>
   based on which weapon used.</br>
   By detecting weapon text:</br>
   <img src="https://github.com/ofeksadlo/CSGO-Aimbot-CNN/blob/main/textDemo.jpg" alt="textDemo" width="150" height="150">
# Disclaimer
**This project is for educational purposes only.**</br>
Developed in Python 3.7.7
