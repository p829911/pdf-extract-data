import io
import os
import pickle
import re
import camelot
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from .preprocessing import Preprocessing


class Extract(Preprocessing):
    """
    This Package is for extracting tables, table_images, and texts from pdf files.
    Also texts in the table are deleted and are replaced by "**table number**".
    The main function is "pdf_to_pickle"; output type of this function is dictionary. (dictionary keys: text, tables, images)
    Image data can be displayed using matplotlib.pyplot package. (plt.imshow())
    """

    def pdf_to_text(self, path):

        # pdf to text
        resource_manager = PDFResourceManager()
        fake_file_handle = io.StringIO()
        converter = TextConverter(resource_manager, fake_file_handle)
        page_interpreter = PDFPageInterpreter(resource_manager, converter)

        with open(path, 'rb') as fh:
            for page in PDFPage.get_pages(fh,
                                          caching=True,
                                          check_extractable=True):
                page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()

        # preprocess
        text = self.process_text(text)
        approval = "".join(re.findall("approval: \d{4}", text))
        text = re.sub(".*approval: \d{4}", " ", text)
        text = re.sub("full prescribing information: contents", "be delete!!", text)
        text = re.sub("full prescribing information are not", " ", text)
        text = re.sub("see full prescribing information", " ", text)
        text = re.sub("reference id: \d*", " ", text)
        text = re.sub("to report .*? www.[\w./]*", " ", text)
        text = re.sub(" {2,}", " ", text)
        text = approval + text
        text = text.strip()
        pre_index = text.find("be delete!!")
        post_index = text.find("full prescribing information")
        pre = text[:pre_index]
        post = text[post_index:]
        contents = text[pre_index:post_index]
        text = pre + "." + post

        return contents, text

    def pdf_to_table(self, path):

        tables = camelot.read_pdf(path, pages="all")

        return tables

    def extracting_images(self, tables):

        img_list = []

        for table in tables:
            img = table._image[0]
            col_start, row_end, col_end, row_start = list(table._image[1].keys())[0]
            table_img = img[int(row_start):int(row_end), int(col_start):int(col_end), :]
            img_list.append(table_img)

        return img_list

    def pdf_to_pickle(self, path, save=True):

        # add filename ".pdf" if not ".pdf"
        ch_path = self.filename_change(path)
        # pdf to text
        contents, text = self.pdf_to_text(ch_path)
        # extracting table from pdf using camelot
        tables = self.pdf_to_table(ch_path)

        if tables:
            # delete table text from real text
            final_text = self.delete_table_text(text, tables)
            # preprocess table
            table_list = self.clean_table(tables)
            # extract image from table
            img_list = self.extracting_images(tables)
            dic = {"text": final_text, "tables": table_list, "images": img_list, "contents": contents}

        else:
            dic = {"text": text, "tables": None, "images": None, "contents": contents}

        if save:
            # saving to pickle file
            name = path.split("/")[-1].split(".")[0]

            if not os.path.isdir(os.getcwd() + '/pickles/'):
                os.mkdir(os.getcwd() + '/pickles/')

            with open(os.getcwd() + '/pickles/' + name + ".pickle", 'wb') as f:
                pickle.dump(dic, f)

        return dic

    def contents_split(self, text):
        contents_list = [
            "1 indications and usage",
            "2 dosage and administration",
            "3 dosage forms and strengths",
            "4 contraindications",
            "5 warnings and precautions",
            "6 adverse reactions",
            "7 drug interactions",
            "8 use in specific populations",
            "9 drug abuse and dependence",
            "10 overdosage",
            "11 description",
            "12 clinical pharmacology",
            "13 nonclinical toxicology",
            "14 clinical studies",
            "15 references",
            "16 how supplied/storage and handling",
            "17 patient counseling information"
        ]
        contents_index = []
        text_list = []

        # find content start index
        for content in contents_list:
            contents_index.append(text.find(content))

        # split contents
        for i in range(len(contents_index)):
            if not i:
                pre = text[:contents_index[0]]
                text_list.append(pre)
            if contents_index[i] == -1:
                text_list.append(None)
            else:
                try:
                    text_s = text[contents_index[i]:contents_index[i + 1]]
                except:
                    text_s = text[contents_index[i]:]
                text_list.append(text_s)

        return text_list
