import os
cur_dir = os.getcwd()
print(cur_dir)
import os
#os.environ['PATH'] = os.environ['PATH'] + ';' + 'C:\\Driver_Trett\\TAT\\OCR Program\\ImageMagick-7.0.8-Q16'
#os.environ['MAGIC_HOME'] = 'C:\\Driver_Trett\\TAT\\OCR Program\\ImageMagick-7.0.8-Q16'
#os.environ['MAGICK_CODER_MODULE_PATH'] = 'C:\\Driver_Trett\\TAT\\OCR Program\\ImageMagick-7.0.8-Q16\\modules\\coders'
#os.environ['PATH'] = os.environ['PATH'] + ';' + 'C:\\Driver_Trett\\TAT\\OCR Program\\poppler\\bin'
cur_dir = os.getcwd()

os.environ['PATH'] = os.environ['PATH'] + ';' + cur_dir +'\\poppler\\bin'
os.environ['PATH'] = os.environ['PATH'] + ';' + cur_dir +'\\ImageMagick-6.9.10-Q8'
os.environ['MAGIC_HOME'] = cur_dir +'\\ImageMagick-6.9.10-Q8'
os.environ['MAGICK_CODER_MODULE_PATH'] = cur_dir +'\\ImageMagick-6.9.10-Q8\\modules\\coders'
from wand.image import Image as Image_new
print("import sucuess")