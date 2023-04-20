# todo: black format, os.path
import pickle
import random
import os

with open(os.path.join("pert_scripts","labels_uniprot.pkl"), 'rb') as f:
    label_dict = pickle.load(f)
assert 'DKGFGFITPADGSKDVFVHFSAIQSNDFKTLDEGQKVEFSIENGAK' in label_dict.keys()
assert label_dict['DKGFGFITPADGSKDVFVHFSAIQSNDFKTLDEGQKVEFSIENGAK'] == 'CSPA_YEREN'


def is_label_same(seq_pert, label_pert):
    """
    Pass if given sequence, an id is not found
    Pass if given sequence, the id remains the same
    Alert if given seequence, the id changes
    """
    label_pert = label_pert[1:] #get rid of ">"
    if seq_pert in label_dict.keys():
        if label_dict[seq_pert] != label_pert: #<-- check if \n at the end disrupts
            return False
    return True

#---- RUNNING, iterate over all 

for filename in os.listdir("perturb"):
    f = os.path.join("perturb", filename)
    # checking if it is a file
    if os.path.isfile(f) and filename.startswith("test_data_insert"): #specify what file
        with open(f) as f_pert:
            data = f_pert.readlines()
            odd_seq_index = []
            for i in range(0, len(data)-1, 2):
                if not is_label_same(data[i+1].strip(),
                                    data[i].strip()):
                    odd_seq_index.append(i)
        print([data[i] for i in odd_seq_index] )




""" --------------- Note to Self
Uniprot syntax:
Seq('MYAIIETGGKQIKVEAGQEIYVEKLAGEVGDVVTFDKVLFVGGDSAKVGVPFVD...INA')
sp|XXXX|...
^ start from 10

deepgoplus Sequence:
label starts with ">"

Already Checked:
import random
print(random.sample(label_dict.keys(), k=20))
print('DKGFGFITPADGSKDVFVHFSAIQSNDFKTLDEGQKVEFSIENGAK' in label_dict.keys()) #<-- True (obtained from sample)
print('DKGFGFITPADGSKDVFVHFSAIQSNDFKTLDEG' in label_dict.keys()) #<-- False

"""



""" INSTRUCTION
1-- Download uniprot_sprot.fasta.gz and put in same folder as script
2-- FIRST write this in script and run
from Bio import SeqIO
import gzip

label_dic = {}
with gzip.open("perturb\\uniprot_sprot.fasta.gz",'rt') as seq_bank:
    for record in SeqIO.parse(seq_bank, "fasta"):
        label_dic[record.seq] = record.id
with open('perturb\\saved_dictionary.pkl', 'wb') as f:
    pickle.dump(label_dic, f)

3-- To test script is running well, paste this at the top of test .fa file
>CSPA_YERENFAKE
DKGFGFITPADGSKDVFVHFSAIQSNDFKTLDEGQKVEFSIENGAK
    When run, this script should return index a list containing 0
"""
