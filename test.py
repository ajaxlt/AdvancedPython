#!/usr/bin/python
#coding:utf-8
import Tkinter as tk
from Tkinter import *
root = tk.Tk()
group = tk.LabelFrame(root,text = '你最喜欢中国四大美女中的哪一位？',padx = 5,pady = 5)
group.pack(padx = 10,pady = 10)

girls = [('西施',1),('王昭君',2),('杨玉环',3),('貂蝉',4)]
v = IntVar()
v.set(1)
for girl,num in girls:
    #调用父窗口是group而不是root，注意这个地方。
    Radiobutton(group,text = girl,variable = v,value = num).pack(anchor = W)
mainloop()
