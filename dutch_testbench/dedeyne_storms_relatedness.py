import xlrd
from collections import namedtuple

path = 'dutch_testbench/DeDeyne-BRM-2008/DeDeyne(2008).xls'
Associations = namedtuple('Associations',['a1','f1','a2','f2','a3','f3'])

def get_association_dict():
    "Create a dictionary word: Associations."
    
    def create_entry(line):
        "Create an entry for the dictionary, on the basis of a line from the file."
        row = [cell.value for cell in line]
        word = row[0]
        return (word,Associations(*row[2:8]))
    
    book = xlrd.open_workbook(path)
    sheet = book.sheet_by_name('associations')
    
    d = dict(create_entry(sheet.row(rownum)) for rownum in range(1,sheet.nrows))
    
    return d
