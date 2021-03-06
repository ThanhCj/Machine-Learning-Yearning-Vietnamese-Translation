# -*- coding: utf-8 -*-
import codecs
import os
import pdfkit


CHAPTERS_DIR = './chapters/'
BOOK_DIR = CHAPTERS_DIR
ACKNOWLEDGEMENT_PATH = './chapters/acknowledgement.md'
GLOSSARY_PATH = './glossary.md'

NO_PART_LIST = ['p{:02d}'.format(i) for i in range(0, 11)]
NO_CHAPTER_LIST = ['ch{:02d}'.format(i) for i in range(1, 59)]

# Ajust values below to modify font-size (unit:pt), colors and margin(unit:px) in pdf files
NORMAL_TEXT_SIZE = 17
SUB_TITLE_SIZE = 27
PART_NAME_SIZE = 48
PART_NAME_COLOR = "#0E275A"
PADDING_TOP_ALL_CHAPTERS = 200
PADDING_TOP_ALL_CHAPTERS_VN = 500

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


class BookMD(object):
    def __init__(self, vn_only=True):
        self.vn_only = vn_only
        self.md_file = self._get_path('book_{}vn.md'.format('' if vn_only else 'en_'))

    @staticmethod
    def _get_path(filename):
        return os.path.join(BOOK_DIR, filename)

    def build(self):
        with codecs.open(self.md_file, 'w', encoding='utf-8') as file_writer:
            TableOfContent().add_md(file_writer)
            MainContent(self.vn_only).add_md(file_writer)
            Glossary().add_md(file_writer)
            Acknowledgement().add_md(file_writer)
            file_writer.write('\n\n')


class BookPart(object):
    def __init__(self, vn_only=True):
        self.vn_only = vn_only

    def _get_content_lines_md(self):
        """a list of markdown lines to be written, must be implemented in subclasses"""
        raise NotImplementedError

    def add_md(self, file_writer):
        for line in self._get_content_lines_md():
            file_writer.write(line)


class TableOfContent(BookPart):
    def __init__(self, vn_only=True):
        super().__init__(vn_only=vn_only)

    def _get_content_lines_md(self):
        lines = []
        lines.append("## MỤC LỤC\n")
        for part in PARTS:
            part_path = part['path']
            lines.append(self.get_toc_line(part_path, level=0))
            start_chapter, end_chatper = part['range']
            for chapter_number in range(start_chapter, end_chatper + 1):
                chapter_path = _chapter_path_from_chapter_number(chapter_number)
                lines.append(self.get_toc_line(chapter_path, level=1))
        # ack
        lines.append(Glossary.toc_line())
        lines.append(Acknowledgement.toc_line())
        return lines

    def get_toc_line(self, path, level):
        part_title = _get_title_from_file_path(path)
        filename = os.path.basename(path)
        link = _get_label_from_filename(filename)

        full_link = "[{display_text}](#{link_to_chapter})".format(
            display_text=_remove_sharp(part_title),
            link_to_chapter=link
        )
        return '\t'*level + '* ' + full_link + '\n'


class MainContent(BookPart):
    def __init__(self, vn_only=True):
        super().__init__(vn_only=vn_only)

    def _get_content_lines_md(self):
        lines = []
        for part in PARTS:
            part_path = part['path']
            lines.extend(self._insert_content(part_path, heading=1))
            start_chapter, end_chatper = part['range']
            for chapter_number in range(start_chapter, end_chatper + 1):
                chapter_path = _chapter_path_from_chapter_number(chapter_number)
                lines.extend(self._insert_content(chapter_path, heading=2))
        return lines

    def _insert_content(self, file_path, heading):
        lines = []
        lines.append('<!-- ================= Insert {} ================= -->\n'.format(file_path))
        lines.append(
            '<!-- Please do not edit this file directly, edit in {} instead -->\n'.format(file_path)
        )

        filename = os.path.basename(file_path)
        lines.append('<a name="{}"></a>\n'.format(_get_label_from_filename(filename)))
        with codecs.open(file_path, 'r', encoding='utf-8') as one_file:
            for line in one_file:
                if self.vn_only and line.startswith('>'):
                    continue
                try:
                    if line.startswith('# '):
                        line = '#'*heading + ' ' + line[len('# '):]
                    elif line.startswith('> # '):
                        line = '> ' + '#'*heading + ' ' + line[len('> # '):]
                    lines.append(line)
                except UnicodeDecodeError as e:
                    print('Line with decode error:')
                    print(e)
        lines.append('\n')
        return lines


