import xlrd
from collections import namedtuple
from collections import defaultdict
from collections import Counter
from numpy import percentile

path = 'dutch_testbench/Ruts-BRMIC-2004/Associations.xls'

def weight_associations(row, weight):
    if weight:
        return ([row.asso1] * 3) + ([row.asso2] * 2) + ([row.asso3] * 1)
    return [row.asso1, row.asso2, row.asso3]

def get_association_dict(weight=False):
    """Get a dictionary that contains associations for each exemplar, sorted by category.
    
    Example:
    >>> association_dict['beroepen']['boekhouder']
    Counter({u'saai': 33, u'geld': 18, u'economie': 17, u'cijfers': 8, ... })
    """
    book = xlrd.open_workbook(path)
    sheets = dict(zip(book.sheet_names(),book.sheets()))
    associations = sheets['recoded associations']
    
    # Get a list of the categories and initialize the association dictionary.
    # This dictionary holds a counter for each exemplar, counting the responses.
    categories = set([x.value for x in associations.col(1)[1:]])
    association_dict = {category:defaultdict(Counter) for category in categories}
    
    # Let's define a row using the column names from the sheet.
    # Having a namedtuple means that we can call each value by its name.
    Row = namedtuple('Row',[cell.value for cell in associations.row(0)])
    
    # And loop over the rows, so that we can count the associations for each exemplar.
    for n in range(1,associations.nrows):
        row = Row(*[str(cell.value) for cell in associations.row(n)])
        association_dict[row.category][row.exemplar].update(weight_associations(row, weight))
    for category, excounter in association_dict.items():
        for exemplar in excounter:
            try:
                excounter[exemplar].pop('x')
            except KeyError:
                pass
    return association_dict

def top_and_bottom(counter, p=5):
    top = percentile(list(counter.values()), 100-p)
    bottom = percentile(list(counter.values()), p)
    return ([a for a,b in counter.most_common() if b >= top],
           [a for a,b in counter.most_common() if b <= bottom])

def test_items1(weight):
    associations     = get_association_dict(weight)
    non_associations = get_non_associates(associations)
    for category, excounter in associations.items():
        for exemplar, counter in excounter.items():
            top, bottom = top_and_bottom(counter)
            for ass in top:
                for non_ass in non_associations[category]:
                    yield exemplar, ass, non_ass

def get_pairs1(weight):
    for ex, a1, a2 in test_items1(weight):
        yield ex, a1
        yield ex, a2

def test_items2(weight):
    associations     = get_association_dict(weight)
    for category, excounter in associations.items():
        for exemplar, counter in excounter.items():
            top, bottom = top_and_bottom(counter)
            for ass in top:
                for ass2 in bottom:
                    yield exemplar, ass, ass2

def get_pairs2(weight):
    for ex, a1, a2 in test_items2(weight):
        yield ex, a1
        yield ex, a2

def get_category_associates(d,category):
    "Get the associated words for an entire category (*not* exemplar!)"
    return set.union(*[set(d[category][exemplar].keys())
                       for exemplar in d[category]])

def get_non_associates(d):
    "Get the NON-associated words per category (*not* exemplar!)"
    categories = set(d.keys())
    associates = {cat:get_category_associates(d,cat) for cat in categories}
    
    # Define helper function:
    def non_associates(category):
        """Helper function to use in the dict comprehension. Returns the set of
        words that are associated with the other categories but not with the input
        category."""
        others = set.union(*[associates[cat] for cat in categories - {category}])
        return others - associates[category]
    
    return {category:non_associates(category) for category in categories}
