
import pickle
import random

with open("pert_scripts\\labels_uniprot.pkl", 'rb') as f:
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

#---- RUNNING
file_perturb = "perturb\\test_data_perturb_1.0ATrue.fa"
with open(file_perturb) as f_pert:
    data = f_pert.readlines()
    odd_seq_index = []
    for i in range(0, len(data)-1, 2):
        if not is_label_same(data[i+1].strip(),
                             data[i].strip()):
            odd_seq_index.append(i)
print(odd_seq_index)




""" Note on Uniprot Syntax
Seq('MYAIIETGGKQIKVEAGQEIYVEKLAGEVGDVVTFDKVLFVGGDSAKVGVPFVD...INA')
sp|XXXX|...
^ start from 10

deepgoplus Sequence:
label starts with ">"
"""


