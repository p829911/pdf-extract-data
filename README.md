# pdfextractdata
This Package is for extracting tables, table_images, and texts from pdf files.

Also texts in the table are deleted and are replaced by `**table number**`.

The main function is `pdf_to_pickle` ; output type of this function is dictionary. (dictionary keys: text, tables, images)

Image data can be displayed using `matplotlib.pyplot` package. ( `plt.imshow() `)

<br><br>

### Installation

- **Using pip**

```bash
pip3 install pdfextractdata
```

<br>

<br>

### USAGE

```python
from pdfextractdata.extract import Extract

p = Extract()
dic = p.pdf_to_pickle(path)
```

<br><br>

### Function Description

- `filename_change(path)`  
  if file type is not PDF, convert it to PDF.

<br>

- `pdf_to_text(path)`  
  this function can convert pdf to text using pdfminer package.

<br>

- `process_text(text)`

  **parameter**:

  text (parameter) is output from above function ( `pdf_to_text` )

  **function**:

  text preprocessing function.

<br>

- `cos_sim(sent1, sent2)`

  **parameter**:

  sent1 is the text extracted from tables.

  sent2 is the original text converted from the pdf file; its length is adjusted to match the length of sent1

  **function**:

  calculate cosine similarity of the two sentences.

<br>

- `process_table(tables)`

  **parameter**: 

  tables (parameter) is output from camelot package (extract tables from pdf)

  **function**: 

  preprocessing text in tables.

<br>

- `delete_table_text(text, tables)`

  **parameter**: 

  text (parameter) is output from above function ( `pdf_to_text` )

  tables (parameter) is output from camelot package (extract tables from pdf)

  **function**: 

  texts in the table are deleted and are replaced by `**table number**` ; using above `cos_sim(sent1, sent2)` function.

<br>

- `clean_table(tables)`

  **parameter**:

  tables (parameter) is output from camelot package (extract tables from pdf)

  **function**:

  The camelot package is not enough to display merged columns and rows, so preprocess table to solve this problem.

<br>

- `extracting_images(tables)`

  **parameter**:

  tables (parameter) is output from camelot package (extract tables from pdf)

  **function**:

  extracting table images from pdf.

<br>

- `pdf_to_pickle(path)`

  **function**:

  The main function is `pdf_to_pickle` ; 

  output type of this function is dictionary (dictionary keys: text, tables, images)

  and is saved as pickle file. saving directory is `working directory/pickle/name.pickle`


<br><br>

### OUTPUT

- **text**

  ![](https://user-images.githubusercontent.com/17154958/58078788-84aced80-7bea-11e9-9ff8-ff76f7fd4185.png)

<br>

- **table**

  ![](https://user-images.githubusercontent.com/17154958/58078856-ad34e780-7bea-11e9-99ab-50940c1e6ac6.png)

<br>

- **image**

  ![](https://user-images.githubusercontent.com/17154958/58079338-becabf00-7beb-11e9-8492-30bada1dae05.png)

