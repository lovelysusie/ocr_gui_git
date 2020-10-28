# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 11:02:28 2020

@author: haonan.liu
"""

from tkinter import *
from tkinter import ttk
root = Tk()

h = ttk.Scrollbar(root, orient=HORIZONTAL)
v = ttk.Scrollbar(root, orient=VERTICAL)
canvas = Canvas(root, scrollregion=(0, 0, 1000, 1000), yscrollcommand=v.set, xscrollcommand=h.set)
h['command'] = canvas.xview
v['command'] = canvas.yview
ttk.Sizegrip(root).grid(column=1, row=1, sticky=(S,E))

canvas.grid(column=0, row=0, sticky=(N,W,E,S))
h.grid(column=0, row=1, sticky=(W,E))
v.grid(column=1, row=0, sticky=(N,S))
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

lastx, lasty = 0, 0

def xy(event):
    global lastx, lasty
    lastx, lasty = canvas.canvasx(event.x), canvas.canvasy(event.y)

def setColor(newcolor):
    global color
    color = newcolor
    canvas.dtag('all', 'paletteSelected')
    canvas.itemconfigure('palette', outline='white')
    canvas.addtag('paletteSelected', 'withtag', 'palette%s' % color)
    canvas.itemconfigure('paletteSelected', outline='#999999')

def addLine(event):
    global lastx, lasty
    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    canvas.create_line((lastx, lasty, x, y), fill=color, width=5, tags='currentline')
    lastx, lasty = x, y

def doneStroke(event):
    canvas.itemconfigure('currentline', width=1)        
        
canvas.bind("<Button-1>", xy)
canvas.bind("<B1-Motion>", addLine)
canvas.bind("<B1-ButtonRelease>", doneStroke)

id = canvas.create_rectangle((10, 10, 30, 30), fill="red", tags=('palette', 'palettered'))
canvas.tag_bind(id, "<Button-1>", lambda x: setColor("red"))
id = canvas.create_rectangle((10, 35, 30, 55), fill="blue", tags=('palette', 'paletteblue'))
canvas.tag_bind(id, "<Button-1>", lambda x: setColor("blue"))
id = canvas.create_rectangle((10, 60, 30, 80), fill="black", tags=('palette', 'paletteblack', 'paletteSelected'))
canvas.tag_bind(id, "<Button-1>", lambda x: setColor("black"))

setColor('black')
canvas.itemconfigure('palette', width=5)
root.mainloop()

#===========================================================================================#
import tkinter as tk
 
root = tk.Tk()
 
WIDTH = HEIGHT = 400
 
x1 = y1 = WIDTH / 2
 
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack()
 
c1 = canvas.create_rectangle(x1, y1, x1 + 10, y1 + 10)
c2 = canvas.create_rectangle(x1, y1, x1 + 10, y1 + 10)
 
 
def draw_rect():
    global c2
    canvas.delete(c2)
    c2 = canvas.create_rectangle(x1, y1, x1 + 10, y1 + 10, fill="green")
 
 
def del_rect():
    canvas.delete(c1)
    #canvas.create_rectangle(x1, y1, x1 + 10, y1 + 10, fill="white", opacity=0.5)
 
 
def move(event):
    global x1, y1
    if event.char == "a":
        del_rect()
        x1 -= 10
    elif event.char == "d":
        del_rect()
        x1 += 10
    elif event.char == "w":
        del_rect()
        y1 -= 10
    elif event.char == "s":
        del_rect()
        y1 += 10
    # draw_rect()
    draw_rect()
 
 
root.bind("<Key>", move)
 
root.mainloop()






from tkinter import * 

def onObjectClick(event):                  
    print('Got object click', event.x, event.y)
    print(event.widget.find_closest(event.x, event.y))

root = Tk()
canv = Canvas(root, width=100, height=100)
obj1Id = canv.create_line(0, 30, 100, 30, width=5, tags="obj1Tag")
obj2Id = canv.create_text(50, 70, text='Click', tags='obj2Tag')

canv.tag_bind(obj1Id, '<ButtonPress-1>', onObjectClick)       
canv.tag_bind('obj2Tag', '<ButtonPress-1>', onObjectClick)   
print('obj1Id: ', obj1Id)
print('obj2Id: ', obj2Id)
canv.pack()
root.mainloop()


