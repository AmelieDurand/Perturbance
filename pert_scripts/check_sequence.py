
from Bio import SeqIO
import pickle
import gzip
import random

with open("perturb\\saved_dictionary.pkl", 'rb') as f:
    label_dict = pickle.load(f)
print(random.sample(label_dict.keys(), k=1))
print('DKGFGFITPADGSKDVFVHFSAIQSNDFKTLDEGQKVEFSIENGAK' in label_dict.keys())
print('DKGFGFITPADGSKDVFVHFSAIQSNDFKTLDEG' in label_dict.keys())


"""
Structure:
Seq('MYAIIETGGKQIKVEAGQEIYVEKLAGEVGDVVTFDKVLFVGGDSAKVGVPFVD...INA')
sp|XXXX|...
"""

"""

with gzip.open("uniprot_sprot.fasta.gz",'rt') as seq_bank:
    for record in SeqIO.parse(seq_bank, "fasta"):
        print(record.id)
        

fasta_sequences = SeqIO.parse(open(".\\data\\test_data.fa"),'fasta')
#with open('test.txt') as out_file:
for fasta in fasta_sequences:
    name, sequence = fasta.id, str(fasta.seq)
    print(name)
    #new_sequence = some_function(sequence)
    #write_fasta(out_file)
"""
# Access Bio package (installed)
# Access python file to check


"""------ FINISHED RUNNING
label_dic = {}
with gzip.open("perturb\\uniprot_sprot.fasta.gz",'rt') as seq_bank:
    for record in SeqIO.parse(seq_bank, "fasta"):
        label_dic[record.seq] = record.id

with open('perturb\\saved_dictionary.pkl', 'wb') as f:
    pickle.dump(label_dic, f)
"""