# encoding=utf8
import codecs
import csv
import re
import sys
import os
import shutil
from collections import OrderedDict
import urllib.request
import pdf_converter as pdf

CHAPTERS_DIR = './chapters/'
ALL_CHAPTERS_FILENAME = 'all_chapters.md'
ALL_CHAPTERS_VN_FILENAME = 'all_chapters_vietnamese_only.md'
HEADER_TO_LINK_MAP = OrderedDict([(' ', '-'), ('#-', '#')])
HEADER_TO_LINK_MAP.update({a: '' for a in '.:?/'})
BOOK_DIR = './book/'

PARTS = [
    {'path': './chapters/p00_01_04.md', 'range': [1, 4]},
    {'path': './chapters/p01_05_12.md', 'range': [5, 12]},
    {'path': './chapters/p02_13_19.md', 'range': [13, 19]},
    {'path': './chapters/p03_20_27.md', 'range': [20, 27]},
    {'path': './chapters/p04_28_32.md', 'range': [28, 32]},
    {'path': './chapters/p05_33_35.md', 'range': [33, 35]},
    {'path': './chapters/p06_36_43.md', 'range': [36, 43]},
    {'path': './chapters/p07_44_46.md', 'range': [44, 46]},
    {'path': './chapters/p08_47_52.md', 'range': [47, 52]},
    {'path': './chapters/p09_53_57.md', 'range': [53, 57]},
    {'path': './chapters/p10_58.md', 'range': [58, 58]},
]


class Book(object):
    def __init__(self):
        self.en_vi_md_path = self._get_path('myl_en_vi.md')
        self.vi_md_path = self._get_path('myl_vi.md')
        self.en_vi_pdf_path = self._get_path('myl_en_vi.pdf')
        self.vi_pdf_path = self._get_path('myl_vi.pdf')

    @staticmethod
    def _get_path(filename):
        return os.path.join(BOOK_DIR, filename)

    def build_all(self):
        self.build_all_md(vn_only=True)
        # self.build_all_md(vn_only=False)
        # self.build_all_pdf(vn_only=True)
        # self.build_all_pdf(vn_only=False)

    def build_all_md(self, vn_only):
        output_filename = self.vi_md_path if vn_only else self.en_vi_md_path
        with codecs.open(output_filename, 'w', encoding='utf-8') as file_writer:
            # Cover.add_md(file_writer)
            TableOfContent().add_md(file_writer)
            # MainContent.add_md(file_writer)
            # Glossary.add_md(file_writer)
            # Acknowledge.add_md(file_writer)

    def build_add_pdf(self, vn_only):
        output_filename = self.vi_pdf_path if vn_only else self.en_vi_pdf_path
        pass


class BookPart(object):

    def _get_content_lines_md(self):
        """a list of markdown lines to be written, must be implemented in subclasses"""
        raise NotImplementedError

    def _get_content_lines_html(self):
        """a list of markdown lines to be written, must be implemented in subclasses"""
        raise NotImplementedError

    # @property
    def add_md(self, file_writer):
        for line in self._get_content_lines_md(): 
            file_writer.write(line)

    # @property
    def add_html(self, file_writer):
        for line in self._get_content_lines_html(): 
            file_writer.write(line)


class TableOfContent(BookPart):
    def _get_content_lines_md(self):
        lines = []
        lines.append("**MỤC LỤC**\n")
        for part in PARTS:
            part_path = part['path']
            lines.append(self.get_toc_line(part_path, level=0))
            start_chapter, end_chatper = part['range']
            for chapter_number in range(start_chapter, end_chatper + 1):
                chapter_path = _chapter_path_from_chapter_number(chapter_number)
                lines.append(self.get_toc_line(chapter_path, level=1))
        return lines

    def _get_content_lines_html(self):
        pass

    @staticmethod
    def _link_to_part_or_chap(path):
        filename = os.path.basename(path)
        
        # If it is a chapter, created a link syntax with only 2 digits (e.g: #01). 
        # If it is a part, keep "p" + 2 digit (e.g: #p01)   
        assert filename[0] in ['c', 'p'], filename

        if filename[0] == 'p':
            link = "#" + filename[:3]
        elif filename[0] == 'c':
            # TODO(tiep): set link to chapter = #chxx instead of #xx
            link = "#" + filename[2:4]
        else:
            assert False, "filename must start with 'c' or 'p', got filename = {}".format(filename)
        return link

    def get_toc_line(self, part_path, level):
        part_title = _get_title_from_file_path(part_path)
        
        full_link = "[{display_text}]({link_to_chapter})".format(
            display_text=_remove_sharp(part_title),
            link_to_chapter=self._link_to_part_or_chap(part_path)
        )
        return '\t'*level + '* ' + full_link + '\n'


