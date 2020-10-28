# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 11:35:06 2020

@author: haonan.liu
"""

from tkdocviewer import DocViewer
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
from gui_pkg.pdf_display_bespoke import display_pdf
import os
import cv2
import ocr_pkg.image_segmentation as img_seg
from gui_pkg.table_crop import get_PerspectiveTransform, getRowColumnLine
import gui_pkg.table_crop as table_crop
import numpy as np
#from ocr_pkg.table_detect import detectTable
from tkinter import messagebox
import gui_pkg.exports as exp
#import exports as exp
#from tkinter import ttk
import pytesseract
#import time
from pandastable import Table
from gui_pkg.defaults import _C as cfg
from gui_pkg.img2table import img2df
import logging
from gui_pkg.table_crop import  getHoughLine

#import tktable
#
#tktable.sample_test()
###environment set up
cur_dir = os.getcwd()
#fonts = font.Font(family = "San Francisco")
os.environ['PATH'] = os.environ['PATH'] + ';' + cur_dir +'\\poppler\\bin'
os.environ['PATH'] = os.environ['PATH'] + ';' + cur_dir +'\\ImageMagick-6.9.10-Q8'
os.environ['MAGIC_HOME'] = cur_dir +'\\ImageMagick-6.9.10-Q8'
os.environ['MAGICK_CODER_MODULE_PATH'] = cur_dir +'\\ImageMagick-6.9.10-Q8\\modules\\coders'
pytesseract.pytesseract.tesseract_cmd = cur_dir +'\\Tesseract-OCR\\tesseract.exe'
logging.basicConfig(filename = 'logfile.log',level=logging.INFO, format=cfg.logFORMAT)

# some parameters
root = tk.Tk()
root.title(cfg.MAIN_TITLE)
rect = 10
ocr_indicator = ""
btn_x = np.array(range(14)) *0.045 +0.14 #the x coordinate of the buttons

def get_filedialog(page_no_in = 0):
    """
    this function is called by the "browser" button
    it help to display the pdf pages
    
    Parameters
    ----------
    page_no_in : integer, optional
        the page number for page displaying. The default is 0.

    Returns
    -------
    filename : string
        the name of the file displayed
        to be shown on the header as well.
    """
    global filename
    global page_num_total
    global page_no
    global page_dict
    global pdf_obj
    filepath = filedialog.askopenfile(initialdir =  "/", title = "Select A File", filetype = cfg.processed_ext)
    if filepath is None:
        return
    else:
        filename = filepath
    if os.path.splitext(filename.name)[-1] == '.pdf':
        logging.info("Processing File: {}".format(filename.name))
        pdf_obj = display_pdf(filename.name)
        page_num_total = pdf_obj.count_pdf_pages()
        root.title(filename.name) #the title of the page shown on the header of the windows
        #open_image()
        page_no = 0
        # Display some document
        doc_viewer.display_file(filename.name, page_no+1)
        doc_viewer.place(relx=0, rely=0, relwidth=1, relheight=1)
        page_img.place_forget()
        
        entry.delete(0, tk.END) #clear the page number from previous document
        entry.insert(0,"1")
        label_page['text'] = "/"+str(page_num_total) #it shows total num of page besides the current page num
        initialize() #this funciton is the initialization for all opening file action
        page_dict = {} 
        return filename

def initialize():
    """
    This function is to initialize the the page details when flip to another page
    img_stack is to save the image changing history
    start_x,start_y, curX,curY is the coordinate of the drag drawing rectangle
    they are set to be 0,1 initially
    """
    global img_stack, start_x,start_y, curX, curY
    img_stack = table_crop.Stack()
    hide_buttons(False)
    start_x,start_y, curX,curY = 0,0,1,1
    
#===================Windows GUI setting==========================
    
def img2icon(path_in, length = 20):
    """
    this funciton is to conver img to tkinter icons
    
    Parameters
    ----------
    path_in : string
        the path of the icon's image
    length : integer, optional
        the size of the icon in the GUI windows. The default is 20.

    Returns
    -------
    icon_img : object
        the icons' image object.

    """
    icon_img = path_in
    icon_img = Image.open(icon_img)
    icon_img = icon_img.resize((length,length))
    icon_img = ImageTk.PhotoImage(icon_img)
    return icon_img

def show_buttons():
    """
    this function is to show all the image editing buttons, 
      which has been hidden initially
    """
    btn_list = [button_plus, button_editmode, button_crop, button_return, btn_undo, #5
               button_rot, button_rot2, button_cut, button_eraser, button_line, #5
               button_wand, button_txt, button_exports, button_pdf]
    for coord, btn in zip(cfg.btn_x, btn_list):
        btn.place(relx=coord, relheight=1, relwidth=cfg.btn_width)
        
    chc_1.place_forget()
    chc_2.place_forget()
    button_save.place_forget()
    button_mask.place_forget()
    
def hide_buttons(aux = False):
    """
    this function is to hide all the edit buttons

    Parameters
    ----------
    aux : boolean, optional
        whether is aux editing model. The default is False.
        if true, some of button will be hidden.
    Returns
    -------
    None.

    """
    btn_list = [button_crop, button_return, button_rot, button_rot2,button_cut,
               button_line, button_exports, button_pdf, button_txt, button_wand, btn_undo, button_eraser]
    
    for btn in btn_list:
        if not aux:
            btn.place_forget()
        else:
            if (btn != button_line) & (btn!=btn_undo):
                btn.place_forget()
                chc_1.place(relx=cfg.btn_x[0*2+10], relheight=0.8, relwidth=0.07)
                chc_2.place(relx=cfg.btn_x[1*2+10], relheight=0.8, relwidth=0.07)
                button_save.place(relx=cfg.btn_x[15], relheight=0.8, relwidth=0.07)
                button_mask.place(relx=cfg.btn_x[2*2+10], relheight=0.8, relwidth=0.07)

#===================pages operation==========================
def add_one():
    """
    this function is to add page number 1,
      and display next page 

    """
    global page_no
    #global page_num_total
    global filename
    if page_no + 1 < page_num_total:
        page_no = page_no + 1
        doc_viewer.display_file(filename.name, page_no+1)
        doc_viewer.place(relx=0, rely=0, relwidth=1, relheight=1)
        page_img.place_forget()
        entry.delete(0, tk.END)
        entry.insert(0, str(page_no + 1))
        initialize()
    else:
        pass
    

def minus_one():
    """
    this function is to minus the page number 1
      and display the last page
    """
    global page_no
    #global page_num_total
    global filename
    if page_no -1 >= 0:
        page_no = page_no - 1
        doc_viewer.display_file(filename.name, page_no+1)
        doc_viewer.place(relx=0, rely=0, relwidth=1, relheight=1)
        page_img.place_forget()
        entry.delete(0, tk.END)
        entry.insert(0, str(page_no + 1))
        initialize()
    else:
        pass

def go_to_page(event):
    """
    this function is to skip to the specific page that user key in
    Parameters
    ----------
    event : tkinter even
        presee enter after the user key in the page number.
    """
    global page_no
    page_no = int(entry.get()) - 1
    doc_viewer.display_file(filename.name, page_no+1)
    doc_viewer.place(relx=0, rely=0, relwidth=1, relheight=1)
    page_img.place_forget()
        
#=================image processing=============================
def edit_mode():
    """
    in the edit mode
     the page flip buttons will be hidden
     page editing buttons will be unhidden
    Returns
    -------
    None.

    """
    global page_dict
    show_buttons()
    doc_viewer.place_forget()
    pdf_obj.pdf_page_to_png(page_no)
    page_img.place(relx=0.02, rely=0, relwidth=1, relheight=1)
    logging.info("Processing Page: {}".format(int(page_no)))
    open_image()
    page_dict["Page"+str(page_no)] = img_cur
    
def open_image():
    #size = int(lower_frame.winfo_height()*1.2)
    global img_array
    global img_cur
    global img_stack
    img_array = cv2.imread(cfg.temp_img_path)
    img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    img_stack = table_crop.Stack()
    img_stack.push(img_array.copy())
    img_cur = img_array.copy()
    show_cur_img()

def return_img():
    global img_cur
    img_cur = img_array.copy()
    show_cur_img()


def crop_img():
    global img_cur
    global img_stack
    img_stack.push(img_cur.copy())
    img_cur = get_PerspectiveTransform(img_cur, 5, 100).main_fun()
    logging.info("Auto Straighten Image")
    show_cur_img()
    
#=================some operations=============================
    

def show_cur_img():
    global img
    global ocr_indicator
    img = ImageTk.PhotoImage(img_resize(img_cur)) #img here is the tkinter format image
    page_img.delete("all")
    page_img.create_image(0,0, anchor='nw', image=img)
    page_img.image = img
    ocr_indicator = "img_cur"

def return_prev_img():
    global img
    global ocr_indicator
    global img_stack
    global img_cur
    #img_cur = img_prev.copy()
    img_cur = img_stack.pop()
    logging.info("Undo")
    show_cur_img()


def img_resize(path_or_img):
    """
    This function is to resize the img_cur to suitabble size fits in the current frame

    Parameters
    ----------
    path_in : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    global img_shown_width
    global img_shown_height
    global ratio
    if isinstance(path_or_img, str):
        img_pil = Image.open(path_or_img)
    else:
        img_pil = Image.fromarray(path_or_img)
    wid, hei = img_pil.size
    if (hei > lower_frame.winfo_height()) | (wid > lower_frame.winfo_width()):
        img_shown_width = int(wid/hei*lower_frame.winfo_height()*cfg.img_canvas_multiplier)
        img_shown_height = int(lower_frame.winfo_height()*cfg.img_canvas_multiplier)
        if img_shown_width > lower_frame.winfo_width() :
            rat = lower_frame.winfo_width() / img_shown_width
            img_shown_width = img_shown_width * rat
            img_shown_height = img_shown_height * rat
        img_pil = img_pil.resize((int(img_shown_width), int(img_shown_height)))
        ratio = int(img_shown_width)/img_cur.shape[1]
