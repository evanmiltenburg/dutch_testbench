# Import all the scripts to load the data.

# Relatedness
from . import dedeyne_storms_relatedness
from . import ruts_etal_relatedness

# Similarity
from . import dedeyne_etal_similarity
from . import ruts_etal_similarity

# Typicality/Goodness
from . import dedeyne_etal_typicality
from . import dedeyne_etal_goodness

# Other imports.
from scipy.stats.stats import pearsonr
from scipy.stats.stats import spearmanr
from scipy.stats.stats import kendalltau
from itertools import chain


def stronger_sim(model, exemplar, correct, incorrect):
    return model.similarity(exemplar, correct) > model.similarity(exemplar, incorrect)

def equal_sim(model, exemplar, correct, incorrect):
    return model.similarity(exemplar, correct) == model.similarity(exemplar, incorrect)

def test_relatedness_1(model, vocab):
    """Test the model for relatedness. Method: check whether the strongest associate
    for each exemplar is more strongly associated than the third strongest one.
    
    This method is using data from De Deyne & Storms (2008)"""
    items   = dedeyne_storms_relatedness.test_items()
    results = {'total': 0,
                'correct': 0,
               'incorrect': 0,
               'skipped': 0,
               'ex_not_in_dict': set(),
               'ass_not_in_dict': set()}
    
    for ex, a1, a3 in items:
        # If all words are in the vocabulary of the model, we can evaluate the item.
        if set([ex, a1, a3]).issubset(vocab):
            
            results['total'] += 1
            # Evaluate whether the similarity between the exemplar and its strongest
            # associate is stronger than the similarity between the exemplar and the
            # third strongest one.
            if stronger_sim(model, ex, a1, a3):
                results['correct'] += 1
            
            elif equal_sim(model, ex, a1, a3):
                results['correct'] += 0.5
                
            else:
                results['incorrect'] += 1
        
        # Else, skip the current item and record which word is not in the vocabulary.
        else:
            results['skipped'] += 1
            if not ex in vocab:
                results['ex_not_in_dict'].add(ex)
            else:
                results['ass_not_in_dict'].update({a1, a3}-vocab)
    
    # Final calculations:
    results['score'] = float(results['correct']) / results['total']
    return results

def test_relatedness_2(model, vocab, variant=None):
    """Test the model for relatedness. Method: check whether the most similar word
    for a given exemplar is more similar than any other word outside the category
    of the exemplar.
    
    This method is using data from Ruts et al. (2004)"""
    
    variants = {'cross-cat':ruts_etal_relatedness.test_items1(weight=False),
                'cross-cat-weighted':ruts_etal_relatedness.test_items1(weight=True),
                'within-cat': ruts_etal_relatedness.test_items2(weight=False),
                'within-cat-weighted': ruts_etal_relatedness.test_items2(weight=True)}
    
    # Get our basic data.
    items = variants[variant]
    # Now we define our results object.
    results = {'total': 0,
               'correct': 0,
               'incorrect': 0,
               'skipped': 0,
               'ex_not_in_dict': set(),
               'ass_not_in_dict': set()}
    
    # Code to perform the evaluation:
    for exemplar, associate, non_associate in items:
        if not exemplar in vocab:
            # If the exemplar is not in the vocab:
            results['skipped'] += 1
            results['ex_not_in_dict'].add(exemplar)
        
        elif not associate in vocab:
            results['skipped'] += 1
            results['ass_not_in_dict'].add(associate)
        
        elif not non_associate in vocab:
            continue
        
        else:
            results['total'] += 1
            # Perform the crucial test:
            if stronger_sim(model, exemplar, associate, non_associate):
                results['correct'] += 1
            
            elif equal_sim(model, exemplar, associate, non_associate):
                results['correct'] += 0.5
            
            else:
                results['incorrect'] += 1
    
    results['score'] = float(results['correct'])/results['total']
    return results

def test_similarity_1(model, vocab):
    """Test the model for similarity. Method: get correlation between model similarity
    and similarity of items in the test set.
    
    This method is using data from De Deyne et al. (2008)"""
    d       = dedeyne_etal_similarity.get_average_similarities()
    results = {category:{'skipped': set()} for category in d}
    pred_overall = []
    actual_overall = []
    for category in d:
        predicted_values = []
        actual_values    = []
        for pair, score in d[category].items():
            if set(pair).issubset(vocab):
                predicted_values.append(model.similarity(*pair))
                actual_values.append(score)
            else:
                results[category]['skipped'].update(set(pair) - vocab)
            pred_overall += predicted_values
            actual_overall += actual_values
        results[category]['pairs_tested'] = len(predicted_values)
        results[category]['pearsonr'] = pearsonr(predicted_values, actual_values)
        results[category]['spearmanr'] = spearmanr(predicted_values, actual_values)
    results['overall'] = dict()
    results['overall']['pairs_tested'] = len(predicted_values)
    results['overall']['pearsonr'] = pearsonr(pred_overall, actual_overall)
    results['overall']['spearmanr'] = spearmanr(pred_overall, actual_overall)
    return results

