import time
from tkinter import *
import tkinter as tk
import json
import tkinter.font as tkFont
from os.path import expanduser
import os.path
import glob
import os
import requests
import win32gui
import win32con

root = tk.Tk()
chunkX = IntVar()
chunkZ = IntVar()
angle = StringVar()
version = "0.5"
JojoeMode = False
lastClip = "null_____"

fontStyle = tkFont.Font(family="TkDefaultFont", size=9)

Label(root, text="Chunk X:", font=fontStyle).grid(row=1, sticky=W)
Entry(root, width=10, exportselection=0, textvariable=chunkX, font=fontStyle).grid(row=2, padx=(5, 0), sticky=W)
Label(root, text="Chunk Z:", font=fontStyle).grid(row=3, sticky=W)
Entry(root, width=10, exportselection=0, textvariable=chunkZ, font=fontStyle).grid(row=4, padx=(5, 0), sticky=W)
Label(root, text="Angle: ", font=fontStyle).grid(row=5, sticky=W)
Entry(root, width=10, exportselection=0, textvariable=angle, font=fontStyle).grid(row=6, padx=(5, 0), sticky=W)
angle.set("1.00")

Label(root, text="Left Fat: -.01", font=fontStyle).grid(row=1, padx=(150, 0), sticky=W)
Label(root, text="Middle Fat: +.01", font=fontStyle).grid(row=2, padx=(150, 0), sticky=W)
Label(root, text="Right Fat: 0", font=fontStyle).grid(row=3, padx=(150, 0), sticky=W)
resultLabel = Label(root, text="", font=fontStyle)
resultLabel.grid(row=10, padx=(0, 0), sticky=E)

def loadLookup():
    global angleIndexes
    readFile = open(os.getcwd() + "/angleIndexes.json")
    angleIndexes = readFile.read()
    readFile.close()

def lookupAngle(angle):
    return json.loads(angleIndexes)[angle]

def parseData(jsonBlob, angle):
    contents = json.loads(jsonBlob)
    angles = contents[str(angle)]
    resultText = ''
    for i in angles:
        resultText += i + "\n"
    resultLabel.config(text=resultText, fg='green')
    
def getGitIndex(x):
    readFile = open(os.getcwd() + "/gitIndexes.json")
    indexes = json.loads(readFile.read())
    readFile.close()
    return str(indexes[str(x)])
    
def lookupChunk(coord):
    readFile = open(os.getcwd() + "/chunkIndexes.json")
    indexes = json.loads(readFile.read())
    readFile.close()
    return str(indexes[str(coord)])

def getXyz():
    resultLabel.config(text="")
    x = chunkX.get()
    z = chunkZ.get()
    ang = lookupAngle(angle.get())
    if JojoeMode:
        filePath = ("F:/forsenCD2" + "/" + str(x) + "/" + str(z) + ".json")
        if os.path.isfile(filePath):
            readFile = open(filePath, 'r')
            parseData(readFile.read(), ang)
            readFile.close()
    else:
        url = 'https://raw.githubusercontent.com/PerfectCDData/data' + getGitIndex(x) + '/main/' + str(x) + '/' + str(z) + '.json'
        data = requests.get(url, allow_redirects=True).content
        parseData(data, ang)
        
def enumHandler(mcWin, ctx):
    title = win32gui.GetWindowText(mcWin)
    if title.startswith('Minecraft') and (title[-1].isdigit() or title.endswith('Singleplayer') or title.endswith('Multiplayer (LAN)')):
        style = win32gui.GetWindowLong(mcWin, -16)
        if ctx:
            style = 382664704
            win32gui.SetWindowLong(mcWin, win32con.GWL_STYLE, style)
            win32gui.SetWindowPos(mcWin, win32con.HWND_TOP, 530, 250, 900, 550, 0x0004)
            return False
        if style == 369623040:
            rect = win32gui.GetWindowRect(mcWin)
            if rect[3] == 1080:
                win32gui.SetWindowPos(mcWin, win32con.HWND_TOP, 0, 0, 1920, 1027, 0x0004)
                return False
            else:
                win32gui.SetWindowPos(mcWin, win32con.HWND_TOP, 0, 0, 1920, 1080, 0x0004)
                return False
        else:
            style &= ~(0x00800000 | 0x00400000 | 0x00040000 | 0x00020000 | 0x00010000 | 0x00800000)
            win32gui.SetWindowLong(mcWin, win32con.GWL_STYLE, style)
            win32gui.SetWindowPos(mcWin, win32con.HWND_TOP, 0, 0, 1920, 1080, 0x0004)
        return False

def toggleRes(doThing):
    try:
        win32gui.EnumWindows(enumHandler, doThing)
    except:
        return

def doToggle():
    toggleRes(False)

def goWindow():
    toggleRes(True)
    
def parseClip(content):
    if not content.startswith("/execute in"):
        return
    parts = content.split(" ")
    x = parts[6].split(".")[0]
    z = parts[8].split(".")[0]
    chunkX.set(lookupChunk(x))
    chunkZ.set(lookupChunk(z))
    angle.set(lookupAngle(parts[9]))

Button(root, text="Get XYZ", command=getXyz).grid(row=7, sticky=W, padx=(5, 0))
Button(root, text="Toggle Resolution", command=doToggle).grid(row=8, sticky=E, padx=(5, 0))
Button(root, text="Windowed", command=goWindow).grid(row=9, sticky=E, padx=(5, 0))
root.resizable(False, False)
root.title("PerfectCD v" + version)
    
def mainLoop():
    global lastClip
    root.after(200, mainLoop)
    try:
        clip = root.clipboard_get()
    except:
        print('Failed to read from clipboard')
        clip = 'aaaaaaaaa'
    if clip != lastClip:
        parseClip(clip)
    lastClip = clip
loadLookup()
lastClip = root.clipboard_get()
root.after(0, mainLoop)
root.geometry('250x260')
root.mainloop()