#        else:
#            img_shown_width  = int(lower_frame.winfo_width()*cfg.img_canvas_multiplier)
#            img_shown_height = int(hei/hei*lower_frame.winfo_width()*cfg.img_canvas_multiplier)
    return img_pil



def rotate_clockwise():
    global img_cur 
    global img_stack
    img_stack.push(img_cur.copy())
    img_cur = img_seg.rotate_back(cfg.rot_unit, img_cur)
    logging.info("Rorate image Clockwise Angle {} degree".format(str(cfg.rot_unit)))
    show_cur_img()

def rotate_counterclockwise():
    global img_cur
    global img_stack
    img_stack.push(img_cur.copy())
    img_cur = img_seg.rotate_back(-cfg.rot_unit, img_cur)
    logging.info("Rorate image Counter Clockwise Angle {} degree".format(str(cfg.rot_unit)))
    show_cur_img()
    
        

def draw_auxiliary_line_byDensity():
    global img_cur
    global m_h
    global m_v
    global hor_lines
    page_img.delete("all")
    show_cur_img()
    m_h = getRowColumnLine(img_cur).horizontal()
    m_v = getRowColumnLine(img_cur).vertical()
    logging.info("Draw Auxiliary Lines By Density")
    try:
        hei, wid, _ = img_cur.shape
    except:
        hei, wid = img_cur.shape
    #here to draw the lines
    #hor_lines = []
    for n, hor in enumerate(m_h):
        #page_img.create_line(0,hor[1]*ratio, wid*ratio, hor[1]*ratio,fill = "green", activewidth=3)
        id = page_img.create_line(0,hor[1]*ratio, wid*ratio, hor[1]*ratio,fill = "green", activewidth=3, tags=('hor', "hor_{}".format(n)))
        print(id)
    
    for n, vert in enumerate(m_v):
        id = page_img.create_line(vert[1]*ratio, 0, vert[1]*ratio, hei*ratio, fill = "blue", activewidth=3,tags=('vert', "vert{}".format(n)))
        print(id)
    hide_buttons(True)
    page_img.bind( "<Double-1>", lambda x: get_lines(x))

