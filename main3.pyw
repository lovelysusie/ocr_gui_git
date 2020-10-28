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
from ocr_pkg.table_detect import detectTable
from tkinter import messagebox
import gui_pkg.exports as exp
from tkinter import ttk
import pytesseract
import time
from pandastable import Table
from gui_pkg.defaults import _C as cfg
from gui_pkg.img2table import img2df
#import tktable
#
#tktable.sample_test()
cur_dir = os.getcwd()
#fonts = font.Font(family = "San Francisco")
os.environ['PATH'] = os.environ['PATH'] + ';' + cur_dir +'\\poppler\\bin'
os.environ['PATH'] = os.environ['PATH'] + ';' + cur_dir +'\\ImageMagick-7.0.8-Q16'
os.environ['MAGIC_HOME'] = cur_dir +'\\ImageMagick-7.0.8-Q16'
os.environ['MAGICK_CODER_MODULE_PATH'] = cur_dir +'\\ImageMagick-7.0.8-Q16\\modules\\coders'
pytesseract.pytesseract.tesseract_cmd = cur_dir +'\\Tesseract-OCR\\tesseract.exe'

# some parameters
root = tk.Tk()
root.title(cfg.MAIN_TITLE)
rect = 10
img_canvas_multiplier = 1
ocr_indicator = ""

def get_filedialog(page_no_in = 0):
    global filename
    global page_num_total
    global page_no
    global page_dict
    global pdf_obj
    filepath = filedialog.askopenfile(initialdir =  "/", title = "Select A File", filetype =
        (("Portable Document Format","*.pdf"),("all files","*.*")))
    if filepath is None:
        return
    else:
        filename = filepath
    pdf_obj = display_pdf(filename.name)
    page_num_total = pdf_obj.count_pdf_pages()
    root.title(filename.name)
    #open_image()
    page_no = 0
    # Display some document
    v.display_file(filename.name, page_no+1)
    v.place(relx=0, rely=0, relwidth=1, relheight=1)
    page_img.place_forget()
    
    entry.delete(0, tk.END)
    entry.insert(0,"1")
    label_page['text'] = "/"+str(page_num_total) #it shows total num of page besides the current page num
    hide_buttons()
    page_dict = {} 
    return filename

def img2icon(path_in, lenght = 20):
    icon_img = path_in
    icon_img = Image.open(icon_img)
    icon_img = icon_img.resize((lenght,lenght))
    icon_img = ImageTk.PhotoImage(icon_img)
    return icon_img

#===================pages operation==========================
def add_one():
    global page_no
    #global page_num_total
    global filename
    if page_no + 1 < page_num_total:
        page_no = page_no + 1
        v.display_file(filename.name, page_no+1)
        v.place(relx=0, rely=0, relwidth=1, relheight=1)
        page_img.place_forget()
        entry.delete(0, tk.END)
        entry.insert(0, str(page_no + 1))
        hide_buttons()
    else:
        pass
    

def minus_one():
    global page_no
    #global page_num_total
    global filename
    if page_no -1 >= 0:
        page_no = page_no - 1
        v.display_file(filename.name, page_no+1)
        v.place(relx=0, rely=0, relwidth=1, relheight=1)
        page_img.place_forget()
        entry.delete(0, tk.END)
        entry.insert(0, str(page_no + 1))
        hide_buttons()
    else:
        pass

def go_to_page(event):
    global page_no
    page_no = int(entry.get()) - 1
    v.display_file(filename.name, page_no+1)
    v.place(relx=0, rely=0, relwidth=1, relheight=1)
    page_img.place_forget()
        
#=================image processing=============================
def edit_mode():
    #global page_img
    global page_dict
    show_buttons()
    v.place_forget()
    pdf_obj.pdf_page_to_png(page_no)
    
    page_img.place(relx=0.1, rely=0, relwidth=1, relheight=1)

    open_image()
    page_dict["Page"+str(page_no)] = img_cur
    
def open_image():
    #size = int(lower_frame.winfo_height()*1.2)
    global img_array
    global img_cur
    global img_prev
    img_array = cv2.imread(cfg.temp_img_path)
    img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    img_prev = img_array.copy()
    img_cur = img_array.copy()
    show_cur_img()


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
    global img_prev
    global img_cur
    img_cur = img_prev.copy()
    show_cur_img()


