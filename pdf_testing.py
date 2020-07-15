

from PyPDF2 import PdfFileReader


filename = "test_files/tj_resume.pdf"
text = ""

with open(filename, 'rb') as f:
    pdf_reader = PdfFileReader(f)

    for i in range(pdf_reader.numPages):
        page_data = pdf_reader.getPage(i)
        page_text = page_data.extractText()
        print(page_text)
        text += page_text

print(text)