def get_lines(event):
    print(page_img.find_closest(event.x, event.y))
    if page_img.find_closest(event.x, event.y) != (2,):
        page_img.delete(page_img.find_closest(event.x, event.y))

   
    
def draw_auxiliary_line_byHough():
    global img_cur
    global m_h
    global m_v
    try:
        hei, wid, _ = img_cur.shape
    except:
        hei, wid = img_cur.shape
    m_h, m_v = getHoughLine(img_cur).run()
    logging.info("Draw Auxiliary Lines By Hough Lines")
    page_img.delete("all")
    show_cur_img()
    for vet in m_v:
        id = page_img.create_line(vet*ratio, 0, vet*ratio, hei*ratio, fill = "blue", activewidth=3)
        print(id)
    hide_buttons(True)
    for hor in m_h:
        id = page_img.create_line(0,hor*ratio, wid*ratio, hor*ratio,fill = "green", activewidth=3)
        print(id)
    
def show_mask():
    global img_cur
    global img_stack
    logging.info("Checking Image Mask")
    img_stack.push(img_cur.copy())
    img_cur = getHoughLine(img_cur).getMask()
    show_cur_img()
    return



def del_line(linename):
    global line
    line = linename
    print("delete",linename)
    page_img.dtag('all', 'horSelected')
    page_img.addtag('horSelected', 'withtag', line)
    page_img.delete('horSelected')
    page_img.delete(line)