def main(vn_only=True):
    if vn_only:
        output_filename = os.path.join(CHAPTERS_DIR, ALL_CHAPTERS_VN_FILENAME)
    else:
        output_filename = os.path.join(CHAPTERS_DIR, ALL_CHAPTERS_FILENAME)
    with codecs.open(output_filename, 'w', encoding='utf-8') as all_file_writer:
        # table of content
        all_file_writer.write("**MỤC LỤC**\n\n")
        for part in PARTS:
            part_path = part['path']
            _insert_to_toc(all_file_writer, part_path, level=0)
            start_chapter, end_chatper = part['range']
            for chapter_number in range(start_chapter, end_chatper + 1):
                chapter_path = _chapter_path_from_chapter_number(chapter_number)
                _insert_to_toc(all_file_writer, chapter_path, level=1)

        # main content
        for part in PARTS:
            part_path = part['path']
            _insert_content(all_file_writer, part_path, vn_only, heading=1)
            start_chapter, end_chatper = part['range']
            for chapter_number in range(start_chapter, end_chatper + 1):
                chapter_path = _chapter_path_from_chapter_number(chapter_number)
                _insert_content(all_file_writer, chapter_path, vn_only, heading=2)


def _remove_sharp(title):
    assert title.startswith('# ')
    return title[len('# '):]


def _get_title_from_file_path(part_path):
    with codecs.open(part_path, 'r', encoding='utf-8') as one_file:
        for line in one_file:
            if line.startswith('# '):
                line = line.strip()
                return line
    assert False, part_path


def is_part(path_name):
    assert path_name[1] in ['p', 'c'], path_name
    return path_name[1] == "p"


def _insert_to_toc(all_file_writer, part_path, level):
    all_file_writer.write(TableOfContent().get_toc_line(part_path, level))


def _insert_content(all_file_writer, file_path, vn_only, heading):
    all_file_writer.write('<!-- ============================ Insert {} =================================== -->\n'.format(file_path))
    all_file_writer.write(
        '<!-- Please do not edit this file directly, edit in {} instead -->\n'.format(file_path)
    )
    
    # Create subsection link with number instead of vietnamese
    path_name = file_path[file_path.index("s")+1:]
    
    if is_part(path_name):
        all_file_writer.write('<a name="%s"></a>\n'%path_name[1:4])
    else:
        all_file_writer.write('<a name="%s"></a>\n'%path_name[3:5])
    with codecs.open(file_path, 'r', encoding='utf-8') as one_file:
        for line in one_file:
            if vn_only and line.startswith('>'):
                continue
            try:
                if line.startswith('# '):
                    line = '#'*heading + ' ' + line[len('# '):]
                elif line.startswith('> # '):
                    line = '> ' + '#'*heading + ' ' + line[len('> # '):]
                all_file_writer.write(line)
            except UnicodeDecodeError as e:
                print('Line with decode error:')
                print(e)
    all_file_writer.write('\n')


def _create_header_link(line):
    for char, new_char in HEADER_TO_LINK_MAP.items():
        line = line.replace(char, new_char)
    return line.lower()


def _get_chapter_title(chapter_number):
    chapter_path = _chapter_path_from_chapter_number(chapter_number)
    with codecs.open(chapter_path, 'r', encoding='utf-8') as one_file:
        for line in one_file:
            if line.startswith('# '):
                line = line.strip()
                return line
    return '# {:02d}. chưa có tên'.format(chapter_number)


def _chapter_path_from_chapter_number(chapter_number):
    return os.path.join(CHAPTERS_DIR, 'ch{:02d}.md'.format(chapter_number))


def create_pdfs():
    pdf.main(vn_only=False)
    pdf.main(vn_only=True)

    # Remove __pycache__ folder  
    shutil.rmtree("__pycache__")


if __name__ == '__main__':
    Book().build_all()
    # main(vn_only=False)
    # main(vn_only=True)
    # create_pdfs()
