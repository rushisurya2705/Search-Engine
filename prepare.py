# read the index.txt and prepare documents, vocab , idf

import chardet
import os


def find_encoding(fname):
    r_file = open(fname, 'rb').read()
    result = chardet.detect(r_file)
    charenc = result['encoding']
    return charenc

current_directory = os.path.dirname(os.path.abspath(__file__))

# filename = 'Search_engine/index.txt'
# my_encoding = find_encoding(filename)
file_path = os.path.join(current_directory, 'index.txt')

my_encoding = find_encoding(file_path)
# Open the file
with open(file_path, 'r', encoding=my_encoding) as f:
    lines = f.readlines()
# with open(filename, 'r', encoding=my_encoding) as f:
#     lines = f.readlines()

def preprocess(document_text):
    # remove the leading numbers from the string, remove not alpha numeric characters, make everything lowercase
    terms = [term.lower() for term in document_text.strip().split()[1:]]
    return terms

vocab = {}
documents = []
for index, line in enumerate(lines):
    # read statement and add it to the line and then preprocess
    tokens = preprocess(line)
    documents.append(tokens)
    tokens = set(tokens)
    for token in tokens:
        if token not in vocab:
            vocab[token] = 1
        else:
            vocab[token] += 1

# reverse sort the vocab by the values
vocab = dict(sorted(vocab.items(), key=lambda item: item[1], reverse=True))

print('Number of documents: ', len(documents))
print('Size of vocab: ', len(vocab))
print('Sample document: ', documents[0])

# save the vocab in a text file
# Get the current directory path
# Create the 'tf-idf' directory
directory = os.path.join(current_directory, 'tf-idf')
if not os.path.exists(directory):
    os.makedirs(directory)
# directory = 'tf-idf'
# if not os.path.exists(directory):
#     os.makedirs(directory)
filepath = os.path.join(directory, 'vocab.txt')
with open(filepath, 'w') as f:
    for key in vocab.keys():
        f.write("%s\n" % key)


# with open('tf-idf/vocab.txt', 'w') as f:
#     for key in vocab.keys():
#         f.write("%s\n" % key)

# save the idf values in a text file
filepath = os.path.join(directory, 'idf-values.txt')
with open(filepath, 'w') as f:
    for key in vocab.keys():
        f.write("%s\n" % vocab[key])
# with open('tf-idf/idf-values.txt', 'w') as f:
#     for key in vocab.keys():
#         f.write("%s\n" % vocab[key])

# save the documents in a text file
filepath = os.path.join(directory, 'documents.txt')
with open(filepath, 'w') as f:
    for document in documents:
        f.write("%s\n" % ' '.join(document))
# with open('tf-idf/documents.txt', 'w') as f:
#     for document in documents:
#         f.write("%s\n" % ' '.join(document))


inverted_index = {}
for index, document in enumerate(documents):
    for token in document:
        if token not in inverted_index:
            inverted_index[token] = [index]
        else:
            inverted_index[token].append(index)

# save the inverted index in a text file
filepath = os.path.join(directory, 'inverted-index.txt')
with open(filepath, 'w') as f:
    for key in inverted_index.keys():
        f.write("%s\n" % key)
        f.write("%s\n" % ' '.join([str(doc_id) for doc_id in inverted_index[key]]))
# with open('tf-idf/inverted-index.txt', 'w') as f:
#     for key in inverted_index.keys():
#         f.write("%s\n" % key)
#         f.write("%s\n" % ' '.join([str(doc_id) for doc_id in inverted_index[key]]))