def img_resize(path_in):
    global img_shown_width
    global img_shown_height
    if isinstance(path_in, str):
        img_pil = Image.open(path_in)
    else:
        img_pil = Image.fromarray(path_in)
    wid, hei = img_pil.size
    if (hei > lower_frame.winfo_height()) | (wid > lower_frame.winfo_width()):
        img_shown_width = int(wid/hei*lower_frame.winfo_height()*img_canvas_multiplier)
        img_shown_height = int(lower_frame.winfo_height()*img_canvas_multiplier)
        if img_shown_width > lower_frame.winfo_width() :
            rat = lower_frame.winfo_width() / img_shown_width
            img_shown_width = img_shown_width * rat
            img_shown_height = img_shown_height * rat
        img_pil = img_pil.resize((int(img_shown_width), int(img_shown_height)))
#        else:
#            img_shown_width  = int(lower_frame.winfo_width()*img_canvas_multiplier)
#            img_shown_height = int(hei/hei*lower_frame.winfo_width()*img_canvas_multiplier)
    return img_pil


def rotate_clockwise():
    global img_cur 
    global img_prev
    img_prev = img_cur.copy()
    img_cur = img_seg.rotate_back(cfg.rot_unit, img_cur)
    show_cur_img()

def rotate_counterclockwise():
    global img_cur
    global img_prev
    img_prev = img_cur.copy()
    img_cur = img_seg.rotate_back(-cfg.rot_unit, img_cur)
    show_cur_img()
    
        
def hide_buttons():
    btn_list = [button_crop, button_return, button_rot, button_rot2,button_cut,
               button_line, button_exports, button_pdf, button_txt, button_wand, btn_undo]
    for btn in btn_list:
        btn.place_forget()
    
    
def show_buttons():
    button_crop.place(relx=0.37, relheight=1, relwidth=0.04)
    button_return.place(relx=0.42, relheight=1, relwidth=0.04)
    button_rot.place(relx=0.47, relheight=1, relwidth=0.04)
    button_rot2.place(relx=0.52, relheight=1, relwidth=0.04)
    button_cut.place(relx=0.57, relheight=1, relwidth=0.06)
    button_line.place(relx=0.625, relheight=1, relwidth=0.06)
    button_pdf.place(relx=0.83, relheight=1, relwidth=cfg.btn_width)
    button_exports.place(relx=0.785, relheight=1, relwidth=cfg.btn_width)
    button_txt.place(relx=0.73, relheight=1, relwidth=cfg.btn_width)
    button_wand.place(relx=0.675, relheight=1, relwidth=0.06)
    btn_undo.place(relx=0.3, relheight=1, relwidth=cfg.btn_width)

    
def return_img():
    global img_cur
    img_cur = img_array.copy()
    #size = int(lower_frame.winfo_height()*1.2)
    show_cur_img()


def crop_img():
    global img_cur
    global img_prev
    #size = int(lower_frame.winfo_height()*1.2)
    img_prev = img_cur.copy()
    img_cur = get_PerspectiveTransform(img_cur, 5, 100).main_fun()
    show_cur_img()


def draw_auxiliary_line():
    m_h = getRowColumnLine(img_cur).horizontal()
    m_v = getRowColumnLine(img_cur).vertical()
    img_w_line = table_crop.draw_auxiliary_line(img_cur,m_h,"h" )
    img_w_line = table_crop.draw_auxiliary_line(img_w_line,m_v,"v" )
    img = ImageTk.PhotoImage(img_resize(img_w_line))
    page_img.delete("all")
    page_img.create_image(0, 0, anchor='nw', image=img)
    page_img.image = img


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
    global img_prev
    img_prev = img_cur.copy()
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
    mask, joint = detectTable(img_cur).run()
    kernel = np.ones((2, 2), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations =2)
    gray_img = cv2.cvtColor(img_cur, cv2.COLOR_BGR2GRAY)
    img_no_border = cv2.add(gray_img, mask)
    img = ImageTk.PhotoImage(img_resize(img_no_border))
    page_img.delete("all")
    page_img.create_image(0,0, anchor='nw', image=img)
    page_img.image = img
    ocr_indicator = "img_no_border"
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
    #exp.page_exports(img_cur, name.name)
    pdf = pytesseract.image_to_pdf_or_hocr(img_cur, extension='pdf')
    f = open(name.name, 'w+b')
    f.write(pdf)
    f.close()
    messagebox.showinfo("", "Finish!")


