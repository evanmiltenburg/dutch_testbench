import csv, zipfile
from io import StringIO
from dutch_testbench import test_suite

class WordNetModel(object):
    """Object that loads a list of similarity values, and that has a similar interface
    to a Gensim model."""
    def __init__(self):
        self.simtype = 'Similar by path'
        self.simtypes = {'Similar by J&C', 'Similar by R', 'Similar by W&P',
                         'Similar by path', 'Similar by L&C', 'Similar by L'}
        zf      = zipfile.ZipFile('./WordNet-tools/sim-processing/simpairs.txt.all.zip')
        data    = StringIO(zf.read('simpairs.txt.all').decode('utf-8'))
        reader  = csv.DictReader(data, delimiter='\t')
        self.simdict = {(entry['word-1'], entry['word-2']): entry for entry in reader
                        if not entry['Similar by path'] == '-1.0'}
        self.vocab   = {w for pair in self.simdict for w in pair}
        zf.close()
        del data
        del reader
    
    def similarity(self,a,b):
        "Computes the similarity between a and b."
        pair = tuple(sorted([a,b]))
        return float(self.simdict[pair][self.simtype])
    
    def doesnt_match(self, l):
        """Computes similarities between the items in l and return the
        item with the lowest sum of similarities to the other items."""
        words = set(l)
        def sum_of_similarities(i):
            return sum(self.similarity(i,x) for x in (words - {i}) )
        
        return min( (sum_of_similarities(i), i) for i in l)[1]

def evaluate_on_all(model):
    model
    vocab = model.vocab
    results = { 'relatedness1': test_suite.test_relatedness_1(model, vocab),
                'relatedness2': test_suite.test_relatedness_2(model, vocab, variant = 'cross-cat'),
                'relatedness2': test_suite.test_relatedness_2(model, vocab, variant = 'cross-cat-weighted'),
                'relatedness2': test_suite.test_relatedness_2(model, vocab, variant = 'within-cat'),
                'relatedness2': test_suite.test_relatedness_2(model, vocab, variant = 'within-cat-weighted'),
                'similarity1': test_suite.test_similarity_1(model, vocab),
                'similarity2': test_suite.test_similarity_2(model, vocab),
                'typicality': test_suite.test_typicality(model, vocab),
                'goodness': test_suite.test_goodness(model, vocab),
                }
    return results
