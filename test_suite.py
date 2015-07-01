# Import all the scripts to load the data.

# Relatedness
import dedeyne_storms_relatedness
import ruts_etal_relatedness

# Similarity
import dedeyne_etal_similarity
import ruts_etal_similarity

# Typicality/Goodness
import dedeyne_etal_typicality
import dedeyne_etal_goodness

# Other imports.
from scipy.stats.stats import pearsonr
from scipy.stats.stats import spearmanr
from scipy.stats.stats import kendalltau

def stronger_sim(model, exemplar, correct, incorrect):
    return model.similarity(exemplar, correct) > model.similarity(exemplar, incorrect)

def test_relatedness_1(model, vocab):
    """Test the model for relatedness. Method: check whether the strongest associate
    for each exemplar is more strongly associated than the third strongest one.
    
    This method is using data from De Deyne & Storms (2008)"""
    d       = dedeyne_storms_relatedness.get_association_dict()
    items   = ( (exemplar, ass.a1, ass.a3) for exemplar, ass in d.items())
    results = {'correct': 0,
               'incorrect': 0,
               'skipped': 0,
               'ex_not_in_dict': set(),
               'ass_not_in_dict': set()}
    
    for ex, a1, a3 in items:
        # If all words are in the vocabulary of the model, we can evaluate the item.
        if set([ex, a1, a3]).issubset(vocab):
            
            # Evaluate whether the similarity between the exemplar and its strongest
            # associate is stronger than the similarity between the exemplar and the
            # third strongest one.
            if stronger_sim(model, ex, a1, a3):
                results['correct'] += 1
            
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
    results['total'] = results['correct'] + results['incorrect']
    results['score'] = float(results['correct']) / results['total']
    return results

def test_relatedness_2(model, vocab):
    """Test the model for relatedness. Method: check whether the most similar word
    for a given exemplar is more similar than any other word outside the category
    of the exemplar.
    
    This method is using data from Ruts et al. (2004)"""
    # Get our basic data.
    associations     = ruts_etal_relatedness.get_association_dict()
    non_associations = ruts_etal_relatedness.get_non_associates(associations)
    not_in_vocab     = set.union(*non_associations.values()) - vocab
    # Now we define our results object.
    results = {category: {'correct': 0,
                          'incorrect': 0,
                          'skipped': 0,
                          'ex_not_in_dict': set(),
                          'ass_not_in_dict': set()}
                for category in associations}
    
    # Code to perform the evaluation:
    for category in associations:
        na_set = non_associations[category] - not_in_vocab
        for exemplar in associations[category]:
            if exemplar in vocab:
                associate = associations[category][exemplar].most_common()[0][0]
                if associate in vocab:
                    for non_associate in na_set:
                        # Perform the crucial test:
                        if stronger_sim(model, exemplar, associate, non_associate):
                            results[category]['correct'] += 1
                        else:
                            results[category]['incorrect'] += 1
    
                else:
                    # If the association is not in the vocab:
                    results[category]['skipped'] += 1
                    results[category]['ass_not_in_dict'].add(associate)
    
            else:
                # If the exemplar is not in the vocab:
                results[category]['skipped'] += 1
                results[category]['ex_not_in_dict'].add(exemplar)
    
        # Compute statistics for category:
        results[category]['total'] = results[category]['correct'] + results[category]['incorrect']
        results[category]['score'] = float(results[category]['correct'])/results[category]['total']
    
    # Compute overall score and other statistics:
    total = sum(results[category]['total'] for category in results)
    correct = sum(results[category]['correct'] for category in results)
    incorrect = sum(results[category]['incorrect'] for category in results)
    score = float(correct)/total
    results['overall'] = {'total': total,
                          'correct': correct,
                          'incorrect': incorrect,
                          'score': score,
                          'not_in_vocab': not_in_vocab}
    return results

def test_similarity_1(model, vocab):
    """Test the model for similarity. Method: get correlation between model similarity
    and similarity of items in the test set.
    
    This method is using data from De Deyne et al. (2008)"""
    d       = dedeyne_etal_similarity.get_average_similarities()
    results = {category:{'skipped': set()} for category in d}
    for category in d:
        predicted_values = []
        actual_values    = []
        for pair, score in d[category].items():
            if set(pair) in vocab:
                predicted_values.append(model.similarity(*pair))
                actual_values.append(score)
            else:
                results[category]['skipped'].update(set(pair) - vocab)
        results[category]['pairs_tested'] = len(predicted_values)
        results[category]['pearsonr'] = pearsonr(predicted_values, actual_values)
        results[category]['spearmanr'] = spearmanr(predicted_values, actual_values)
    return results

def test_similarity_2(model, vocab):
    """Test the model for similarity. Method: get correlation between model similarity
    and similarity of items in the test set.
    
    This method is using data from Ruts et al. (2004)"""
    d = ruts_etal_similarity.get_similarity_dict()
    results = {category:{'skipped': set()} for category in d}
    for category in d:
        predicted_values = []
        actual_values    = []
        for pair, score in d[category].items():
            if set(pair) in vocab:
                predicted_values.append(model.similarity(*pair))
                actual_values.append(score)
            else:
                results[category]['skipped'].update(set(pair) - vocab)
        results[category]['pairs_tested'] = len(predicted_values)
        results[category]['pearsonr'] = pearsonr(predicted_values, actual_values)
        results[category]['spearmanr'] = spearmanr(predicted_values, actual_values)
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