def on_move_press(event):
    global curX, curY
    curX, curY = (event.x, event.y)
    page_img.coords(rect, start_x, start_y, curX, curY)
    

def on_button_release(event):
    print(start_x, start_y, curX, curY)
    pass

def on_button_press(event, **kwargs):
    global start_x
    global start_y
    global rect
    start_x = event.x
    start_y = event.y
    #rect = page_img.create_rectangle(0, 0, 1,1, fill = "", outline="#e01919")
    #page_img.delete(rect)
    
    if rect:
        page_img.delete(rect)
        
    #rect = page_img.create_rectangle(0, 0, 1,1, fill = "red", outline="#e01919", alpha = 0.5)
    rect = create_rectangle(0, 0, 1,1, fill = "red", outline="#e01919", alpha = 0.5)


def create_rectangle(x1, y1, x2, y2, **kwargs):
    if 'alpha' in kwargs:
        alpha = int(kwargs.pop('alpha') * 255)
        fill = kwargs.pop('fill')
        fill = root.winfo_rgb(fill) + (alpha,)
    return page_img.create_rectangle(x1, y1, x2, y2, **kwargs)


def crop_manul():
    global img_cur
    global img_stack
    img_stack.push(img_cur.copy())
    if len(img_array)>0:
        hei,wid = img_cur.shape[0], img_cur.shape[1]
        print("img wid",wid, "hei", hei)
        print("img shown width", img_shown_width)
        print("img shown height", img_shown_height)
        logging.info("Crop Image to Width {} Height {}".format(wid, hei))
        rate = wid/img_shown_width
        start_x_img = rate * start_x
        start_y_img = rate * start_y
        cur_x_img = rate * curX
        cur_y_img = rate * curY
        if len(img_cur) == 3:
            img_cur = img_cur[int(start_y_img):int(cur_y_img),int(start_x_img):int(cur_x_img), :]
        else:
            img_cur = img_cur[int(start_y_img):int(cur_y_img),int(start_x_img):int(cur_x_img)]
        show_cur_img()
    else:
        pass

def magic_stick():
    global img_no_border
    global ocr_indicator
    global img_cur
    global img_stack
    #img_no_border = table_crop.rm_lines(img_cur)
    img_stack.push(img_cur.copy())
    img_cur = table_crop.rm_lines(img_cur)
    logging.info("Auto Table Lines Removal")
    show_cur_img()



#===========================eraser=============================
def eraser():
    global ocr_indicator
    global img_cur
    global img_stack
    img_stack.push(img_cur.copy())
    if len(img_array)>0:
        hei,wid = img_cur.shape[0], img_cur.shape[1]
        print("img wid",wid, "hei", hei)
        print("img shown width", img_shown_width)
        print("img shown height", img_shown_height)
        
        rate = wid/img_shown_width
        start_x_img = rate * start_x
        start_y_img = rate * start_y
        cur_x_img = rate * curX
        cur_y_img = rate * curY

        if len(img_cur.shape) == 3:
            img_cur[int(start_y_img):int(cur_y_img),int(start_x_img):int(cur_x_img), :]=255
        else:
            img_cur[int(start_y_img):int(cur_y_img),int(start_x_img):int(cur_x_img)]=255
        show_cur_img()
        logging.info("Remove Area {},{},{},{}".format(start_x_img,start_y_img, cur_x_img, cur_y_img))
    else:
        return
    
    
