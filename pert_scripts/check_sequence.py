import pickle
import random
import pandas as pd
import os
from Bio import SeqIO
import gzip
"""
label_dic = {}
with gzip.open("pert_scripts\\uniprot.gz",'rt') as seq_bank:
    for record in SeqIO.parse(seq_bank, "fasta"):
        label = record.id #Try split with "|"
        label = label.split('|')[-1]
        label_dic[record.seq] = label
with open('pert_scripts\\uniprot_canon.pkl', 'wb') as f:
    pickle.dump(label_dic, f)
"""
with open(os.path.join("pert_scripts", "uniprot_canon.pkl"), "rb") as f:
    uniprot_dict = pickle.load(f)

#print(random.sample(uniprot_dict.items(), k=4)) <--- Check formatting

assert "DKGFGFITPADGSKDVFVHFSAIQSNDFKTLDEGQKVEFSIENGAK" in uniprot_dict.keys()
assert uniprot_dict["DKGFGFITPADGSKDVFVHFSAIQSNDFKTLDEGQKVEFSIENGAK"] == "CSPA_YEREN"


def is_label_same(seq_pert, label_pert):
    """
    Pass if given sequence, an id is not found
    Pass if given sequence, the id remains the same
    Alert if given seequence, the id changes
    """
    label_pert = label_pert[1:]  # get rid of ">"
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
    for filename in os.listdir("perturb"):
        f = os.path.join("perturb", filename)
        # checking if it is a file
        if os.path.isfile(f) and filename.startswith(
            "test.fa"
        ):  # specify what file
            with open(f) as f_pert:
                test_file = f_pert.readlines()
                
                seq_unfound = [] 
                seq_label_change = []

                for i in range(0, len(test_file) - 1, 2):
                #for i in [14, 46, 86, 126, 180, 190, 212, 266]:
                    be_there, match = is_label_same(test_file[i + 1].strip(), test_file[i].strip())
                    if be_there and not match:
                        seq_label_change.append(i)
                    elif not be_there:
                        seq_unfound.append(i)              
            # print(seq_label_change)
            # print([test_file[i].strip() for i in seq_label_change])
            dict_return = []
            for i in seq_label_change:
                seq = test_file[i + 1].strip()
                dict_return.append(uniprot_dict[seq])
            # print(dict_return)
            # print(seq_label_change)
            print(f'#sequence where label changed: {len(seq_label_change)}')
            print(f'#sequence not found: {len(seq_unfound)}')
    df = pd.DataFrame({
        "label changes (index)": seq_label_change,
        "label in test file": [test_file[i].strip()[1:] for i in seq_label_change],
        "label in uniprot": dict_return, 
        })
    print(df)
if __name__ == '__main__':
    main()

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
with gzip.open("pert_scripts\\uniprot.gz",'rt') as seq_bank:
    for record in SeqIO.parse(seq_bank, "fasta"):
        label_dic[record.seq] = record.id
with open('pert_scripts\\uniprot_canon.pkl', 'wb') as f:
    pickle.dump(label_dic, f)

3-- To test script is running well, paste this at the top of test .fa file
>CSPA_YERENFAKE
DKGFGFITPADGSKDVFVHFSAIQSNDFKTLDEGQKVEFSIENGAK
    When run, this script should return index a list containing 0
"""
