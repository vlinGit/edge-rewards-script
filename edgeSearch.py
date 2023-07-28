import pyautogui
import random
import time

points = 0
cap = 200
x = 700
y = 50

letters = "abcdefghijklmnopqrstuvwxyz"

time.sleep(2)

while points < cap:
    
    count = 0
    wordSize = random.randint(2,6)
    
    pyautogui.moveTo(x,y)
    pyautogui.mouseDown()
    pyautogui.mouseUp()
    
    while count < wordSize:
        pyautogui.typewrite(letters[random.randint(0,25)])
        count += 1
        
    points+=5
    time.sleep(0.03)
    pyautogui.press("enter")
