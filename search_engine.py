import pickle
import os
import math
import numpy as np
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import string
from collections import Counter

pages_folder = "./FetchedPages/"
fetched_files = os.listdir(pages_folder)

pickle_folder = "./PickleFile/"
os.makedirs(pickle_folder, exist_ok=True)


# print(len(fetched_files))

with open(pickle_folder + "3500_inverted_index.pickle", "rb") as f:
    inverted_index = pickle.load(f)

with open(pickle_folder + "3500_page_tokens.pickle", "rb") as f:
    page_tokens = pickle.load(f)

with open(pickle_folder + "3500_crawled_pages.pickle", "rb") as f:
    pages = pickle.load(f)

# for key in inverted_index.keys():
#     df = len(inverted_index[key].keys())


def calculate_DF(documents):
    DF = {}

    for docno in documents:
        tokens = documents[docno]

        for word in tokens:
            try:
                DF[word].add(docno)
            except:
                DF[word] = {docno}

    for word in DF:
        DF[word] = len(DF[word])

    return DF


df = calculate_DF(page_tokens)
doc_length = len(page_tokens)
doc_vectors = {}
doc_vector_length = {}

for doc in page_tokens:
    tokens = page_tokens[doc]
    doc_vector_length[doc] = 0

    for token in tokens:
        tf = inverted_index.get(token, 0).get(doc, 0)
#         print(tf)

        doc_freq = df.get(token, 0)

        idf = np.log2(doc_length/doc_freq)

        weight = tf * idf
        try:
            doc_vectors[doc][token] = weight

        except:
            doc_vectors[doc] = {}
            doc_vectors[doc][token] = weight

        doc_vector_length[doc] += weight**2
    doc_vector_length[doc] = math.sqrt(doc_vector_length[doc])

# print(doc_vector_length)

query = str(input("Enter a query: "))
print("\n")

Stemmer = PorterStemmer()
stop_words = stopwords.words('english')

query_data = query.lower()
query_data = query_data.translate(str.maketrans('', '', string.punctuation))
query_tokens = query_data.split()
query_tokens = [token for token in query_tokens if token not in stop_words]
query_tokens = [word for word in query_tokens if word.isalpha()]
query_tokens = [Stemmer.stem(token) for token in query_tokens]
queries = [query_tokens]
query_vectors = {}
query_vector_length = {}
query_length = len(queries)
for index, query in enumerate(queries):
    print(index)
    q_tokens = queries[index]
    query_vector_length[index] = 0
    for token in np.unique(q_tokens):
        q_tf = Counter(q_tokens)[token]
        q_df = df.get(token, 0)
        if q_df == 0:
            q_idf = 0
        else:
            q_idf = np.log2(doc_length/q_df)
        q_weight = q_tf * q_idf
        try:
            query_vectors[index][token] = q_weight

        except:
            query_vectors[index] = {}
            query_vectors[index][token] = q_weight

        query_vector_length[index] += q_weight**2
    query_vector_length[index] = math.sqrt(query_vector_length[index])
query_vectors = query_vectors[0]
query_vector_length = query_vector_length[0]

cosine_similarity = {}

for token in query_tokens:
    if token in inverted_index:
        for doc_id, doc_freq in inverted_index[token].items():
            denom = doc_vector_length[doc_id] * \
                query_vector_length
            try:
                cosine_similarity[doc_id] += (
                    doc_vectors[doc_id][token] * query_vectors[token]) / denom
            except:
                cosine_similarity[doc_id] = (
                    doc_vectors[doc_id][token] * query_vectors[token]) / denom
cosine_similarity = dict(sorted(
    cosine_similarity.items(), key=lambda item: item[1], reverse=True))

# print(list(cosine_similarity.keys())[0:10])
choice = True
current = 0
while (choice):
    if current > len(cosine_similarity):
        print("No more documents left")
        break
    elif current+10 > len(cosine_similarity):
        for index, link in enumerate(list(cosine_similarity.keys())[current:]):
            l = int(link[11:])
            print(l)
            print(str(index+current+1)+'.'+pages[l])
            break
    else:
        for index, link in enumerate(list(cosine_similarity.keys())[current:current+10]):
            l = int(link[11:])
            print(str(index+current+1)+'.'+pages[l])
        ch = str(input("Do you want to see more results:"))
        if ch == 'y' or ch == 'yes':
            choice = True
        else:
            choice = False
        current += 10
