# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 16:47:11 2020

@author: haonan.liu
"""

from yacs.config import CfgNode as CN
import numpy as np

_C = CN()

#_C.ICON_DIR = r"C:\Users\haonan.liu\OneDrive - Driver Group PLC\Documents\Python Scripts\ocr_gui\icons"

_C.HEIGHT = 790
_C.WIDTH = 1500
_C.img_canvas_multiplier = 1
_C.rect = 10

_C.temp_img_path =  r".\memoryfile\temp1.png"
_C.rot_unit = -0.015
_C.btn_width = 0.028
_C.MAIN_TITLE = "Welcome to DAT OCR"
_C.TIELE =  "DAT Optical Character Recognition"

_C.processed_ext = (("Portable Document Format","*.pdf"),("PNG File",".png"),("all files","*.*"))
_C.logFORMAT = '%(asctime)s-%(levelname)s: %(message)s'
btn_x = np.array(range(18)) *0.045 +0.14
_C.btn_x = btn_x.tolist()

#the choice of getting lines methodology
_C.choice = [
    ("By Density",1),
    ("By Hough Lines",2),
    ("Save Button",3)]
#==========================================icon folders====================================================
_C.ICON_DIR = r".\icons"
_C.OPEN_ICON = _C.ICON_DIR+"\\file icon.png"
_C.EXIT_ICON = _C.ICON_DIR+"\\exit icon.png"
_C.HELP_IDX = _C.ICON_DIR +"\\delight.jpg"

_C.FOLDER_ICON = _C.ICON_DIR+"\\folder.png"
_C.MINUS_ICON = _C.ICON_DIR+"\\left.png"
_C.PLUS_ICON = _C.ICON_DIR+"\\right.png"
_C.EDIT_MODE_ICON = _C.ICON_DIR+"\\first-aid-kit.png"
_C.CROP_ICON = _C.ICON_DIR+"\\crop (1).png"
_C.RETURN_ICON = _C.ICON_DIR+"\\undo.png"
_C.UNDO_ICON = _C.ICON_DIR+"\\undo1.png"
_C.ROTATE1 = _C.ICON_DIR+"\\rotate.png"
_C.ROTATE2 = _C.ICON_DIR+"\\rotateBack.png"
_C.SCISSORS = _C.ICON_DIR+"\\scissors.png"
_C.ERASER = _C.ICON_DIR+"\\eraser.png"
_C.PENCIL = _C.ICON_DIR+"\\pencil.png"
_C.WAND = _C.ICON_DIR+"\\wand.png"
_C.TXT_ICON = _C.ICON_DIR+"\\txt.png"
_C.PDF_ICON = _C.ICON_DIR+"\\pdf.png"
_C.savebtnBlue = _C.ICON_DIR+"\\save.png"
_C.mask = _C.ICON_DIR+"\\facial-mask.png"
_C.excel_icon = _C.ICON_DIR +"\\excel.png"
