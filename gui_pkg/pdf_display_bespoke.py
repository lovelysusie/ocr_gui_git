# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 09:26:17 2019

@author: haonan.liu
"""

import os
cur_dir = os.getcwd()

os.environ['PATH'] = os.environ['PATH'] + ';' + cur_dir +'\\poppler\\bin'
os.environ['PATH'] = os.environ['PATH'] + ';' + cur_dir +'\\ImageMagick-6.9.10-Q8'
os.environ['MAGIC_HOME'] = cur_dir +'\\ImageMagick-6.9.10-Q8'
os.environ['MAGICK_CODER_MODULE_PATH'] = cur_dir +'\\ImageMagick-6.9.10-Q8\\modules\\coders'

from wand.image import Image as Image_new
import PyPDF2
import io
from .defaults import _C as cfg
from tika import parser
from PyPDF2 import PdfFileWriter, PdfFileReader

class display_pdf():
    def __init__(self, path_in):
        """
        this function is to display pdf pages on the tkinter windows
        """
        self.path_in = path_in
        #self.page_no = page_no
        self.temp_img_path = cfg.temp_img_path
        self.pdfFileObj_page = open(self.path_in,'rb')
        self.pdfReader = PyPDF2.PdfFileReader(self.pdfFileObj_page, strict = False)
        #self.num_pages = self.pdfReader.numPages
        #self.page = self.pdfReader.getPage(self.page_no)
        #self.page_width = self.page.mediaBox.getUpperRight_x()
        self.out = r".\memoryfile\temp.pdf"
        
    def pdf_page_to_png(self, page_no ,resolution = 100,):
        """
        Returns specified PDF page as wand.image.Image png.
        :param PyPDF2.PdfFileReader src_pdf: PDF from which to take pages.
        :param int pagenum: Page number to take.
        :param int resolution: Resolution for resulting png in DPI.
        """    

        try:
            pdfReader_page = PyPDF2.PdfFileReader(self.pdfFileObj_page)
            dst_pdf = PyPDF2.PdfFileWriter()
            dst_pdf.addPage(pdfReader_page.getPage(page_no))    

            pdf_bytes = io.BytesIO()
            dst_pdf.write(pdf_bytes)
            pdf_bytes.seek(0)    

            img = Image_new(file = pdf_bytes, resolution = resolution)
            img = img.convert("png")
            img.save(filename = self.temp_img_path)
            
        except:
            self.pdf_page_2_png_2(page_no)
 
 
    def pdf_page_2_png_2(self, page_no):
        """
        since import package takes time
        it will only import package when in need
        this function works as a supplimentary PDF pages to .png image
        
        """
        from pdf2image import convert_from_path
        images = convert_from_path(self.path_in)
        images[page_no].save(self.temp_img_path)
        #return images    

    def count_pdf_pages(self):
        #pdfFileObj_page = open(self.path_in,'rb')
        #pdfReader = PyPDF2.PdfFileReader(pdfFileObj_page, strict = False)
        num_pages = self.pdfReader.numPages
        return num_pages
    
    def get_page_width(self, page_no):
        page = self.pdfReader.getPage(page_no)
        page_width = page.mediaBox.getUpperRight_x()
        return page_width
    
    def extrac_text_from_page(self, page_number):
        """
        to extract content from the specific 
        """
        writer = PdfFileWriter()
        writer.addPage(self.pdfReader.getPage(page_number))
        outfile = open(self.out, 'wb')
        writer.write(outfile)
        outfile.close()
        raw = parser.from_file(self.out)
        text_of_page = raw['content']
        del raw
        return text_of_page






        
