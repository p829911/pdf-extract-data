import io
import os
import pickle
import re
import numpy as np
import pandas as pd
from collections import Counter
import camelot
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter

class Extract:
    """
    This Package is for extracting tables, table_images, and texts from pdf files.
    Also texts in the table are deleted and are replaced by "**table number**".
    The main function is "pdf_to_pickle"; output type of this function is dictionary. (dictionary keys: text, tables, images)
    Image data can be displayed using matplotlib.pyplot package. (plt.imshow())
    """

    def filename_change(self, path):
        if path[-4:] != ".pdf":
            ch_path = path + ".pdf"
            os.rename(path, ch_path)
            return ch_path
        else:
            return path

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

        try:
            text = re.split("approval: *\d{4}", text)[1]
        except:
            text = text

        text = re.sub("reference id: *\d{7}", "", text)
        text = re.sub("revised[:]? \d{1,2}/\d{4}", "", text)

        return text

    def process_text(self, text):
        text = text.lower()
        text = re.sub("(\[.*?\])", "", text)
        text = re.sub("[_\t\x0c\n\xad●]", " ", text)
        text = re.sub("•", "", text)
        text = re.sub("-", " ", text)
        text = re.sub(" {2,}", " ", text)
        text = text.strip()

        return text

    def cos_sim(self, sent1, sent2):
        sent1 = dict(Counter(sent1.split()))
        sent2 = dict(Counter(sent2.split()))

        norm1 = np.linalg.norm(list(sent1.values()))
        norm2 = np.linalg.norm(list(sent2.values()))

        union = 0
        for word, count in sent1.items():
            try:
                union += sent2[word] * count
            except KeyError:
                continue

        return union / (norm1 * norm2)

    def process_table(self, table):

        # preprocess tables
        # delete "\n", "  "
        table = table.applymap(lambda x: x.replace("\n", " "))
        for column_num in range(table.shape[1]):
            try:
                if not table[column_num].apply(len).sum():
                    table = table.drop(column_num, axis=1)
            except:
                continue

        return table

    def delete_table_text(self, text, tables):

        # pandas options display to all sentence
        pd.set_option('display.max_colwidth', -1)

        final_text = text
        tables_text = []

        # preprocess text
        for table in tables:
            table = self.process_table(table.df)
            table_text = table.to_string(index=False, header=False)
            table_text = self.process_text(table_text)
            tables_text.append(table_text)

        # calculate cosine similarity
        for Num, table_text in enumerate(tables_text):

            max_cos = -1.0
            max_i = 0
            table_text_len = len(table_text.split())
            total_len = len(final_text.split())
            range_len = total_len - table_text_len

            for i in range(range_len):
                text1 = table_text
                text2 = " ".join(final_text.split()[i:i + table_text_len])

                sim = self.cos_sim(text1, text2)
                if sim >= max_cos:
                    max_cos = sim
                    max_i = i

            print(max_cos, max_i)

            final_text = " ".join(final_text.split()[:max_i]) + " **TABLE{}** ".format(Num + 1) + " ".join(
                final_text.split()[max_i + table_text_len:])

        final_text = re.split("full prescribing information: contents", final_text)

        pre = final_text[0]
        pre = pre.strip()

        try:
            post = re.split("sections or subsections omitted from the full prescribing information are not listed.",
                            final_text[1])[1]
            post = post.strip()
        except:
            post = None

        final_text = [pre, post]

        return final_text

    def clean_table(self, tables):

        table_list = []

        # preprocess tables
        # delete "\n", "  "
        for table in tables:
            table = self.process_table(table.df)

            # adding empty columns and rows
            for i in range(table.shape[0]):
                for j in range(table.shape[1]):
                    if not i and not j:
                        continue
                    elif not i and not table.iloc[i, j]:
                        table.iloc[i, j] = table.iloc[i, j - 1]
                    elif i == 1 and not j:
                        continue
                    elif i == 1 and not table.iloc[i, j]:
                        table.iloc[i, j] = table.iloc[i, j - 1]
                    elif not table.iloc[i, j]:
                        table.iloc[i, j] = table.iloc[i - 1, j]

            table.columns = table.iloc[0]
            table = table.iloc[1:]
            table = table.drop_duplicates()
            table_list.append(table)

        return table_list

    def extracting_images(self, tables):

        img_list = []

        for table in tables:
            img = table._image[0]
            tk = list(table._image[1].keys())[0]
            table_img = img[int(tk[3]):int(tk[1]), int(tk[0]):int(tk[2]), :]
            img_list.append(table_img)

        return img_list

    def pdf_to_pickle(self, path):

        # add filename ".pdf" if not ".pdf"
        path = self.filename_change(path)

        # pdf to text
        text = self.pdf_to_text(path)

        # extracting table from pdf using camelot
        tables = camelot.read_pdf(path, pages='all')

        if tables:

            # delete table text from real text
            final_text = self.delete_table_text(text, tables)

            # preprocess table
            table_list = self.clean_table(tables)

            # extract image from table
            img_list = self.extracting_images(tables)

            dic = {"text": final_text, "tables": table_list, "images": img_list}

        else:
            dic = {"text": text, "tables": None, "images": None}

        # saving to pickle file
        prefix = "/".join(path.split("/")[:-1])
        name = path.split("/")[-1].split(".")[0]

        if not os.path.isdir(prefix + '/pickles/'):
            os.mkdir(prefix + '/pickles/')

        with open(prefix + '/pickles/' + name + ".pickle", 'wb') as f:
            pickle.dump(dic, f)

        return dic