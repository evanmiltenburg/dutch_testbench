from collections import namedtuple

path = 'dutch_testbench/DeDeyne-BRM-2008/DeDeyne(2008).txt'
Associations = namedtuple('Associations',['a1','f1','a2','f2','a3','f3'])

def get_association_dict():
    "Create a dictionary word: Associations."
    
    def create_entry(line):
        "Create an entry for the dictionary, on the basis of a line from the file."
        row = line.strip().split(';')
        word = row[0]
        data = map(lambda x: int(x) if x.isdigit() else x, row[2:8])
        return (word,Associations(*data))

    with open(path) as f:
        f.readline()
        d = dict(create_entry(line) for line in f)
    
    return d
