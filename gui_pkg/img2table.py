# -*- coding: utf-8 -*-
"""
Created on Tue May 12 17:46:17 2020

@author: haonan.liu
"""


import ocr_pkg.image_segmentation as img_seg
import ocr_pkg.img_recgonition as img_ocr
import pytesseract
import pandas as pd
import numpy as np
import cv2
from ocr_pkg.table_detect import detectTable

folder = r"C:\Users\haonan.liu\OneDrive - Driver Group PLC\Documents\Python Scripts\ocr_gui_exe(Jul)"

def img2df(img, v_line = None):
    """
    This function is to convert image to a pandas data frame and extract its content
    
    Parameters
    ----------
    img : array
        the input image

    Returns
    -------
    df : pandas dataframe
        the output table in df format

    """
    df = {}
    kernel = np.ones((2, 2), np.uint8)
    
    col_txt = None
    erode = cv2.erode(img.copy(),kernel,iterations = 2)
    
    mask, joint = detectTable(erode).run()
    houghs = img_seg.img_line_det(mask,3,20,220)
    rows, cols = img_ocr.filter_line(houghs,5)
    if v_line:
        cols = v_line
        print("Column lines getting from user operation")
        # check the rows and cols is correct or not, if not need to change some parameters
    #img_ocr.draw_lines(img.copy() ,cols, rows, r"D:\samples\houghline111.png" )
    if len(cols) != 0:
        print("{} column lines detected".format(len(cols)))
        for col_n, (left,right) in enumerate(zip(cols, cols[1:])):
            print("left {}, right {}".format(left, right))
            
            img_col = img[:,left:right]
            col_txt = pytesseract.image_to_data(img_col)
            try:
                col_cell = get_col_txt(col_txt, rows)
                col_name = "Col "+str(col_n)
                df[col_name] = col_cell
                print("manage to get a df")
            except:
                print("error in converting")
                pass
        
    else:
        print("column lines 0")
        col_txt = pytesseract.image_to_data(img)
        col_cell = get_col_txt(col_txt, rows)
        df['content'] = col_cell
    return pd.DataFrame(df)
            


def get_col_txt(data_str,rows_y_list=None):
    """
    this function is to place the cells in one column in to specific rows

    Parameters
    ----------
    data_str : str
        the output of pytesseract image to data
    rows_y_list : list
        the lsit of the y coordinate of each rows
        default is None, if None, will aggregate by natural line

    Returns 
    -------
    a list of strings for each cells

    """
    data_str = data_str.split('\n')
    data_str = list(map(lambda x: x.split('\t'), data_str))
    col_txt_df = pd.DataFrame(data_str[1:], columns = data_str[0])
    col_txt_df['block_num'] = col_txt_df['block_num'].apply(lambda x: int(x))
    col_txt_df['line_num'] = col_txt_df['line_num'].apply(lambda x: int(x))
    col_txt_df['top'] = col_txt_df['top'].apply(lambda x: int(x))
    col_txt_df['text'] = col_txt_df['text'].fillna("")
    if rows_y_list:
        col_cell = [""] * len(rows_y_list)
        for r_n, (row_top, row_btm) in enumerate(zip(rows_y_list, rows_y_list[1:])):
            col_cell[r_n] = " ".join(col_txt_df[(col_txt_df['top']>=row_top+5) & (col_txt_df['top']<=row_btm+5)]['text']).strip()
        return col_cell
    else:
        chk = col_txt_df.groupby(['block_num', 'par_num', 'line_num'])['text'].apply(lambda x: ' '.join(x).strip()).reset_index()
        return chk[chk['text'] != '']['text'].tolist()


    
