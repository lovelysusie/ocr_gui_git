
import pytesseract
import os
import tabula
import cv2
import numpy as np
#from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2 import PdfFileReader

class page_exports():
    def __init__(self, img_in, exp_path):
        self.img_in = img_in
        self.exp_path = exp_path
        self.croped_pdf_path = r".\memoryfile\croped_temp.pdf"

    def export(self):
        path_split = os.path.splitext(self.exp_path)
        if path_split[1] == '.txt':
            self.__to_txt__()
        else:
            self.__to_pdf__()
    def __to_txt__(self):
        ocr_result = pytesseract.image_to_string(self.img_in)
        if ocr_result.isspace():
            ocr_result = pytesseract.image_to_string(self.img_in, config = '--psm 6')
        file = open(self.exp_path, 'w', encoding = 'utf8')
        file.write(ocr_result)
        file.close()

    def __to_pdf__(self):
        pdf = pytesseract.image_to_pdf_or_hocr(self.img_in, extension='pdf')
        f = open(self.exp_path, 'w+b')
        f.write(pdf)
        f.close()
    def img2df(self, path_in, page_num, area = None, shown_wid = None,multiple_tables=False):
        try:
            if area != [0,0,1,1]:
                pdfobj = PdfFileReader(open(path_in, 'rb'))
                _,_, page_width, page_height = pdfobj.getPage(0).mediaBox
                print("page width {}, height{}".format(page_width, page_height))
                ratio = page_width/shown_wid
                area = (np.array(area) * ratio).tolist()
            df = tabula.read_pdf(path_in, pages = page_num+1, lattice=True, area = area,multiple_tables=multiple_tables)
            
            return df
        except:
            return None
    def crop_page(self,pdf_path,page_num,page_width,convas_wid, s_x, s_y, c_x, c_y):
        ratio = page_width/convas_wid
        bbox = [s_y,s_x, c_y, c_x] * int(ratio)
        df = tabula.read_pdf(pdf_path, area = bbox ,pages = page_num+1, lattice=True)
        return df
    def img2str(self, img_input):
        text = pytesseract.image_to_string(img_input)
        if text.isspace():
            text = pytesseract.image_to_string(img_input, config = '--psm 6')
        return text

# path = r"C:\Users\haonan.liu\Downloads\An_MPI_Implementation_of_the_Fast_Messy_Genetic_Al.pdf"
# from PyPDF2 import PdfFileReader
# input1 = PdfFileReader(open(path, 'rb'))
# shapes = input1.getPage(0).mediaBox
