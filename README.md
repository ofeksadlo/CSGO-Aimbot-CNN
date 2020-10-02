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
1) You need to play on fullscreen windowed.
2) Mouse raw input needs to be disabled for the aimbot to work properly.
3) Resolution has to be 1920x1080 otherwise you'll need to change values to fit your custom resolution.
4) Install all dependencies from dependency file.
5) Open main.py and go to the game. Place an opponent in your FOV and he will die.

# Compatibility issues
The aimbot is good but not perfect it's based on a custom yolo-tiny model.</br>
This verison of an aimbot is based completely on CPU. Which in CSGO is a big downside.</br>
Because CSGO is based heavily on CPU the aimbot and CSGO ending up fighting for performance. So</br>
consider typing in concole fps_max 60. The reason I don't use GPU for inferencing the model.</br>
Is because I have AMD graphic card. </br>
In theory this aimbot can be much more powerful with a decent</br>
NVIDIA graphic card.</br>

In order to get a decent frames the model process in a second. I'v only used</br>
the small fov for detecting opponents.</br>

The higher the sensetivity the more snappy the aimbot is.</br>

As of for now the model is only trained for ct opponents.</br> 
So it's useless against terrorists.

# Future plans
1) Adding support for aiming on terrorist opponents.
2) Adding support for sniper rifles.
3) Adding spray control that will target the head.
4) Adding keyboard conrtol to toggle aimbot On / Off.