#===========================================================export functions============================================================
def img2txt():
    global ocr_indicator
    name = filedialog.asksaveasfile(mode='w',defaultextension=".txt")
    if name is None:
        return
    if ocr_indicator == "img_cur":
        print("ocr current img")
        exp.page_exports(img_cur, name.name)
    else:
        print("img remove border")
        exp.page_exports(img_no_border, name.name)
    messagebox.showinfo("title???", "Finish!")
    

def img2pdf():
    name = filedialog.asksaveasfile(mode='w',defaultextension=".pdf")
    if name is None:
        return
    exp.page_exports(img_cur, name.name).__to_pdf__()
    messagebox.showinfo("", "Finish!")


def img2excel():
    global df
    global page_width
    
    try:
        df = exp.page_exports(img_cur, filename.name).img2df(filename.name,page_no, 
                             area = [start_y, start_x,curY,curX], shown_wid = img_shown_width)[0]
        print("tabula result: ",len(df))
    except:
        df = None
        print("fail from tabula")
    try:
        if df.empty:
            df = img2df(img_cur) #the col by col extraction function
    except:
        if not df:
            df = img2df(img_cur)
    #page_width = pdf_obj.get_page_width(page_no)
    #df = exp.page_exports(img_cur).crop_page(filename.name, page_no, page_width,img_shown_width,start_x, start_y, curX, curY)
    pop_table = tk.Toplevel(height = 500, width = 700)
    pop_table.wm_title("Table output")
    logging.info("Converting to Table")
    #pop_frame = tk.Label(pop_table)
    pt = Table(pop_table, dataframe = df) #,showtoolbar=True
    pt.show()
    #pt.place(relx=0, rely=0, relwidth=1, relheight=0.8)

    return
#===================================pop up windows=============================================
def popup_entrybox():
    global output_txt
    popup_window = tk.Toplevel(height = 500, width = 700)
    popup_window.wm_title("OCR output")

    l = tk.Label(popup_window, text="OCR output:")
    l.place(relx=0.1, rely=0, relwidth=1, relheight=0.05, anchor='n')
    
    back = tk.Frame(master = popup_window, width = 800, height = 600)
    back.place(relx=0.5, rely=0.05, relwidth=1, relheight=0.95, anchor='n')
    # if ocr_indicator == "img_cur":
        # print("ocr current img")
    try:
        text = pdf_obj.extrac_text_from_page(page_no) #use tika module to extract content
        
        if not text:
            text = exp.page_exports(img_cur, filename.name).img2str(img_cur)
        else:
            if (len(text) < 5) or text.isspace():
                text = exp.page_exports(img_cur, filename.name).img2str(img_cur)
    except:
        text = exp.page_exports(img_cur, filename.name).img2str(img_cur)
    # else:
    #     text = pdf_obj.extrac_text_from_page(page_no)
    #     if (len(text) < 5) or text.isspace():
    #         print("OCRing img remove border")
    #         text = pytesseract.image_to_string(img_no_border)
    #         if text.isspace():
    #             text = pytesseract.image_to_string(img_no_border, config = '--psm 6')
    output_txt = tk.Text(back)
    #output_txt.delete(0, tk.END)
    output_txt.insert(tk.END, text)
    output_txt.place(relx=0.5, rely=0, relwidth=0.9, relheight=0.9, anchor='n')
    save_out_btn = tk.Button(back, text = "Save", font =4, command= lambda: create_save())
    save_out_btn.place(relx = 0.5, rely=0.92, relwidth=0.15, relheight=0.06, anchor='n')
    remove_space_btn = tk.Button(back, text = "Trim", font = 4, command = lambda: remove_space())
    remove_space_btn.place(relx = 0.3, rely=0.92, relwidth=0.15, relheight=0.06, anchor='n')
    
def create_save():
    name = filedialog.asksaveasfile(mode='w',defaultextension=".txt")
    if name is None:
        return
    file = open(name.name, 'w', encoding = 'utf8')
    file.write(output_txt.get(1.0, "end-1c"))
    file.close()
    messagebox.showinfo("", "Finish!")
    
