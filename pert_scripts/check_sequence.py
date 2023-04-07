
import pickle

with open("perturb\\saved_dictionary.pkl", 'rb') as f:
    label_dict = pickle.load(f)

def is_label_same(seq_pert, label_pert):
    """
    Pass if given sequence, an id is not found
    Pass if given sequence, the id remains the same
    Alert if given seequence, the id changes
    """
    label_pert = label_pert[1:] #get rid of ">" at the start
    if seq_pert in label_dict.keys():
        if label_dict[seq_pert] != label_pert: #<-- check if \n at the end disrupts
            return False
    return True

#---- RUNNING
file_perturb = "perturb\\test_data_perturb_0.01aTrue.fa"
with open(file_perturb) as f_pert:
    data = f_pert.readlines()
    odd_seq = []
    for i in range(0, len(data), 2):
        if not is_label_same(data[i+1],data[i]):
            odd_seq.append(data[i])
        




""" --------------- Note to Self
Uniprot syntax:
Seq('MYAIIETGGKQIKVEAGQEIYVEKLAGEVGDVVTFDKVLFVGGDSAKVGVPFVD...INA')
sp|XXXX|...

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
2-- FIRST RUN
from Bio import SeqIO
import gzip

label_dic = {}
with gzip.open("perturb\\uniprot_sprot.fasta.gz",'rt') as seq_bank:
    for record in SeqIO.parse(seq_bank, "fasta"):
        label_dic[record.seq] = record.id
with open('perturb\\saved_dictionary.pkl', 'wb') as f:
    pickle.dump(label_dic, f)
"""
