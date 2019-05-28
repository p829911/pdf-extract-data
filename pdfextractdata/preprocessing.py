import os
import re
from collections import Counter
import numpy as np
import pandas as pd


class Preprocessing:

    def filename_change(self, path):
        if path[-4:] != ".pdf":
            ch_path = path + ".pdf"
            os.rename(path, ch_path)
            return ch_path
        else:
            return path

    def process_text(self, text):
        text = text.lower()
        text = text.split("•")
        split_text = ""
        for sent in text:
            split_text += sent + "."
        text = split_text
        text = re.sub("(\[.*?\])", "", text)
        text = re.sub("[_\t\x0c\n\xad●\uf0b7®©]", " ", text)
        # text = re.sub("•", "", text)
        text = re.sub("-", " ", text)
        text = re.sub(" {2,}", " ", text)
        text = text.strip()
        text = re.sub(" \.", ".", text)
        text = re.sub("\.\.", ".", text)

        return text

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

    def delete_table_text(self, text, tables):
        # pandas options display to all sentence
        pd.set_option('display.max_colwidth', -1)

        final_text = text
        tables_text = []

        # table_to_text
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
            range_len = total_len - table_text_len + 1

            for i in range(range_len):
                text1 = table_text
                text2 = " ".join(final_text.split()[i:i + table_text_len])

                sim = self.cos_sim(text1, text2)
                if sim > max_cos:
                    max_cos = sim
                    max_i = i

            if max_cos > 0.6:
                final_text = " ".join(final_text.split()[:max_i]) + " **TABLE{}** ".format(Num + 1) + \
                             " ".join(final_text.split()[max_i + table_text_len:])

        return final_text

    def add_blank_cells(self, table):
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

        try:
            table = table.drop_duplicates()
        except:
            return table

        return table

    def clean_table(self, tables):
        table_list = []

        # preprocess tables
        # delete "\n", "  "
        for table in tables:
            table = self.process_table(table.df)
            table = self.add_blank_cells(table)

            table_list.append(table)

        return table_list
