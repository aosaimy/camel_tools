from ntpath import join
from flask import Flask
from camel_tools.disambig.mle import MLEDisambiguator
from flask import request
from flask import jsonify
import sys

app = Flask(__name__)
mle = MLEDisambiguator.pretrained()

from camel_tools.morphology.database import MorphologyDB
from camel_tools.morphology.analyzer import Analyzer
db = MorphologyDB.builtin_db()

# Create analyzer with no backoff
analyzer = Analyzer(db)


@app.route("/diac", methods=['POST'])
def diac():
    content = request.get_json(silent=True)
    sentences = content['text'].split('\n')
    arr = []
    for sent in sentences:
        diacSent = disam('diac', sent.split())
        arr.append(' '.join(['' if word is None else word for word in diacSent]))
    return jsonify({"text": '\n'.join(arr), "type": 'lex'});

@app.route("/lemma", methods=['POST'])
def lemma():
    content = request.get_json()
    sentence = content['text'].split()
    return jsonify({"text": disam('lex', sentence), "type": 'lex'})

@app.route("/morph", methods=['POST'])
def morph():
    content = request.get_json(silent=True)
    sentence = content['text'].split()
    return morph(sentence);

def disam(type, sentence):

    # We expect a sentence to be whitespace/punctuation tokenized beforehand.
    # We provide a simple whitespace and punctuation tokenizer as part of camel_tools.
    # See camel_tools.tokenizers.word.simple_word_tokenize.
    disambig = mle.disambiguate(sentence)

    # Let's, for example, use the top disambiguations to generate a diacritized
    # version of the above sentence.
    # Note that, in practice, you'll need to make sure that each word has a
    # non-zero list of analyses.
    return [(d.analyses[0].analysis[type] if len(d.analyses) > 0 else None) for d in disambig];

def morph(sentence):

    # We expect a sentence to be whitespace/punctuation tokenized beforehand.
    # We provide a simple whitespace and punctuation tokenizer as part of camel_tools.
    # See camel_tools.tokenizers.word.simple_word_tokenize.
    
    words = []
    for d in sentence:
        if d:
            x = {
                'word': d,
                'analyses': analyzer.analyze(d),
            }
            words.append(x)
        else:
            words.append(None)
    return jsonify(words);


