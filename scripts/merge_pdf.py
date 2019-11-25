#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
   Merge pdfs and output pdf with bookmark

   python pdfmerge.py -p ./pdf-files -o merged-out.pdf -b True
"""

import os, sys, codecs
from argparse import ArgumentParser, RawTextHelpFormatter
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger


def find_candidate_files(root_path='', keyword=None):
    result = []
    for fpath, dirs, fs in os.walk(root_path):
        for f in fs:
            candidate_file = os.path.join(fpath, f)
            if os.path.splitext(candidate_file)[1] != ".pdf":
                continue
            if f.find(keyword) == -1:
                continue
            result.append(candidate_file)

    return result


def merge_files(path, output_filename, keyword, import_bookmarks=True):
    merger = PdfFileMerger()
    file_list = find_candidate_files(root_path=path, keyword=keyword)
    if len(file_list) == 0:
        print("Cannot find any pdfs match with {} under folder {}".format(keyword, path))
        sys.exit()

    for filename in file_list:
        f = codecs.open(filename, 'rb')
        file_rd = PdfFileReader(f)
        short_filename = os.path.basename(os.path.splitext(filename)[0])
        if file_rd.isEncrypted:
            print('Cannot support encrypted pdf：{}'.format(filename))
            continue

        merger.append(file_rd, bookmark=short_filename, import_bookmarks=import_bookmarks)
        print('Merging pdf：{}'.format(filename))
        f.close()

    out_filename = os.path.join(os.path.abspath(path), output_filename)
    merger.write(out_filename)
    print('Merge succeed：{}'.format(out_filename))
    merger.close()


if __name__ == "__main__":
    description = "\n Merge pdfs and output pdf with bookmark\nExample："
    description = description + '\n python pdfmerge.py -p ./pdf-files -o merged-out.pdf -b True'

    parser = ArgumentParser(description=description, formatter_class=RawTextHelpFormatter)
    parser.add_argument("-p", "--path",
                        dest="path",
                        default=".",
                        help="path contains pdf files to merge")
    parser.add_argument("-k", "--keyword",
                        dest="keyword",
                        help="keyword to search")
    parser.add_argument("-o", "--output",
                        dest="output_filename",
                        default="merged.pdf",
                        help="output file name",
                        metavar="FILE")
    parser.add_argument("-b", "--bookmark",
                        dest="import_bookmarks",
                        default="True",
                        help="Whether to generate bookmarks")

    args = parser.parse_args()
    mergefiles(args.path, args.output_filename, args.import_bookmarks)
