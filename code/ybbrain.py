import json
import numpy as np
import gensim
import sklearn 
from sklearn.neighbors import KNeighborsClassifier
from sklearn import preprocessing
import random

intents = []
contexts = []

train_corp = []

with open('dictionary.json', 'r') as f:
    data = json.load(f)

for entry in data:
    example = entry['example']

    intent = entry['intent']
    if intent not in intents:
        intents.append(intent)

    context = entry['context']
    if context not in contexts:
        contexts.append(context)

    train_corp.append(
            gensim.models.doc2vec.TaggedDocument(
                gensim.utils.simple_preprocess(example), [intent, context]))

converter = gensim.models.doc2vec.Doc2Vec(vector_size=20, min_count=1, epochs=20)
converter.build_vocab(train_corp)
converter.train(train_corp, total_examples=converter.corpus_count, epochs=converter.epochs)   

# number of tag - номер тега
# number of tags - количество тегов
def prepare_classifier(n_tag, n_neighbors):
    X = []
    y = []
    for line_id, line in enumerate(train_corp):
        inferred_vec = converter.infer_vector(train_corp[line_id].words)
        X.append(inferred_vec)
        y.append(train_corp[line_id].tags[n_tag])

    encoder = preprocessing.LabelEncoder().fit(y)
    classifier = KNeighborsClassifier(n_neighbors=n_neighbors)

    y = encoder.transform(y)
    classifier.fit(X, y)

    return encoder, classifier

intent_encoder, intent_classifier = prepare_classifier(0, 3)
context_encoder, context_classifier = prepare_classifier(1, 3)

# for outside using
# мозг не включает сравнение с шаблонными фразами (алгоритмический метод)
def suppose(phrase, last_context=''):
    words = gensim.utils.simple_preprocess(phrase)

    # intent
    intent_code = intent_classifier.predict([converter.infer_vector(words)])
    # позиции с максимальной вероятностью
    intent = intent_encoder.inverse_transform(intent_code)[0]

    # context
    probs = context_classifier.predict_proba([converter.infer_vector(words)])[0]

    # подобие цепи маркова с одним шагом для коэффициентов
    if last_context:
        lc_code = context_encoder.transform([last_context])[0]
        probs[np.arange(len(probs)) != lc_code] *= 0.85

    maxprob_ids = np.argwhere(probs == np.max(probs)).flatten()
    maxprob_id = random.choice(maxprob_ids)
    context = context_encoder.classes_[maxprob_id]

    return intent, context
