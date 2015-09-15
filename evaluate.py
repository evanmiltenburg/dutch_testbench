import glob, json
from gensim.models import Word2Vec
from dutch_testbench import test_suite

def evaluate_on_all(filename):
    model = Word2Vec.load_word2vec_format(filename, binary=True)
    vocab = set(model.vocab.keys())
    results = { 'relatedness1': test_suite.test_relatedness_1(model, vocab),
                'relatedness2': test_suite.test_relatedness_2(model, vocab),
                'similarity1': test_suite.test_similarity_1(model, vocab),
                'similarity2': test_suite.test_similarity_2(model, vocab),
                'typicality': test_suite.test_typicality(model, vocab),
                'goodness': test_suite.test_goodness(model, vocab),
                }
    return results

def get_name_from_path(path):
    return path.split('/')[-1].split('.')[0]

def evaluate_folder(path_to_folder):
    files = glob.glob(path_to_folder + '*.bin')
    for filename in files:
        results   = evaluate_on_all(filename)
        json_name = get_name_from_path(filename) + '.json'
        with open('./result_data/' + json_name, 'w') as f:
            json.dump(results, f)
