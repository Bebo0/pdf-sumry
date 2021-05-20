from pdfminer.high_level import extract_text, extract_pages
# import pdfminer.high_level
from io import StringIO

BOOK_PATH = "../Complete_Course_In_Astrobiology.pdf"
import re
import pdfminer
import nltk
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from collections import defaultdict
import heapq


class RangeOfPages:
    """
    Defines the range of pages that should be extracted from the pdf. Default value extracts all pages.
    """
    def __init__(self, start=0, end=10**5):
        self.start = start
        self.end = end


def extractTextFromPDF(pdf=BOOK_PATH, range=RangeOfPages()):
    """

    Args:
        pdf: the path of the pdf to be summarized relative to this module
        range (optional): the range of pages where the summarization should be extracted

    Returns: one unclean string representing ALL the text extracted from the pdf

    """
    pdfText = StringIO()
    with open(pdf, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        # outlines = doc.get_outlines()
        rsrcmgr = PDFResourceManager()
        laParams = pdfminer.layout.LAParams()
        setattr(laParams, 'all_texts', True)
        device = TextConverter(rsrcmgr, pdfText, laparams=laParams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        currPageNumber = 0
        for page in PDFPage.create_pages(doc):
            if range.start <= currPageNumber <= range.end:
                interpreter.process_page(page)
            currPageNumber += 1

        return pdfText.getvalue()


def createSummaryTextFile(summarySentences, pathToPDF):
    """ Output the summary into a .txt file named after the original pdf + "summary"

    Args:
        summarySentences: ListOfStrings that represent the sentences in the summary, ordered by their score

    Returns: None

    """
    name = re.findall(r"(\b\w*)(.pdf)?$", pathToPDF)[0][0]
    name += "_Summary"
    f = open(name, "w+")
    for score, sentence in summarySentences:
        f.write(sentence + "\n")
    f.close()


def summarize(pdfText):
    """ Summarizes the text by scoring every sentence


    Args:
        pdfText: the pdf in string format to be summarized

    Returns: ListOfStrings that represent the sentences in the summary, ordered by their score

    """
    wordsOnly = re.sub('[^a-zA-Z]', ' ', pdfText)
    wordsOnly = re.sub(r'\s+', ' ', wordsOnly)

    sentences = re.sub('[^a-zA-Z0-9.]', ' ', pdfText)
    sentences = re.sub(r'\s+', ' ', sentences)

    sentences = nltk.sent_tokenize(sentences.strip())

    stopwords = nltk.corpus.stopwords.words('english')
    stopwords.append("cid")
    wordFrequency = defaultdict(int)

    wordsOnly = wordsOnly.lower()
    wordsOnly = nltk.word_tokenize(wordsOnly)
    # print(wordsOnly)

    for word in wordsOnly:
        if word not in stopwords and len(word) > 1:
            wordFrequency[word] += 1

    maxFrequency = max(wordFrequency.values())

    for word, frequency in wordFrequency.items():
        wordFrequency[word] = (frequency / maxFrequency)

    sentenceScores = defaultdict(int)
    heap = []
    sentenceIndex = defaultdict(int)
    print(sentenceScores[0])
    for idx, sentence in enumerate(sentences):
        score = 0
        for word in nltk.word_tokenize(sentence.lower()):
            if word in wordFrequency and len(sentence.split(' ')) < 30:
                score += wordFrequency[word]
        heapq.heappush(heap, (-score, sentence))
        sentenceIndex[sentence] = idx

    summarySentences = heapq.nsmallest(30, heap)
    summarySentences.sort(key=lambda s: sentenceIndex[s])
    print(summarySentences)


    return summarySentences


def main():
    range = RangeOfPages(19)
    pathToPDF = BOOK_PATH
    pdfText = extractTextFromPDF(pathToPDF, range)

    summarySentences = summarize(pdfText)
    createSummaryTextFile(summarySentences, pathToPDF)

main()
