## How to run check_sequence.py

1-- Download uniprot_sprot.fasta.gz and put in same folder as script (pert_scripts)

2-- FIRST write this in script and run
```
from Bio import SeqIO
import gzip

label_dic = {}
with gzip.open("pert_scripts\\uniprot_sprot.fasta.gz",'rt') as seq_bank:
    for record in SeqIO.parse(seq_bank, "fasta"):
        label_dic[record.seq] = record.id
with open('pert_scripts\\saved_dictionary.pkl', 'wb') as f:
    pickle.dump(label_dic, f)
```

3-- To test script is running well, paste this at the top of test .fa file. When run, this script should return a list containing 0
```
>CSPA_YERENFAKE
DKGFGFITPADGSKDVFVHFSAIQSNDFKTLDEGQKVEFSIENGAK
```
    
