import xlrd
from itertools import combinations
from collections import defaultdict
import csv, re

def get_sheet_dict():
    path = 'dutch_testbench/Ruts-BRMIC-2004/Sim_ratings.xls'
    book = xlrd.open_workbook(path)
    sheet_dict = dict(zip(book.sheet_names(),book.sheets()))
    # no need for this sheet.
    sheet_dict.pop('information')
    return sheet_dict

################################################################################
# Basic functions allowing us to get useful values about the data.

def num_vals(sheet):
    "Returns the number of words."
    return max(int(cell.value) for cell in sheet.col(0) if isinstance(cell.value,float))

def getparticipants(sheet,colnum):
    "Function that takes a sheet and a column number and returns the participant numbers, if present."
    
    def subject_number(cell):
        "Helper function to make the loop look more readable."
        return int(cell.value.strip('}subject {'))
    
    return [subject_number(cell) for cell in sheet.col(colnum)
            if 'subject' in str(cell.value)]

def num_participants(sheet):
    "Get the total number of participants, using the above function."
    return max(i for colnum in range(5,8) for i in getparticipants(sheet, colnum))

def number_to_word(sheet):
    "Returns a dictionary INDEX:WORD for all words in the sheet."
    words = [cell.value for cell in sheet.col(1) if not cell.value==''][1:]
    words = map(lambda w: w.encode('utf-8'), words)
    return dict(zip(range(1,len(words)+1),words))

################################################################################
# Functions to get the similarity matrices from the excel sheet.

def get_matrix(sheet,row_n,until_val,start_col=3):
    "Returns a matrix containing all the similarity values for one participant."
    return [[cell.value for cell in sheet.row_slice(rowx,
                                                      start_colx=start_col,
                                                      end_colx=start_col+until_val)]
              for rowx in range(row_n,row_n+until_val)]

def get_matrices(sheet):
    "Returns all the similarity matrices."
    vals            = num_vals(sheet)
    until_val       = vals + 1
    participants    = num_participants(sheet)
    starting_row    = 2
    matrices        = {}
    for participant in range(0,participants):
        row_n = starting_row + participant * (vals + 5)
        matrices[participant] = get_matrix(sheet,row_n=row_n,until_val=until_val)
    return matrices

################################################################################
# And a function to get the actual scores for each item.

def get_similarity_scores(sheet):
    "Function to get similarity scores for all participants."
    
    def get_sim_values(matrix):
        "Helper function to get similarity values for individual matrices."
        similarity = {}
        for a,b in combinations(range(1,num_vals(sheet)+1), 2):
            smallest = min(a,b) # python automatically has the smallest item first if
            largest  = max(a,b) # you use combinations() on a range, but just to be sure..
            similarity[(smallest,largest)] = matrix[smallest][largest]
        return similarity
    matrices = get_matrices(sheet)
    return {participant: get_sim_values(matrix) for participant, matrix in matrices.items()}

def avg_score(sheet):
    "Compute average score for each index."
    avg_dict = defaultdict(list)
    scores = get_similarity_scores(sheet)
    for participant in scores:
        for pair in scores[participant]:
            if scores[participant][pair] > 0:
                avg_dict[pair].append(scores[participant][pair])
    return {pair:(sum(avg_dict[pair])/len(avg_dict[pair])) for pair in avg_dict}

################################################################################
# Let's generate a similarity dictionary for a particular sheet, using the
# functions defined above.

def similarity_for_sheet(sheet):
    "Use previously defined functions to get a pair:average similarity dictionary."
    scores = avg_score(sheet)
    words  = number_to_word(sheet)
    return {(words[a],words[b]): score for (a,b),score in scores.items()}

# Not using this function anymore. We'll just work from the dictionary.
# def write_similarity_values():
#     "Write everything to appropriately named files."
#     sheet_dict = get_sheet_dict()
#     for name, sheet in sheet_dict.items():
#         with open('similarity_values/' + name + '.csv','w') as f:
#             writer = csv.writer(f,delimiter='\t')
#             d = similarity_for_sheet(sheet)
#             writer.writerows([a,b,score] for (a,b),score in d.items())

def get_similarity_dict():
    "Get a dictionary containing the similarity values, by category."
    sheet_dict = get_sheet_dict()
    return {name: similarity_for_sheet(sheet)
            for name, sheet in sheet_dict.items()}
