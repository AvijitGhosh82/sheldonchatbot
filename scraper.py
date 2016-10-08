from bs4 import BeautifulSoup
import requests
import types
import pickle

def replace_with_newlines(element):
    text = ''
    for elem in element.recursiveChildGenerator():
        if isinstance(elem, types.StringTypes):
            text += elem.strip()
        elif elem.name == 'br':
            text += '\n'
    return text

url = "http://www.imdb.com/character/ch0064640/quotes"

r  = requests.get(url)
data = r.text
soup = BeautifulSoup(data,"html.parser")

quoteblock= soup.find("div", {"id": "tn15content"})
quoteblock.find('div').decompose()
quoteblock.find('h5').decompose()


quoteblock = replace_with_newlines(quoteblock)

quotes=quoteblock.split("\n\n")

pickle.dump(quotes, open('quoteobj', 'w'))

