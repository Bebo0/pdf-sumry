from io import StringIO

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
nltk.download("stopwords")
nltk.download("punkt")

BOOK_PATH = "./test.pdf"


class RangeOfPages:
    """ Defines the range of pages that should be extracted from the pdf. Default value extracts all pages.
    """

    def __init__(self, start=0, end=10 ** 5):
        self.start = start
        self.end = end


def extractTextFromPDF(pdf, range=RangeOfPages()):
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
        rsrcmgr = PDFResourceManager()
        laParams = pdfminer.layout.LAParams()
        setattr(laParams, 'all_texts', True)
        device = TextConverter(rsrcmgr, pdfText, laparams=laParams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        currPageNumber = 0
        for page in PDFPage.create_pages(doc):
            if range.start <= currPageNumber <= range.end:  # only process pages within the range
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


def summarize(pdfText, numOfSentencesInSummary):
    """ Summarizes the text by scoring every sentence

    First pre-process the words and sentences, then score the words, then score the sentences, and finally output
    the best scored sentences into a summary.

    Args:
        pdfText: the pdf in string format to be summarized
        numOfSentencesInSummary: the number of sentences wanted in the summary

    Returns: ListOfStrings that represent the sentences in the summary, ordered by their score and index

    """

    def preProcessWords():
        # remove all non-letter characters such that the result is only words
        wordsOnly = re.sub('[^a-zA-Z]', ' ', pdfText)
        wordsOnly = re.sub(r'\s+', ' ', wordsOnly)
        return nltk.word_tokenize(wordsOnly.lower())

    def preProcessSentences():
        # remove all non-letter characters except for dots and semi colons which represent sentence boundaries
        sentences = re.sub('[^a-zA-Z0-9.;]', ' ', pdfText)
        sentences = re.sub(r'\s+', ' ', sentences)
        return nltk.sent_tokenize(sentences.strip())

    def scoreWords(wordsOnly):
        stopwords = nltk.corpus.stopwords.words('english')  # don't score words such as [a, an, the, it] etc.
        stopwords.append("cid")

        wordFrequency = defaultdict(int)
        for word in wordsOnly:
            if word not in stopwords and len(word) > 1:
                wordFrequency[word] += 1

        maxFrequency = max(wordFrequency.values())

        # score words in a normalized way
        for word, frequency in wordFrequency.items():
            wordFrequency[word] = (frequency / maxFrequency)

        return wordFrequency

    def scoreSentences(sentences, wordScore):
        # score sentences using the scores of their constituent words
        heap = []
        sentenceIndex = defaultdict(int)
        for idx, sentence in enumerate(sentences):
            score = 0
            for word in nltk.word_tokenize(sentence.lower()):
                if word in wordScore and len(sentence.split(' ')) < 30:
                    score += wordScore[word]
            heapq.heappush(heap, (-score, sentence))  # use min heap to keep track of the highest scoring sentences
            sentenceIndex[sentence] = idx  # keep track of where this sentence appeared from the beginning of the text
        return heap, sentenceIndex

    def findBestSentences(highestScored, indices):
        # find the highest scored sentences
        summarySentences = heapq.nsmallest(numOfSentencesInSummary, highestScored)
        # then sort them by the order of their appearance
        summarySentences.sort(key=lambda s: indices[s[1]])
        return summarySentences

    wordsOnly = preProcessWords()
    sentences = preProcessSentences()
    wordScores = scoreWords(wordsOnly)
    highestScored, indices = scoreSentences(sentences, wordScores)
    summarySentences = findBestSentences(highestScored, indices)

    return summarySentences


def main():
    range = RangeOfPages(0, 10000)
    pathToPDF = BOOK_PATH
    pdfText = extractTextFromPDF(pathToPDF, range)

    summarySentences = summarize(pdfText, 25)
    createSummaryTextFile(summarySentences, pathToPDF)


main()