def test_similarity_2(model, vocab):
    """Test the model for similarity. Method: get correlation between model similarity
    and similarity of items in the test set.
    
    This method is using data from Ruts et al. (2004)"""
    d = ruts_etal_similarity.get_similarity_dict()
    results = {category:{'skipped': set()} for category in d}
    pred_overall = []
    actual_overall = []
    for category in d:
        predicted_values = []
        actual_values    = []
        for pair, score in d[category].items():
            if set(pair).issubset(vocab):
                predicted_values.append(model.similarity(*pair))
                actual_values.append(score)
            else:
                results[category]['skipped'].update(set(pair) - vocab)
            pred_overall += predicted_values
            actual_overall += actual_values
        results[category]['pairs_tested'] = len(predicted_values)
        results[category]['pearsonr'] = pearsonr(predicted_values, actual_values)
        results[category]['spearmanr'] = spearmanr(predicted_values, actual_values)
    results['overall'] = dict()
    results['overall']['pairs_tested'] = len(predicted_values)
    results['overall']['pearsonr'] = pearsonr(pred_overall, actual_overall)
    results['overall']['spearmanr'] = spearmanr(pred_overall, actual_overall)
    return results

def test_typicality(model, vocab):
    """Test the model on typicality data. Method: for each category, create sets
    of items that have a higher typicality than the mean, with one item that has
    a lower typicality than the mean. Model score is the success rate for picking
    out the atypical item.
    
    This method is using data from De Deyne et al. (2008)"""
    d = dedeyne_etal_typicality.get_typicality_data()
    results = {'correct':0, 'incorrect':0}
    for category in d:
        avg       = float(sum(d[category].values()))/len(d[category])
        above_avg = {ex for ex,score in d[category].items() if score > avg} & vocab
        below_avg = {ex for ex,score in d[category].items() if score < avg} & vocab
        for ex in below_avg:
            if model.doesnt_match(above_avg | {ex}) == ex:
                results['correct'] += 1
            else:
                results['incorrect'] += 1
    results['total'] = results['correct'] + results['incorrect']
    results['score'] = float(results['correct'])/results['total']
    return results

def test_goodness(model, vocab):
    """Tests the model on its ability to create a goodness ranking for a category.
    Method: get spearman (rank) correlation between the predicted and the actual ranking.
    
    This method is using data from De Deyne et al. (2008)"""
    d       = dedeyne_etal_goodness.get_goodness_rankings()
    results = {category:dict() for category in d}
    categories = (set(d.keys()) & vocab)
    for category in categories:
        exemplars = set(d[category]) & vocab
        sorted_exemplars = [b for a,b in sorted([(model.similarity(category, ex), ex)
                                                for ex in exemplars], reverse=True)]
        predicted_ranking = []
        actual_ranking    = []
        for exemplar in exemplars:
            actual_ranking.append(d[category].index(exemplar))
            predicted_ranking.append(sorted_exemplars.index(exemplar))
        results[category]['spearman'] = spearmanr(predicted_ranking, actual_ranking)
        results[category]['kendall'] = kendalltau(predicted_ranking, actual_ranking)
        results[category]['num_items'] = len(exemplars)
    avg_spearman = float(sum(abs(results[cat]['spearman'][0]) for cat in categories))/len(categories)
    avg_kendall  = float(sum(abs(results[cat]['kendall'][0]) for cat in categories))/len(categories)
    results['overall'] = dict()
    results['overall']['avg_spearman'] = avg_spearman
    results['overall']['avg_kendall'] = avg_kendall
    return results


def all_pairs():
    """DEFINITELY NOT OPTIMIZED function to get all pairs of words that are being
    compared by this module"""
    x = chain(dedeyne_storms_relatedness.get_pairs(),
              ruts_etal_relatedness.get_pairs1(True),
              ruts_etal_relatedness.get_pairs2(True),
              ruts_etal_relatedness.get_pairs1(False),
              ruts_etal_relatedness.get_pairs2(False),
              dedeyne_etal_similarity.get_pairs(),
              ruts_etal_similarity.get_pairs(),
              dedeyne_etal_typicality.get_pairs(),
              dedeyne_etal_goodness.get_pairs())
    for pair in x:
        yield pair

def write_all_pairs():
    "DEFINITELY NOT OPTIMIZED function to write all pairs to disk."
    with open('simpairs.txt','w') as f:
        f.writelines(a + '\t' + b + '\n'
                    for a,b in {tuple(sorted(pair)) for pair in all_pairs()})
