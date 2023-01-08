import pickle
import os
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import string


pages_folder = "./FetchedPages/"
fetched_files = os.listdir(pages_folder)
stop_words = stopwords.words('english')
Stemmer = PorterStemmer()
page_tokens = {}
inverted_index = {}
for file in fetched_files:
    page = open(pages_folder + file, "r", encoding="utf-8")
    data = page.read()
    soup = BeautifulSoup(data, "lxml")
    for i in soup(["style", "script", "head", "meta", "[document]", "link", "noscript", "svg"]):
        i.extract()
    text_data = " ".join(soup.stripped_strings)
    text_data = text_data.lower()
    text_data = text_data.translate(str.maketrans('', '', string.punctuation))
    text_tokens = text_data.split()
    text_tokens = [token for token in text_tokens if token not in stop_words]
    text_tokens = [word for word in text_tokens if word.isalpha()]
    text_tokens = [Stemmer.stem(token) for token in text_tokens]
    text_tokens = [token for token in text_tokens if len(str(token)) >= 3]

    page_tokens[file] = text_tokens

    for token in text_tokens:
        tf = inverted_index.setdefault(token, {}).get(file, 0)
        inverted_index.setdefault(token, {})[file] = tf + 1
# print(page_tokens)
# print(inverted_index)
pickle_folder = "./PickleFile/"
os.makedirs(pickle_folder, exist_ok=True)

with open(pickle_folder + "3500_inverted_index.pickle", "wb") as f:
    pickle.dump(inverted_index, f)

with open(pickle_folder + "3500_page_tokens.pickle", "wb") as f:
    pickle.dump(page_tokens, f)