class Glossary(BookPart):
    label = 'glossary'

    def __init__(self, vn_only=True):
        super().__init__(vn_only=vn_only)

    @classmethod
    def toc_line(cls):
        return "* [Bảng thuật ngữ Anh-Việt](#{})\n".format(cls.label)

    def _get_content_lines_md(self):
        lines = []
        lines.append('<a name="{}"></a>\n\n'.format(self.label))
        with codecs.open(GLOSSARY_PATH, 'r', encoding='utf-8') as ack_file:
            for line in ack_file:
                lines.append(line)
        return lines


class Acknowledgement(BookPart):
    label = 'ack'

    def __init__(self, vn_only=True):
        super().__init__(vn_only=vn_only)

    @classmethod
    def toc_line(cls):
        return "* [Lời Nhóm Dịch](#{})\n".format(cls.label)

    def _get_content_lines_md(self):
        lines = []
        lines.append('<a name="{}"></a>\n\n'.format(self.label))
        with codecs.open(ACKNOWLEDGEMENT_PATH, 'r', encoding='utf-8') as ack_file:
            for line in ack_file:
                lines.append(line)
        return lines


class BookPDF(object):
    def __init__(self, vn_only=True):
        self.vn_only = vn_only
        self.md_file = BookMD(vn_only=vn_only).md_file
        self.html_file = self.md_file.replace('.md', '.html')
        self.pdf_file = self.md_file.replace('.md', '.pdf')
        self.no_part_list = ['p{:02d}'.format(i) for i in range(0, 11)]
        self.no_chapter_list = ['ch{:02d}'.format(i) for i in range(1, 59)]
        self.html_string = ''
        self.part_list = []  # TODO: description
        self.chapter_list = []

    def _get_raw_html_string(self):
        os.system("python3 -m grip {} --export {}".format(self.md_file, self.html_file))

        f = codecs.open(self.html_file, "r", "utf-8", "html.parser")
        self.html_string = f.read()
        f.close()

    def _add_break_page_before_each_part(self):
        for part_name in self.no_part_list:
            self.html_string = self.html_string.replace(
                '<p><a name="user-content-%s"></a></p>' % part_name,
                '<div style="page-break-after: always;"></div>\r\n<p><a name="%s"></a></p>' % part_name
            )

    def _add_break_page_before_each_chapter(self):
        for chapter_name in self.no_chapter_list:
            self.html_string = self.html_string.replace(
                '<p><a name="user-content-%s"></a></p>' % chapter_name,
                '<div style="page-break-after: always;"></div>\r\n<p><a name="%s"></a></p>' % chapter_name
            )

    def _add_break_page_before_glossary(self):
        # add page break before acknowledgement
        self.html_string = self.html_string.replace(
            '<p><a name="user-content-glossary"></a></p>',
            '<div style="page-break-after: always;"></div>\r\n<p><a name="glossary"></a></p>'
        )
        splits = ['a-d', 'e-l', 'm-r', 's-z']
        for split in splits:
            self.html_string = self.html_string.replace(
                '<p><a name="user-content-glossary-%s"></a></p>' % split,
                '<div style="page-break-after: always;"></div>\r\n<p><a name="%s"></a></p>' % split
            )

    def _add_break_before_acknowledgement(self):
        # add page break before acknowledgement
        self.html_string = self.html_string.replace(
            '<p><a name="user-content-ack"></a></p>',
            '<div style="page-break-after: always;"></div>\r\n<p><a name="ack"></a></p>'
        )

    @staticmethod
    def _get_link_from_file(filename):
        title = _get_title_from_file_path(filename)
        return _convert_title_to_link(title)

    def _correct_part_links(self):
        for order, part_name in enumerate(self.no_part_list):
            self.html_string = self.html_string.replace('#%s' % part_name, '%s' % self.part_list[order])

    def _correct_chapter_links(self):
        # Replace the correct link subsection of each chapter
        for order, chapter_name in enumerate(self.no_chapter_list):
            self.html_string = self.html_string.replace(
                '#%s' % chapter_name, '%s'% self.chapter_list[order]
            )

    def _correct_glossary_link(self):
        glossary_link = _convert_title_to_link(self._get_link_from_file(GLOSSARY_PATH))
        self.html_string = self.html_string.replace(
            '#glossary', glossary_link
        )

    def _correct_acknowledgement_link(self):
        ack_link = _convert_title_to_link(self._get_link_from_file(ACKNOWLEDGEMENT_PATH))
        self.html_string = self.html_string.replace(
            '#ack', ack_link
        )

    def _remove_title_bar(self):
        # Remove the ".md" title bar at begining
        self.html_string = self.html_string.replace(
            '<h3>\n                  <span class="octicon octicon-book"></span>\n                  %s\n                </h3>'%os.path.basename(self.md_file),
            ""
        )

    def _center_images(self):
        # TODO: avoide replace multiple times inside for loop
        for line in self.html_string.splitlines():
            if "<img " in line:
                new_line = line.replace("<p>", "<p align=\"center\">")
                self.html_string = self.html_string.replace(line, new_line)

    def _center_tabels(self):
        self.html_string = self.html_string.replace("<table>", '<table style="margin:0px auto; width:100%">')

    def _get_part_and_chapter_lists(self):
        assert not self.part_list, self.part_list
        assert not self.chapter_list, self.chapter_list
        for part in PARTS:
            part_path = part['path']
            self.part_list.append(self._get_link_from_file(part_path))

            start_chapter, end_chatper = part['range']
            for chapter_number in range(start_chapter, end_chatper + 1):
                chapter_path = _chapter_path_from_chapter_number(chapter_number)
                self.chapter_list.append(self._get_link_from_file(chapter_path))

    def _other_format(self):
        padding_top = PADDING_TOP_ALL_CHAPTERS_VN if self.vn_only else PADDING_TOP_ALL_CHAPTERS
        self.html_string = self.html_string.replace(
            '<style>',
            '<style>tr{font-size: %ipt}h1{padding-top: %ipx;text-align: center;color: %s}li,p{font-size: %ipt}body{text-align: justify;}' % (
                NORMAL_TEXT_SIZE, padding_top, PART_NAME_COLOR, NORMAL_TEXT_SIZE
            )
        )
        self.html_string = self.html_string.replace(
            '<h1>',
            '<h1 style="font-size:%ipt">'%PART_NAME_SIZE
        )
        self.html_string = self.html_string.replace(
            '<h2>',
            '<h2 style="font-size:%ipt">'%SUB_TITLE_SIZE
        )

    def _to_pdf(self):
        f = codecs.open(self.html_file, "w", "utf-8", "html.parser")
        f.write(self.html_string)
        f.close()
        options = {
            'page-size': 'A4',
            'margin-top': '2.5cm',
            'margin-right': '2.5cm',
            'margin-bottom': '2.5cm',
            'margin-left': '2.5cm',
            'encoding': "UTF-8",
            'footer-center': '[page]'
        }
        print("Convert html file {} to pdf file {}".format(self.html_file, self.pdf_file))
        pdfkit.from_file(self.html_file, self.pdf_file, options=options)

        # Remove the created html file
        os.remove(self.html_file)

    def build(self):
        # md to raw html
        self._get_raw_html_string()

        # raw html to fine html
        self._add_break_page_before_each_part()
        self._add_break_page_before_each_chapter()
        self._add_break_page_before_glossary()
        self._add_break_before_acknowledgement()
        self._get_part_and_chapter_lists()
        self._correct_part_links()
        self._correct_chapter_links()
        self._correct_glossary_link()
        self._correct_acknowledgement_link()
        self._remove_title_bar()
        self._center_images()
        self._center_tabels()
        self._other_format()

        # fine html to pdf
        self._to_pdf()


def _convert_title_to_link(title):
    title = title.lower()
    title = title.replace(" ", "-")
    title = title.replace(".", "")
    title = title.replace(":", "")
    title = title.replace("/", "")
    title = title.replace("?", "")
    title = title.replace(",", "")
    title = title.replace("#-", "#user-content-")
    return title


def _get_label_from_filename(chapter_or_part_filename):
    if chapter_or_part_filename.startswith('p'):
        return chapter_or_part_filename[:3]  # pxx
    elif chapter_or_part_filename.startswith('ch'):
        return chapter_or_part_filename[:4]  # chxx
    assert False, chapter_or_part_filename
    return ''


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
    return ''


def _chapter_path_from_chapter_number(chapter_number):
    return os.path.join(CHAPTERS_DIR, 'ch{:02d}.md'.format(chapter_number))


if __name__ == '__main__':
    BookMD(vn_only=True).build()
    BookMD(vn_only=False).build()
    BookPDF(vn_only=True).build()
    BookPDF(vn_only=False).build()
