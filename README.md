# Dutch Test bench

This repository provides a collection of tests for semantic models trained on the Dutch language. The data used in this repository is described in three papers: Ruts et al. (2004), De Deyne & Storms (2008), and De Deyne et al. (2008). One might also use the following files as an interface to the norms collected by these authors (the names are self-explanatory):

* `dedeyne_etal_similarity.py`
* `ruts_etal_similarity.py`
* `dedeyne_storms_relatedness.py`
* `ruts_etal_relatedness.py`
* `dedeyne_etal_typicality.py`
* `dedeyne_etal_goodness.py`

## Main file
The main file is `test_suite.py`. This file contains six test functions that each take a `model` object and return a dictionary with the outcome of the test. Import it using `from dutch_testbench import test_suite`.

* `test_relatedness_1` Tests relatedness by checking whether the strongest associate for each exemplar is more strongly associated with the exemplar than the third strongest one. Uses data from De Deyne & Storms (2008).

* `test_relatedness_2` Tests relatedness by checking for each of the semantic categories whether the strongest associate for each exemplar within that semantic category is more strongly associated with the exemplar than all the associates from other categories. Uses data from Ruts et al. (2004).

* `test_similarity_1` Tests similarity by correlating predicted similarity values with actual similarity values. Uses data from De Deyne et al. (2008).

* `test_similarity_2` Tests similarity by correlating predicted similarity values with actual similarity values. Uses data from Ruts et al. (2004).

* `test_typicality` Tests whether the model can single out atypical examplars within a semantic category. Uses data from De Deyne et al. (2008).

* `test_goodness` Correlates the predicted goodness ranking of exemplars within each category with the actual goodness ranking of those exemplars. Uses data from De Deyne et al. (2008).

**NB. If you are not using this module along with Gensim/word2vec:**
* All functions except `test_typicality` require `model.similarity()` to be implemented.
* `test_typicality` requires `model.doesnt_match()` to be implemented.

One way to achieve this is to **wrap your own model in a class that provides these functions.** The `similarity(a,b)` function should take two strings and return the similarity between those strings (or `1-distance(a,b)`).

One way to implement `doesnt_match` would be:

    def doesnt_match(l):
        """Computes similarities between the items in l and return the
        item with the lowest sum of similarities to the other items."""
        sims = {i: sum(similarity(i,x)
                       for x in filter(lambda x:not x == i, l)
                      ) for i in l}
        return min(sims.items(), key=lambda (word,sim):sim)[0]

## Requirements
Required packages are:
* `xlrd` to read excel files.
* `scipy` to compute correlation scores.
