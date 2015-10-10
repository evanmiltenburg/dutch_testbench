from itertools import product
import xlrd

path = 'dutch_testbench/DeDeyne-BRM-2008b/exceldata/exemplar judgments/exemplarGoodnessRankOrder.xls'

replacements = {'reptiles':            'reptiel',
                'amphibians':          'amfibie',
                'mammals':             'zoogdier',
                'birds':               'vogel',
                'fish':                'vis',
                'insects':             'insect',
                'musical instruments': 'muziekinstrument',
                'tools':               'gereedschap',
                'vehicles':            'voertuig',
                'sports':              'sporten',
                'professions':         'beroep',
                'clothing':            'kleding',
                'kitchen utensils':    'keukengerei',
                'weapons':             'wapen',
                'vegetables':          'groente',
                'fruit':               'fruit'}

def values_for_list(l):
    return [x.value for x in l]

def sum_for_row(row):
    return sum(values_for_list(row))

def ranking_for_sheet(sheet):
    "Get a ranking for a particular sheet."
    items = values_for_list(sheet.col(0))
    return [b for a,b in sorted((sum_for_row(sheet.row(i)[2:]), items[i])
                                for i in range(sheet.nrows))]

def get_goodness_rankings():
    "Get rankings for all the sheets."
    book = xlrd.open_workbook(path)
    sheet_dict = dict(zip(book.sheet_names(),book.sheets()))
    return {replacements[category]: ranking_for_sheet(sheet)
            for category, sheet in sheet_dict.items()}

def get_pairs():
    d = get_goodness_rankings()
    for cat, exemplars in d.items():
        for pair in product([cat],exemplars):
            yield pair
