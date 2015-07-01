import xlrd

path = 'dutch_testbench/DeDeyne-BRM-2008b/exceldata/exemplar judgments/exemplarTypicalityRatings.xls'

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

def get_typicality_data():
    "Get the typicality data, by category"
    
    # Helper function.
    def get_mean_typicalities(sheet):
        "Get the mean typicalities from a given sheet."
        words  = map(lambda x:x.value, sheet.col(0)[1:])
        values = map(lambda x:x.value, sheet.col(30)[1:])
        return dict(zip(words,values))
    
    book = xlrd.open_workbook(path)
    sheet_dict = dict(zip(book.sheet_names(),book.sheets()))
    return {replacements[category]: get_mean_typicalities(sheet)
            for category, sheet in sheet_dict.items()}