def remove_space():
    text_inEntry = output_txt.get(1.0, "end-1c").split("\n")
    text_inEntry = [substr for substr in text_inEntry if (substr != "") & (not substr.isspace())]
    text_inEntry = "\n".join(text_inEntry)
    output_txt.delete(1.0, "end-1c")
    output_txt.insert(1.0, text_inEntry)
    
#===========================filters and other img processing=========================
def GussianBlur():
    global img_cur
    global img_stack
    img_stack.push(img_cur.copy())
    img_cur = cv2.GaussianBlur(img_cur,(5,5),0)
    show_cur_img()

def erode_img():
    global img_cur
    global img_stack
    img_stack.push(img_cur.copy())
    kernel = np.ones((2,2),np.uint8)
    if len(img_cur.shape) == 3:
        img_cur = cv2.cvtColor(img_cur, cv2.COLOR_BGR2GRAY)
    img_cur = cv2.erode(img_cur,kernel,iterations = 1)
    show_cur_img()
    
def dilate_img():
    global img_cur
    global img_stack
    img_stack.push(img_cur.copy())
    kernel = np.ones((2,2),np.uint8)
    if len(img_cur.shape) == 3:
        img_cur = cv2.cvtColor(img_cur, cv2.COLOR_BGR2GRAY)
    img_cur = cv2.dilate(img_cur,kernel,iterations = 1)
    show_cur_img()



#===========================rotate img=========================
def orientation_det():
    orient = pytesseract.image_to_osd(img_cur)
    messagebox.showinfo("", orient)

def rot_clockwise():
    global img_cur
    global img_stack
    #img_prev = img_cur.copy()
    img_stack.push(img_cur.copy())
    img_cur = cv2.rotate(img_cur,cv2.ROTATE_90_CLOCKWISE)
    show_cur_img()

def rot_Counterclockwise():
    global img_cur
    global img_stack
    img_stack.push(img_cur.copy())
    img_cur = cv2.rotate(img_cur,cv2.ROTATE_90_COUNTERCLOCKWISE)
    show_cur_img()

#=========================help index==========================================
def help_index():
    popup_window = tk.Toplevel(height = 753, width = 500)
    popup_window.wm_title("Help Index")

    l = tk.Label(popup_window, text="We Are Always Ready for Help")
    l.place(relx=0.1, rely=0, relwidth=1, relheight=0.05)#, anchor='n'
    
    help_pic_cns = tk.Canvas(popup_window, highlightthickness=0, bg="white") # bd=0,
    help_pic_cns.delete("all")
    
    
    img = ImageTk.PhotoImage(Image.open(cfg.HELP_IDX))
    help_pic_cns.create_image(0,0, anchor='nw', image=img)
    help_pic_cns.image = img    
    help_pic_cns.place(relx=0, rely=0, relwidth=1, relheight=1)#, anchor='n'
    #output_txt.delete(0, tk.END)
    


#======================Windows settings==============================================
canvas = tk.Canvas(root, height=cfg.HEIGHT, width=cfg.WIDTH, bg = "white")
canvas.pack()
#====================================================================================

frame = tk.Frame(root, bg='white', bd=10)
frame.place(relx=0.5, rely=0, relwidth=1, relheight=0.07, anchor='n')

#====================================================================================

menubar = tk.Menu(root)
filemenu = tk.Menu(menubar,  background= "#e0ecde",selectcolor = "#68b2a0", tearoff=0)
open_icon = img2icon(cfg.OPEN_ICON)
exit_icon = img2icon(cfg.EXIT_ICON)

save_icon = cfg.ICON_DIR+"\\save icon.png"
save_icon = img2icon(save_icon)

filemenu.add_command(label=" Open", background= "white", font = 5, image = open_icon, compound="left")
filemenu.add_command(label=" Save", background= "#e0ecde", font = 5, image = save_icon, compound="left",)
filemenu.add_separator()
filemenu.add_command(label=" Exit", background= "#e0ecde", font = 5, image = exit_icon, compound="left", command=root.quit)
#filemenu['font'] = fonts                 
menubar.add_cascade(label="File", background= "#e0ecde", font = 5, menu=filemenu)
#====================================================================================
helpmenu = tk.Menu(menubar, tearoff=0,   background= "#f5f5f5")
helpmenu.add_command(label="Help", command= lambda: help_index())
helpmenu.add_command(label="More Services")
menubar.add_cascade(label="Help", menu=helpmenu)
#helpmenu['font'] = fonts                 
#====================================================================================
filtermenu = tk.Menu(menubar, tearoff=0)
filtermenu.add_command(label="MediumBlur")
filtermenu.add_command(label="GussianBlur", command = lambda : GussianBlur())
filtermenu.add_command(label="Erosion", command = lambda : erode_img())
filtermenu.add_command(label="Dilation", command = lambda : dilate_img())

