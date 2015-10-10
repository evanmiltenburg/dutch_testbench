import xlrd
import glob
from itertools import combinations
from collections import defaultdict



def get_similarities():
    "Get similarities from the excel files provided by De Deyne et al."
    path = 'dutch_testbench/DeDeyne-BRM-2008b/exceldata/pairwise similarities/*.xls'
    sims = defaultdict(list)
    
    # Useful function:
    def get_kind(filename):
        "Helper function to extract category from the file name."
        return filename.split('/')[-1].split('.')[0][20:]
        
    for filename in glob.glob(path):
        book = xlrd.open_workbook(filename)
        kind = get_kind(filename)
        for i,sheet in enumerate(book.sheets()):
            names = [x.value for x in sheet.row(1)[2:]]
            # De Deyne et al. for some reason made the format different for these..
            if kind in {'Vegetables', 'Sports', 'Professions', 'Fruit'}:
                names = [x.value for x in sheet.row(0)[2:]]
            matrix = [[x.value for x in sheet.row(i)[2:]]
                      for i in range(2,sheet.nrows)]
            gen = ( tuple(sorted([a,b]))
                    for a,b in combinations(range(len(names)),2))
            d = {(names[a],names[b]):matrix[a][b] for a,b in gen}
            sims[kind].append(d)
    return sims

def average_similarities(d):
    "Get the averages for all dictionaries."
    
    # Useful function:
    def avg(l):
        "Returns the average for a list of numbers."
        return sum(l)/len(l)
    
    # Function to be used in dictionary comprehension below:
    def average_similarity(list_of_dicts):
        "Get the averages for one list of dictionaries."
        pairs = list_of_dicts[0].keys()
        simlist_dict = defaultdict(list)
        for sim_dict in list_of_dicts:
            for pair in pairs:
                simlist_dict[pair].append(sim_dict[pair])
        return {pair: avg(l) for pair,l in simlist_dict.items()}
    
    return {kind: average_similarity(d[kind]) for kind in d}

def get_average_similarities():
    "Wrapper for the functions above."
    return average_similarities(get_similarities())

def get_pairs():
    for d in get_average_similarities().values():
        for pair in d.keys():
            yield pair
