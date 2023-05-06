import pickle
import random
import pandas as pd
import os
from Bio import SeqIO
import gzip

#issue: RS23B not accepted for RS23A

""" <--- UNCOMMENT IF RUNNING FIRST TIME
label_dic = {}
with gzip.open("pert_scripts\\uniprot.gz",'rt') as seq_bank:
    for record in SeqIO.parse(seq_bank, "fasta"):
        label = record.id #Try split with "|"
        label = label.split('|')[-1]
        label = label.split('_')[0]
        label_dic[record.seq] = label
    # Overwrite labels from test file    
    with open("data\\test_data.fa") as f:
        fa_file = f.readlines()
        for i in range(0, len(fa_file) - 1, 2):
            label_temp = fa_file[i][1:].strip()
            label = label.split('_')[0]
            seq_temp = fa_file[i+1].strip()
            label_dic[seq_temp] = label_temp

    with open('pert_scripts\\uniprot_canon_fixed.pkl', 'wb') as f:
        pickle.dump(label_dic, f)
"""   


with open(os.path.join("pert_scripts", "uniprot_canon_fixed.pkl"), "rb") as f:
    uniprot_dict = pickle.load(f)

print(random.sample(uniprot_dict.items(), k=4)) #<--- Check formatting

assert "DKGFGFITPADGSKDVFVHFSAIQSNDFKTLDEGQKVEFSIENGAK" in uniprot_dict.keys()
assert uniprot_dict["DKGFGFITPADGSKDVFVHFSAIQSNDFKTLDEGQKVEFSIENGAK"] == "CSPA"


def is_label_same(seq_pert, label_pert):
    """
    Pass if given sequence, an id is not found
    Pass if given sequence, the id remains the same
    Alert if given seequence, the id changes
    """
    label_pert = label_pert[1:]  # get rid of ">"
    label_pert = label_pert.split('_')[0]
    if seq_pert in uniprot_dict.keys():
        if uniprot_dict[seq_pert] != label_pert:  # <-- check if \n at the end disrupts
            return True, False 
        else: 
            return True, True
    return False, False

def val_to_key(thing_to_search):
    """_summary_

    Args:
        thing_to_search (_type_): _description_

    Returns:
        _type_: _description_
    """
    thing_to_search = thing_to_search.strip()
    keys = [k for k, v in uniprot_dict.items() if v==thing_to_search]
    print(keys)
    return keys

def main():
    # ---- RUNNING, iterate over all
    print(len(uniprot_dict.keys()))
    perturb_file_master = []
    for root, dirs, files in os.walk("perturb", topdown=False):
        for name in files:
            perturb_file_master.append(os.path.join(root, name))
    for f in perturb_file_master:
        with open(f) as f_pert:
            test_file = f_pert.readlines()
            
            seq_unfound = [] 
            seq_label_change = []

            for i in range(1, len(test_file) - 1, 2): #!! EMPTY LINE at beginning
                be_there, match = is_label_same(test_file[i + 1].strip(), test_file[i].strip())
                if be_there and not match:
                    seq_label_change.append(i)
                elif not be_there:
                    seq_unfound.append(i)              
        
        print(f'#sequence where label changed (/3875): {len(seq_label_change)}')
        print(f'#sequence not found (/3875): {len(seq_unfound)}')
        df = pd.DataFrame({
        "label changes (index)": seq_label_change,
        "label in test file": [test_file[i].strip()[1:] for i in seq_label_change],
        "label in uniprot": [uniprot_dict[test_file[i+1].strip()] for i in seq_label_change], 
        })
        if not df.empty: print(df)

if __name__ == '__main__':
    main()

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
2-- FIRST write this in script and run
from Bio import SeqIO
import gzip

label_dic = {}
with gzip.open("pert_scripts\\uniprot.gz",'rt') as seq_bank:
    for record in SeqIO.parse(seq_bank, "fasta"):
        label_dic[record.seq] = record.id
with open('pert_scripts\\uniprot_canon.pkl', 'wb') as f:
    pickle.dump(label_dic, f)
"""