menubar.add_cascade(label="Filters", menu=filtermenu)
#====================================================================================
operationmenu = tk.Menu(menubar, tearoff=0)
operationmenu.add_command(label="Eraser", command = lambda: eraser())
operationmenu.add_command(label="Fine Liner")
operationmenu.add_command(label="Corner Picker")
operationmenu.add_command(label="Border Removal")

menubar.add_cascade(label="Operations", menu=operationmenu)
#====================================================================================
page_orgmenue = tk.Menu(menubar, tearoff=0)
page_orgmenue.add_command(label = "Rotate Clockwise(90°)", command= lambda:rot_clockwise())
page_orgmenue.add_command(label = "Rotate Counter Clockwise(90°)", command = lambda: rot_Counterclockwise())
page_orgmenue.add_command(label="Orientation Detection", command = lambda: orientation_det())

menubar.add_cascade(label="Page Organize", menu=page_orgmenue)
menubar.config(selectcolor = "#68b2a0", bd=0)
                              
#=======================================buttons on top=============================================

get_file = img2icon(cfg.FOLDER_ICON, 32)
file_load_button = tk.Button(frame, text="", font=8, border="0", image = get_file,command= lambda: get_filedialog(0), bg = "white")
file_load_button.place(relx=0, relheight=1, relwidth=cfg.btn_width)
file_load_button['border'] = "0"

entry = tk.Entry(frame, font=40)
entry.place(relx=0.07,relwidth=0.03, relheight=1)
entry.bind("<Return>", go_to_page)

minus = img2icon(cfg.MINUS_ICON, 32)
button_minues = tk.Button(frame, text = "", font = 8,bg = "white", border= "0",image = minus, command = lambda: minus_one())
button_minues.place(relx=0.035, relheight=1, relwidth=cfg.btn_width)

label_page = tk.Label(frame, bg = "white")
label_page.config(font=6)
label_page.place(relx = 0.105, relwidth=0.03, relheight=1)


plus_icon = img2icon(cfg.PLUS_ICON, 32)
button_plus = tk.Button(frame, text = "", font = 8, bg = "white", bd = 0.5, border= "0",image = plus_icon,command = lambda: add_one())
button_plus.place(relx=cfg.btn_x[0], relheight=1, relwidth=cfg.btn_width)

edit_mode_icon = img2icon(cfg.EDIT_MODE_ICON, 32)
button_editmode = tk.Button(frame, text = "", font = 8, bg = "white", bd = 0.5, border= "0",image = edit_mode_icon, command = lambda: edit_mode())
button_editmode.place(relx=cfg.btn_x[1], relheight=1, relwidth=cfg.btn_width)

crop = img2icon(cfg.CROP_ICON,32)
button_crop = tk.Button(frame, text = "", font = 8, bg = "white", image = crop, border = "0",command = lambda: crop_img())
button_crop.place(relx=cfg.btn_x[2], relheight=1, relwidth=cfg.btn_width)

return_icon = img2icon(cfg.UNDO_ICON, 32)
button_return = tk.Button(frame, text = "", image = return_icon, bg = "white",font = 8, border = "0",command = lambda: return_img())
button_return.place(relx=cfg.btn_x[3], relheight=1, relwidth=cfg.btn_width)

undo_icon = img2icon(cfg.RETURN_ICON, 32)
btn_undo = tk.Button(frame, text="", image = undo_icon, bg="white", font=8, border="0",command=lambda: return_prev_img())
btn_undo.place(relx=cfg.btn_x[4], relheight=1, relwidth=cfg.btn_width)