def img2excel():
#    name = filedialog.asksaveasfile(mode='w',defaultextension=".xlsx")
#    if name is None:
#        return
#    time.sleep(10)
#    messagebox.showinfo("", "Finish!")
    global df
    global page_width
    
    df = exp.page_exports(img_cur, filename.name).img2df(filename.name,page_no)
    try:
        if df.empty:
            df = img2df(img_cur)
    except:
        if not df:
            df = img2df(img_cur)
    #page_width = pdf_obj.get_page_width(page_no)
    #df = exp.page_exports(img_cur).crop_page(filename.name, page_no, page_width,img_shown_width,start_x, start_y, curX, curY)
    pop_table = tk.Toplevel(height = 500, width = 700)
    pop_table.wm_title("Table output")
    
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
    if ocr_indicator == "img_cur":
        print("ocr current img")
        text = pdf_obj.extrac_text_from_page(page_no)
        if (len(text) < 5) or text.isspace():
            text = pytesseract.image_to_string(img_cur)
            if text.isspace():
                text = pytesseract.image_to_string(img_cur, config = '--psm 6')
    else:
        text = pdf_obj.extrac_text_from_page(page_no)
        if (len(text) < 5) or text.isspace():
            print("OCRing img remove border")
            text = pytesseract.image_to_string(img_no_border)
            if text.isspace():
                text = pytesseract.image_to_string(img_no_border, config = '--psm 6')

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
    global img_prev
    img_prev = img_cur.copy()
    img_cur = cv2.GaussianBlur(img_cur,(5,5),0)
    show_cur_img()

def erode_img():
    global img_cur
    global img_prev
    img_prev = img_cur.copy()
    kernel = np.ones((2,2),np.uint8)
    if len(img_cur.shape) == 3:
        img_cur = cv2.cvtColor(img_cur, cv2.COLOR_BGR2GRAY)
    img_cur = cv2.erode(img_cur,kernel,iterations = 1)
    show_cur_img()
    
def dilate_img():
    global img_cur
    global img_prev
    img_prev = img_cur.copy()
    kernel = np.ones((2,2),np.uint8)
    if len(img_cur.shape) == 3:
        img_cur = cv2.cvtColor(img_cur, cv2.COLOR_BGR2GRAY)
    img_cur = cv2.dilate(img_cur,kernel,iterations = 1)
    show_cur_img()

#===========================eraser=============================
def eraser():
    global img_no_border
    global ocr_indicator
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
        if len(img_cur) == 3:
            img_no_border[int(start_y_img):int(cur_y_img),int(start_x_img):int(cur_x_img), :]=255
        else:
            img_no_border[int(start_y_img):int(cur_y_img),int(start_x_img):int(cur_x_img)]=255
        img = ImageTk.PhotoImage(img_resize(img_no_border))
        page_img.delete("all")
        page_img.create_image(0,0, anchor='nw', image=img)
        page_img.image = img
        ocr_indicator =  "img_no_border"
    else:
        pass
    

#===========================rotate img=========================
def orientation_det():
    orient = pytesseract.image_to_osd(img_cur)
    messagebox.showinfo("", orient)

def rot_clockwise():
    global img_cur
    global img_prev
    img_prev = img_cur.copy()
    img_cur = cv2.rotate(img_cur,cv2.ROTATE_90_CLOCKWISE)
    show_cur_img()

def rot_Counterclockwise():
    global img_cur
    global img_prev
    img_prev = img_cur.copy()
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
    
    
    img = ImageTk.PhotoImage(Image.open(cfg.icon_folder+"\\delight.jpg"))
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
page_orgmenue.add_command(label = "Rorate Clockwise(90°)", command= lambda:rot_clockwise())
page_orgmenue.add_command(label = "Rorate Counter Clockwise(90°)", command = lambda: rot_Counterclockwise())
page_orgmenue.add_command(label="Orientation Detection", command = lambda: orientation_det())

menubar.add_cascade(label="Page Orgnize", menu=page_orgmenue)
menubar.config(selectcolor = "#68b2a0", bd=0)
                              
#=======================================buttons on top=============================================

get_file = img2icon(cfg.FOLDER_ICON, 32)
file_load_button = tk.Button(frame, text="", font=8, border="0", image = get_file,command= lambda: get_filedialog(0), bg = "white")
file_load_button.place(relx=0, relheight=1, relwidth=cfg.btn_width)
file_load_button['border'] = "0"

minus = img2icon(cfg.MINUS_ICON, 32)
button_minues = tk.Button(frame, text = "", font = 8,bg = "white", border= "0",image = minus, command = lambda: minus_one())
button_minues.place(relx=0.035, relheight=1, relwidth=cfg.btn_width)

entry = tk.Entry(frame, font=40)
entry.place(relx=0.07,relwidth=0.03, relheight=1)
entry.bind("<Return>", go_to_page)

label_page = tk.Label(frame, bg = "white")
label_page.config(font=6)
label_page.place(relx = 0.105, relwidth=0.03, relheight=1)

