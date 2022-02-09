import requests
from bs4 import BeautifulSoup

url = 'https://www.worddb.com/6-letter/words'

html = requests.get(url).content
soup = BeautifulSoup(html, 'html.parser')

words = soup.findAll(
    'a', {
        'class': 'word s_but s_but_point'
    }
)
words = [(w.text).lower().replace('-','') for w in words]
words.append('eunoia')
words = [w for w in words if len(w) == 6]
words_csv = [', '.join(list(w)) for w in words]


with open('dictionary.txt','w') as f:
    f.write(', '.join(words))
