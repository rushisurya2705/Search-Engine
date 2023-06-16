from flask import Flask, render_template, request, jsonify
import math
import chardet

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'


def find_encoding(fname):
    r_file = open(fname, 'rb').read()
    result = chardet.detect(r_file)
    charenc = result['encoding']
    return charenc


def load_vocab():
    vocab = {}
    filename = 'tf-idf/vocab.txt'
    my_encoding = find_encoding(filename)
    with open(filename, 'r', encoding=my_encoding) as f:
        vocab_terms = f.readlines()

    filename = 'tf-idf/idf-values.txt'
    my_encoding = find_encoding(filename)
    with open(filename, 'r', encoding=my_encoding) as f:
        idf_values = f.readlines()

    for (term, idf_value) in zip(vocab_terms, idf_values):
        vocab[term.strip()] = int(idf_value.strip())

    return vocab


def load_documents():
    documents = []
    filename = 'tf-idf/documents.txt'
    my_encoding = find_encoding(filename)
    with open(filename, 'r', encoding=my_encoding) as f:
        documents = f.readlines()

    documents = [document.strip().split() for document in documents]

    return documents


def load_inverted_index():
    inverted_index = {}
    filename = 'tf-idf/inverted-index.txt'
    my_encoding = find_encoding(filename)
    with open(filename, 'r', encoding=my_encoding) as f:
        inverted_index_terms = f.readlines()

    for row_num in range(0, len(inverted_index_terms), 2):
        term = inverted_index_terms[row_num].strip()
        documents = inverted_index_terms[row_num + 1].strip().split()
        inverted_index[term] = documents

    return inverted_index


def load_link_of_qs():
    filename = 'Qindex.txt'
    my_encoding = find_encoding(filename)
    with open(filename, 'r', encoding=my_encoding) as f:
        links = f.readlines()

    return links


vocab_idf_values = load_vocab()
documents = load_documents()
inverted_index = load_inverted_index()
Qlink = load_link_of_qs()


def get_tf_dictionary(term):
    tf_values = {}
    if term in inverted_index:
        for document in inverted_index[term]:
            if document not in tf_values:
                tf_values[document] = 1
            else:
                tf_values[document] += 1

    for document in tf_values:
        tf_values[document] /= len(documents[int(document)])

    return tf_values


def get_idf_value(term):
    return math.log(len(documents) / vocab_idf_values[term])


def calculate_sorted_order_of_documents(query_terms):
    potential_documents = {}
    for term in query_terms:
        if term not in vocab_idf_values or vocab_idf_values[term] == 0:
            continue
        tf_values_by_document = get_tf_dictionary(term)
        idf_value = get_idf_value(term)
        for document in tf_values_by_document:
            if document not in potential_documents:
                potential_documents[document] = tf_values_by_document[document] * idf_value
            potential_documents[document] += tf_values_by_document[document] * idf_value

    for document in potential_documents:
        potential_documents[document] /= len(query_terms)

    potential_documents = dict(sorted(potential_documents.items(), key=lambda item: item[1], reverse=True))

    ans = []
    for document_index in potential_documents:
        ans.append(
            {
                "Question Link": Qlink[int(document_index)][:-2],
                "Score": potential_documents[document_index],
                "Document": ' '.join(documents[int(document_index)]).upper()
            }
        )

    return ans

class SearchForm(FlaskForm):
    search = StringField('ENTER YOUR SEARCH TERM')
    num_questions = SelectField('NUMBER OF QUESTIONS', choices=[('5', '5'), ('10', '10'), ('15', '15'), ('20', '20')])
    submit = SubmitField('SEARCH')


@app.route("/", methods=['GET', 'POST'])
def home():
    form = SearchForm()
    results = []
    if form.validate_on_submit():
        query = form.search.data
        q_terms = [term.lower() for term in query.strip().split()]
        num_questions = int(form.num_questions.data)
        results = calculate_sorted_order_of_documents(q_terms)[:num_questions]

    return render_template('index.html', form=form, results=results)


if __name__ == '__main__':
    app.run(debug=True)
