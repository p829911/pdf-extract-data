# pdfextractdata
This Package is for extracting tables, table_images, and texts from pdf files.

Also texts in the table are deleted and are replaced by `**table number**`.

The main function is `pdf_to_pickle` ; output type of this function is dictionary. (dictionary keys: text, tables, images)

Image data can be displayed using `matplotlib.pyplot` package. ( `plt.imshow() `)

<br><br>

### USAGE

```python
from pdfextractdata.extract import Extract

p = Extract()
p.pdf_to_pickle(path)
```

<br><br>

### Function Description

- `filename_change(path)`  
  if file type is not PDF, convert it to PDF.

<br>

- `pdf_to_text(path)`  
  this function can pdf to text using pdfminer package.

<br>

- `process_text(text)`

  **parameter**:

  text (parameter) is output from above function ( `pdf_to_text` )

  **function**:

  text preprocessing function.

<br>

- `cos_sim(sent1, sent2)`

  **parameter**:

  sent1 is text in tables.

  sent2 is original text it's length is same with sent1

  **function**:

  calculate cosine similarity two sentence.

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

  The camelot package is not enough to display merged columns and rows; so preprocessing table for solving this problems.

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

  output type of this function is dictionary. (dictionary keys: text, tables, images)

  and be saved data in pickle file. saving directory is `working directory/pickle/name.pickle`


<br><br>

### OUTPUT

- **text**

  ![](https://user-images.githubusercontent.com/17154958/58078788-84aced80-7bea-11e9-9ff8-ff76f7fd4185.png)

<br>

- **table**

  ![](https://user-images.githubusercontent.com/17154958/58078856-ad34e780-7bea-11e9-99ab-50940c1e6ac6.png)

<br>

- **image**

  ![](/home/p829911/.config/Typora/typora-user-images/1558425989562.png)