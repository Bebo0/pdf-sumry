# pdf_sumry
## _When you don't have time to read a 500 page pdf_

This is a Python script that summarizes an entire pdf or a range of its pages.

## How to Run
This project uses pipenv to manage and install its dependencies. Ensure you have pipenv installed on your computer.
```
pip3 install pipenv
```
Open project in an IDE like PyCharm and allow it to automatically install the required packages. Otherwise, cd into project dir, and run:
```
pipenv shell && pipenv install
```
(Optional) specify the following variables in the main() method.
```
range = RangeOfPages()
pathToPDF = BOOK_PATH
summarySentences = summarize(pdfText, 25)
```
Run.
```
(pdf-sumry) eva@eva-pc:~/src/pdf-sumry/src$ python3 pdf-sumry.py 
[nltk_data] Downloading package stopwords to /home/eva/nltk_data...
[nltk_data]   Package stopwords is already up-to-date!
[nltk_data] Downloading package punkt to /home/eva/nltk_data...
[nltk_data]   Package punkt is already up-to-date!
[nltk_data] Downloading package wordnet to /home/eva/nltk_data...
[nltk_data]   Package wordnet is already up-to-date!
INFO:pdf_sumry:Extracting text from pdf...
INFO:pdf_sumry:Successfully extracted text!
INFO:pdf_sumry:Summarizing...
INFO:pdf_sumry:Successfully summarized text!
INFO:pdf_sumry:Successfully created text file test_Summary!
```

## How it works
1) Extract all text from a pdf.
2) Pre-process words and sentences from text.
3) Lemmatize then score words by how many times they are seen.
4) Score sentences by their constituent words.
5) Summary will contain the best 25 (can be modified) sentences, sorted by when they appear.
