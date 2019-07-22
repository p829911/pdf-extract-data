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
        text = re.sub("full prescribing information are", " ", text)
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
        text = pre + ". prepostdividing" + post

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
        text = re.sub('–', ' ', text)
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

        contents_index_final = [index for index in contents_index if index != -1]

        # split contents
        for i in range(len(contents_index_final)):
            if not i:
                pre = text[:contents_index_final[0]]
                text_list.append(pre)

            try:
                text_s = text[contents_index_final[i]:contents_index_final[i + 1]]
            except:
                text_s = text[contents_index_final[i]:]
            text_list.append(text_s)

        return text_list

    def contents_words(self, dic):
        contents_list = [
            "indications and usage",
            "dosage and administration",
            "dosage forms and strengths",
            "contraindications",
            "warnings and precautions",
            "adverse reactions",
            "drug interactions",
            "use in specific populations",
            "drug abuse and dependence",
            "overdosage",
            "description",
            "clinical pharmacology",
            "nonclinical toxicology",
            "clinical studies",
            "references",
            "how supplied/storage and handling",
            "patient counseling information"
        ]
        for word in re.split('(\d.?[.]\d| \d\d? |[*])', dic['contents']):
            if len(word.strip()) != 0 and len(re.findall('[\d*.!-]', word.strip())) == 0:
                contents_list.append(word.strip())

        contents_list = list(set(contents_list))

        return contents_list

    def split_contexts(self, ls, contents_list):
        split_list = list()

        number = ls[:2].strip()
        number_two = re.findall(number + '[.]' + '\d\d? ', ls)
        number_final = list()

        for i in range(len(number_two)):
            if int(number_two[i].split('.')[1].strip()) == 1:
                number_final.append(number_two[i])
            elif int(number_two[i].split('.')[1].strip()) > int(number_two[i - 1].split('.')[1].strip()):
                number_final.append(number_two[i])

        for z in number_final:
            if z.split('.')[0] == number:
                result = re.search(z, ls)
                split_list.append(result.start())

        num = len(split_list)
        contexts = list()
        pre = ""
        title = ""

        if num == 0:
            for content in contents_list:
                match = re.findall('\d\d? ' + content, ls)
                if len(match):
                    search = re.search(match[0], ls)
                    end = search.end()
                    title = ls[:end].strip()
                    contexts.append(ls[end:].strip())
        else:
            for i in range(num):
                if i == 0:
                    pre = ls[:split_list[i]].strip()
                    for content in contents_list:
                        match = re.findall('\d\d? ' + content, pre)
                        if len(match):
                            search = re.search(match[0], pre)
                            end = search.end()
                            title = pre[:end].strip()
                            post = pre[end:].strip()
                            if post:
                                contexts.append(post)

                if i == num - 1:
                    contexts.append(ls[split_list[i]:].strip())
                else:
                    contexts.append(ls[split_list[i]:split_list[i + 1]].strip())

        return title, contexts

    def context_make_dic(self, contexts, contents_list):
        context_dic = {}
        for context in contexts:
            for content in contents_list:
                match = re.findall('\d\d?[.]\d\d? ' + content, context)
                if len(match):
                    search = re.search(match[0], context)
                    end = search.end()
                    pre = context[:end].strip()
                    post = context[end:].strip()
                    context_dic[pre] = post
                    break
            else:
                match = re.findall('\d\d?[.]\d\d?', context)
                if len(match):
                    search = re.search(match[0], context)
                    end = search.end()
                    pre = context[:end].strip()
                    post = context[end:].strip()
                    context_dic[pre] = post

        if context_dic == {}:
            context_dic["content"] = contexts
        return context_dic

    def pickle_make_dic(self, dic):
        contents_list = self.contents_words(dic)
        lss = self.contents_split(dic['text'])
        title_dic = {}
        for i, ls in enumerate(lss):
            if i != 0 and ls:
                title, contexts = self.split_contexts(ls, contents_list)
                context_dic = self.context_make_dic(contexts, contents_list)
                title_dic[title] = context_dic

        return title_dic
