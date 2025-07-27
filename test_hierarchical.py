#!/usr/bin/env python3

from src.pdf_outline_extractor.extractor_new import PDFOutlineExtractor

def test_hierarchical():
    extractor = PDFOutlineExtractor()
    result = extractor.extract_outline('pdfs/file02.pdf')

    print('TITLE:', repr(result['title']))
    print('HEADINGS COUNT:', len(result['outline']))
    print('ALL HEADINGS:')
    for i, heading in enumerate(result['outline'], 1):
        print(f'  {i}. {heading["level"]} | {repr(heading["text"])} | Page {heading["page"]}')

if __name__ == "__main__":
    test_hierarchical()
