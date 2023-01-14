import os

print(os.getenv('PATH'))
print()
os.environ['PATH'] = "C:\Program Files\Tesseract-OCR;" + os.environ['PATH']
print(os.getenv('PATH'))
enter_key = input("Enter : ")