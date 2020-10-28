# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 15:17:54 2019

@author: haonan.liu
"""

import cv2
import numpy as np
from matplotlib import pyplot as plt
from ocr_pkg.table_detect import detectTable
import ocr_pkg.image_segmentation as img_seg
import ocr_pkg.img_recgonition as img_ocr


#https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html

#src_path = r"D:\samples\1B-Vol No.1 57.png"
#src_path = r"D:\samples\Pages from 1B-Vol No.1.png"


class get_PerspectiveTransform():
    def __init__(self, img_in, size, max_gap = 20):
        self.img_in = img_in
        self.size = size
        self.max_gap = max_gap
    #step one get structural element
    def stru_element_gen(self):
        disc = np.zeros([self.size, self.size])
        disc[0] = 1
        i = 1
        while i < self.size:
            disc[i][0] = 1
            i  = i + 1
        return np.uint8(disc)
    
    #setp two eroding
    def tips_collect(self, kernel_in):
        if len(self.img_in.shape) == 3:
            gray_img = cv2.cvtColor(self.img_in,cv2.COLOR_BGR2GRAY)
        else:
            gray_img = self.img_in
        morphological = cv2.erode(gray_img, kernel_in, iterations=2)
        mask, joint = detectTable(morphological.copy()).run()
        tips_col = []
        tips = np.where(joint == 255)
        i = 0
        while i < len(tips[0]):
            tips_col.append([tips[1][i],tips[0][i]])
            i = i + 1
        return tips_col
        
    def corner_extract(self, tips_in):
        tips_in = sorted(tips_in, key = lambda x: x[0])
        groups = [[tips_in[0]]]
        for x in tips_in[1:]:
            if abs(x[0] - groups[-1][-1][0]) <= self.max_gap:
                groups[-1].append(x)
            else:
                groups.append([x])
        groups = self.__tip_filter(groups)
        return groups

    def __pickup_corner(self, group_in):
        a = group_in[0][0]
        b = group_in[-1][0]
        c = group_in[0][-1]
        d = group_in[-1][-1]
        return a,b,c,d
    
    def __tip_filter(self, group_in):
        """
        this funtions is to 
        """
        result = []
        for sub_grp in group_in:
            sub_grp = sorted(sub_grp, key = lambda x: x[1])
            result.append(sub_grp)
        return result


    def perspectiveTransform(self, a,b,c,d):
        pts1 = np.float32([a,b,c,d])
        width = b[0] - a[0]
        height = c[1] - a[1]
        pts2 = np.float32([[0,0], [width,0], [0,height], [width, height]])
        M = cv2.getPerspectiveTransform(pts1,pts2)
        dst = cv2.warpPerspective(self.img_in.copy(),M,(width,height))
        #add an outer bounding on image
        dst= cv2.copyMakeBorder(dst,3,3,3,3,cv2.BORDER_CONSTANT,value=(0,0,0))
        return dst
    
    def main_fun(self):
        kernel = self.stru_element_gen()
        tips = self.tips_collect(kernel)
        group_in = self.corner_extract(tips)
        a,b,c,d = self.__pickup_corner(group_in)
        img_out = self.perspectiveTransform(a,b,c,d)
        #print(a,b,c,d)
        return img_out

def show_img(img_input):
    cv2.namedWindow("current img", cv2.WINDOW_NORMAL)
    cv2.imshow("current img", img_input)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


#result_path = r"D:\samples"
#img = cv2.imread(src_path)

#img_crop = get_PerspectiveTransform(img, 5, 100).main_fun()
#show_img(img_crop)

#----------------------generate mask to find out the positon of rows and columns-----------------------------

class getRowColumnLine():
    def __init__(self, img_in, scaleW=400, scaleH=400, multiplier=0.5):
        self.img = img_in
        self.scaleW = scaleW
        self.scaleH = scaleH
        try:
            (self.rows, self.cols,self.ch) = self.img.shape
            self.gray_img = cv2.cvtColor(img_in,cv2.COLOR_BGR2GRAY)
        except:
            (self.rows, self.cols) = self.img.shape
            self.gray_img = img_in
        self.multiplier = multiplier
        
    def vertical(self):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.cols // self.scaleW, 1))
        img_vertical = cv2.erode(self.gray_img.copy(), kernel, iterations=1)
        margin_v = np.sum(img_vertical, axis = 0)
        #self.__line_plot(margin_v)
        margin_v = self.__getLocalLowest(margin_v, self.rows)
        return margin_v
    
    def horizontal(self):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, self.rows // self.scaleH))
        img_vertical = cv2.erode(self.gray_img.copy(), kernel, iterations=1)
        margin_h = np.sum(img_vertical, axis = 1)
        #self.__line_plot(margin_h)
        margin_h = self.__getLocalLowest(margin_h, self.cols)
        return margin_h

    def __line_plot(self, margin_in):
        plt.figure(figsize=(30,10))
        plt.plot(range(len(margin_in)), margin_in)
        plt.show()   
        
    def __getLocalLowest(self,margin_in, edge_in):
        threshold = edge_in * self.multiplier * 255
        return [[y,i] for i, y in enumerate(margin_in)
            if ((i == 0) or (margin_in[i - 1] >= y))
            and ((i == len(margin_in) - 1) or (y < margin_in[i+1])) and (y < threshold)]

class getHoughLine():
    def __init__(self, img_in, max_gap = 10):
        self.img = img_in
        self.kernel = np.ones((2, 2), np.uint8)
        self.erode = cv2.erode(self.img.copy(),self.kernel,iterations = 2)
        self.max_gap = max_gap
    def run(self):
        mask, joint = detectTable(self.erode).run()
        houghs = img_seg.img_line_det(mask,3,20,220)
        rows, cols = img_ocr.filter_line(houghs, self.max_gap)
        return rows, cols
    def getMask(self):
        mask, joint = detectTable(self.erode).run()
        return mask

def draw_auxiliary_line(img_in,margin, direction):
    img_w_line = img_in.copy()
    x, y, ch = img_in.shape
    if direction == "h":
        for line in margin:
            img_w_line = cv2.line(img_w_line, (0, line[1]), (y, line[1]), (0,255,0), 2 )
    if direction == "v":
        for line in margin:
            img_w_line = cv2.line(img_w_line, (line[1], 0), (line[1],x), (0,0,255), 2 )
    return img_w_line
    

#---------------------remove table border-----------------------------
  
def rm_lines(img_in):
    mask, joint = detectTable(img_in).run()
    kernel = np.ones((2, 2), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations =2)
    gray_img = cv2.cvtColor(img_in.copy(), cv2.COLOR_BGR2GRAY)
    img_no_border = cv2.add(gray_img, mask)
    return img_no_border


#---------------------remove table border-----------------------------
class Stack:
    def __init__(self):
        self.items = []
    
    def isEmpty(self):
        return self.items == []
    
    def push(self, item):
        self.items.append(item)
        
    def pop(self):
        return self.items.pop()
    
    def peek(self):
        return self.items[len(self.items)-1]
    
    def size(self):
        return len(self.items)
    