plus_icon = img2icon(cfg.PLUS_ICON, 32)
button_plus = tk.Button(frame, text = "", font = 8, bg = "white", bd = 0.5, border= "0",image = plus_icon,command = lambda: add_one())
button_plus.place(relx=0.14, relheight=1, relwidth=cfg.btn_width)

edit_mode_icon = img2icon(cfg.EDIT_MODE_ICON, 32)
button_editmode = tk.Button(frame, text = "", font = 8, bg = "white", bd = 0.5, border= "0",image = edit_mode_icon, command = lambda: edit_mode())
button_editmode.place(relx=0.175, relheight=1, relwidth=cfg.btn_width)

crop = img2icon(cfg.CROP_ICON,32)
button_crop = tk.Button(frame, text = "", font = 8, bg = "white", image = crop, border = "0",command = lambda: crop_img())
button_crop.place(relx=0.21, relheight=1, relwidth=cfg.btn_width)

return_icon = img2icon(cfg.RETURN_ICON, 32)
button_return = tk.Button(frame, text = "", image = return_icon, bg = "white",font = 8, command = lambda: return_img())
button_return.place(relx=0.245, relheight=1, relwidth=cfg.btn_width)
button_return['border'] = "0"

undo_icon = img2icon(cfg.UNDO_ICON, 32)
btn_undo = tk.Button(frame, text="", image = undo_icon, bg="white", font=8, border="0",command=lambda: return_prev_img())
btn_undo.place(relx=0.3, relheight=1, relwidth=cfg.btn_width)

rot1 = img2icon(cfg.ROTATE1,32)
button_rot = tk.Button(frame, text = "↷", font = 9, bg = "white",border="0", image = rot1, command = lambda: rotate_clockwise())
button_rot.place(relx=0.47, relheight=1, relwidth=cfg.btn_width)

rot2 = img2icon(cfg.ROTATE2,32)
button_rot2 = tk.Button(frame, text = "", font = 9, bg = "white", border="0", image=rot2 ,command = lambda: rotate_counterclockwise())
button_rot2.place(relx=0.52, relheight=1, relwidth=cfg.btn_width)

cut_icon = img2icon(cfg.SCISSORS,32)
button_cut = tk.Button(frame, text = "cut", font = 9, bg = "white", image = cut_icon,border="0", command = lambda: crop_manul())
button_cut.place(relx=0.57, relheight=1, relwidth=cfg.btn_width)

lines = img2icon(cfg.PENCIL,32)
button_line = tk.Button(frame, text = "", font = 9, bg = "white", image = lines,border = "0", command = lambda :draw_auxiliary_line()) 
button_line.place(relx=0.625, relheight=1, relwidth=cfg.btn_width)


magic_wand = img2icon(cfg.WAND,32)
button_wand = tk.Button(frame, text = "", font = 9, bg = "white", image = magic_wand, border = "0", command = lambda :magic_stick()) 
button_wand.place(relx=0.675, relheight=1, relwidth=0.06)

exports_txt = img2icon(cfg.TXT_ICON, 32)
button_txt = tk.Button(frame, text = "", font = 9, bg = "white", image = exports_txt, border = "0", command = lambda: popup_entrybox())
button_txt.place(relx=0.73, relheight=1, relwidth=cfg.btn_width)

exports_excel = img2icon(cfg.excel_icon,32)
button_exports = tk.Button(frame, text = "", font = 9, bg = "white", image = exports_excel, border = "0", command = lambda :img2excel()) 
button_exports.place(relx=0.785, relheight=1, relwidth=cfg.btn_width)

exports_pdf = img2icon(cfg.PDF_ICON, 32)
button_pdf = tk.Button(frame, text = "", font = 9, bg = "white", image = exports_pdf, border = "0", command=lambda: img2pdf())
button_pdf.place(relx=0.83, relheight=1, relwidth=cfg.btn_width)
#====================================================================================

lower_frame = tk.Frame(root, bg='green',  border= "0",colormap="new")
lower_frame.place(relx=0.5, rely=0.06, relwidth=1, relheight=0.90, anchor='n')


v = DocViewer(lower_frame)
v.place(relx=0, rely=0, relwidth=1, relheight=1)

page_img = tk.Canvas(lower_frame, bg="green", highlightthickness=0, bd = "0.5") # bd=0,
page_img.bind("<ButtonPress-1>", on_button_press)
page_img.bind("<B1-Motion>", on_move_press)
page_img.bind("<ButtonRelease-1>", on_button_release)
# Start Tk's event loop
root.config(menu=menubar, background = 'white', border = "0") #, cursor = "mouse"
root.mainloop()


