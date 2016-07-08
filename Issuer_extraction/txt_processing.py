# Author: Albert de Jamblinne de Meux
# thealbertsmail@gmail.com
# All right reserved.
#
# Under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License
# Read the LICENSE.TXT for detail or https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode


# function to process the txt.

import os
import html2text
import re

def get_files(folder):
    """
    Provide a dict with the files.
    the key of the dict are the fileid,
    the values are the path to the file.
    """
    filelist = os.listdir(folder)
    files = {}
    for f in filelist:
        tmp=f.split('_')[0]
        if '.txt' in tmp:
            tmp=tmp.replace('.txt','')
        files[tmp] = os.path.realpath(os.path.join(folder,f))

    return files

def get_text(filename, raw=True):
    '''
    Return the text from a file.

    Args:
        filename: file to read
        raw: if False, the html tags are strip.

    Return: a string with the text.
    '''
    assert os.path.isfile(filename)

    if raw:
        with open(filename, 'r') as f:
            result = f.read().decode('ascii', errors='ignore')
        return result
    else:
        with open(filename, 'r') as f:
            data = f.read().decode('ascii', errors='ignore')
        return html2text.html2text(pre_html(data))

def pre_html(text):
    """
    Play with html tags before we strip all the html tags.
    """
    text = text.replace('</tr>', '.</tr>')
    text = text.replace('</p>', '.</p>')

    return text

def clean_text(text):
    """
    Clean the text a bit,
    """
    text = text.replace('*', '')
    text = text.replace('#', '')
    text = text.replace('\t', ' ')
    text = text.replace('\r', ' ')
    text = text.replace('&',' and ')
    text = re.sub(r'\.[\.\s]+', r'.\n\n', text)  # take care of multiple points
    text = re.sub(r'(\n)*(\s)*\|+(\s)*(\n)*', r'', text)  # clean any '|' with space en return around
    text = re.sub(r'--+', r'', text)  # remove ----- character
    text = re.sub(r'[\s\.]*:[\s\.]*', r': ', text)  # be sure tho have space around the column (:)
    #text = re.sub(r'\n\s*[1-9ivx\)\(]+\s', r'\n\g<0>. ', text) # reformat numbers.
    text = text.replace('\n', ' ') # remove carriage return.
    return text
