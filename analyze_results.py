import glob, pickle
from collections import defaultdict, namedtuple
from pprint import pprint

def path_to_name(path):
    return path.split('/')[-1].split('.')[0]

def load_pickled_dict(path):
    with open(path) as f:
        return pickle.load(f)

def get_all_results(folder="result_data/"):
    return {path_to_name(path): load_pickled_dict(path)
            for path in glob.glob(folder + '*.pickle')}

def average(l):
    return sum(l)/len(l)

Pair = namedtuple('Pair', ['key', 'score'])

def relatedness1(results):
    return [Pair(k, d['relatedness1']['score']) for k,d in results.items()]

def relatedness2(results):
    return [Pair(k, d['relatedness2']['overall']['score']) for k,d in results.items()]

def typicality(results):
    return [Pair(k, d['typicality']['score']) for k,d in results.items()]

def goodness(results):
    return [Pair(k, d['typicality']['score']) for k,d in results.items()]

def similarity1(results):
    def get_similarity(d):
        "Helper function"
        return average([d['similarity1'][category]['spearmanr'][0]
                        for category in d['similarity1'].keys()])
    # Output:
    return [Pair(k, get_similarity(d)) for k,d in results.items()]

def similarity2(results):
    def get_similarity(d):
        "Helper function"
        return average([d['similarity2'][category]['spearmanr'][0]
                        for category in d['similarity2'].keys()])
    # Output:
    return [Pair(k, get_similarity(d)) for k,d in results.items()]

def get_groups(results):
    groups = defaultdict(set)
    for name in results:
        if 'wikisize' in name:
            groups['wikisize'].add(name)
        elif 'govsize' in name:
            groups['govsize'].add(name)
        else:
            parts = name.split('_')
            groups[parts[0]].add(name)
    return groups

results = get_all_results()
groups  = get_groups(results)
relatedness1({k:results[k] for k in groups['all']})
