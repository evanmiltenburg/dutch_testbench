import glob, pickle
from gensim.models import Word2Vec
from dutch_testbench import test_suite

def evaluate_on_all(filename):
    model = Word2Vec.load_word2vec_format(filename, binary=True)
    vocab = set(model.vocab.keys())
    results = { 'relatedness1': test_suite.test_relatedness_1(model, vocab),
                'relatedness2-cc': test_suite.test_relatedness_2(model, vocab, variant = 'cross-cat'),
                'relatedness2-ccw': test_suite.test_relatedness_2(model, vocab, variant = 'cross-cat-weighted'),
                'relatedness2-wc': test_suite.test_relatedness_2(model, vocab, variant = 'within-cat'),
                'relatedness2-wcw': test_suite.test_relatedness_2(model, vocab, variant = 'within-cat-weighted'),
                'similarity1': test_suite.test_similarity_1(model, vocab),
                'similarity2': test_suite.test_similarity_2(model, vocab),
                'typicality': test_suite.test_typicality(model, vocab),
                'goodness': test_suite.test_goodness(model, vocab),
                }
    return results

def get_name_from_path(path):
    return path.split('/')[-1].split('.')[0]

def evaluate_model(path_to_model):
    results   = evaluate_on_all(filename)
    pickle_name = get_name_from_path(filename) + '.pickle'
    with open('./result_data/' + pickle_name, 'w') as f:
        pickle.dump(results, f)

evaluate_folder('../vectors/all_w10_mc50_skipgram.bin')