rot1 = img2icon(cfg.ROTATE1,32)
button_rot = tk.Button(frame, text = "↷", font = 9, bg = "white",border="0", image = rot1, command = lambda: rotate_clockwise())
button_rot.place(relx=cfg.btn_x[5], relheight=1, relwidth=cfg.btn_width)

rot2 = img2icon(cfg.ROTATE2,32)
button_rot2 = tk.Button(frame, text = "", font = 9, bg = "white", border="0", image=rot2 ,command = lambda: rotate_counterclockwise())
button_rot2.place(relx=cfg.btn_x[6], relheight=1, relwidth=cfg.btn_width)

cut_icon = img2icon(cfg.SCISSORS,32)
button_cut = tk.Button(frame, text = "cut", font = 9, bg = "white", image = cut_icon,border="0", command = lambda: crop_manul())
button_cut.place(relx=cfg.btn_x[7], relheight=1, relwidth=cfg.btn_width)

eraser_icon = img2icon(cfg.ERASER,32)
button_eraser = tk.Button(frame, text = "cut", font = 9, bg = "white", image = eraser_icon,border="0", command = lambda: eraser())
button_eraser.place(relx=cfg.btn_x[8], relheight=1, relwidth=cfg.btn_width)

lines = img2icon(cfg.PENCIL,32)
button_line = tk.Button(frame, text = "", font = 9, bg = "white", image = lines,border = "0", command = lambda :draw_auxiliary_line_byDensity()) 
button_line.place(relx=cfg.btn_x[9], relheight=1, relwidth=cfg.btn_width)

magic_wand = img2icon(cfg.WAND,32)
button_wand = tk.Button(frame, text = "", font = 9, bg = "white", image = magic_wand, border = "0", command = lambda :magic_stick()) 
button_wand.place(relx=cfg.btn_x[10], relheight=1, relwidth=cfg.btn_width)

exports_txt = img2icon(cfg.TXT_ICON, 32)
button_txt = tk.Button(frame, text = "", font = 9, bg = "white", image = exports_txt, border = "0", command = lambda: popup_entrybox())
button_txt.place(relx=cfg.btn_x[11], relheight=1, relwidth=cfg.btn_width)

exports_excel = img2icon(cfg.excel_icon,32)
button_exports = tk.Button(frame, text = "", font = 9, bg = "white", image = exports_excel, border = "0", command = lambda :img2excel()) 
button_exports.place(relx=cfg.btn_x[12], relheight=1, relwidth=cfg.btn_width)

exports_pdf = img2icon(cfg.PDF_ICON, 32)
button_pdf = tk.Button(frame, text = "", font = 9, bg = "white", image = exports_pdf, border = "0", command=lambda: img2pdf())
button_pdf.place(relx=cfg.btn_x[13], relheight=1, relwidth=cfg.btn_width)

savebtn = img2icon(cfg.savebtnBlue, 32)
button_save = tk.Button(frame, text = "", font = 9, bg = "white", image = savebtn, border="0", command=lambda: show_buttons()) 

maskbtn = img2icon(cfg.mask, 32)
button_mask = tk.Button(frame, text = "", font=9,bg="white", image = maskbtn, border="0", command = lambda: show_mask())

chc_1 = tk.Radiobutton(frame, text = cfg.choice[0][0], indicatoron = 0, value = cfg.choice[0][1], command=lambda: draw_auxiliary_line_byDensity()) #by density
chc_2 = tk.Radiobutton(frame, text = cfg.choice[1][0], indicatoron = 0, value = cfg.choice[1][1], command=lambda: draw_auxiliary_line_byHough())  #by hough line


#====================================================================================

lower_frame = tk.Frame(root, bg='green',  border= "0",colormap="new")
lower_frame.place(relx=0, rely=0.06, relwidth=1, relheight=0.90, anchor='nw')


doc_viewer = DocViewer(lower_frame)
doc_viewer.place(relx=0, rely=0, relwidth=1, relheight=1)

page_img = tk.Canvas(lower_frame, bg="green", highlightthickness=0, bd = "0.5") # bd=0,
page_img.bind("<ButtonPress-1>", on_button_press)
page_img.bind("<B1-Motion>", on_move_press)
page_img.bind("<ButtonRelease-1>", on_button_release)

# Start Tk's event loop
root.config(menu=menubar, background = 'white', border = "0") #, cursor = "mouse"
root.mainloop()


