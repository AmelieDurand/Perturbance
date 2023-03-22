import random

#initialize LIST of useless characters + main
char_useless = list('BJOUXZ'.lower()) #<--- REMOVE lower() later
char_main = list('ACDEFGHIKLMNPQRSTVWY'.lower())

#sequence = 'MFLLHEYDIFWAFLIIASLIPILAFWISALLAPVREGPEKLSSYESGIEPMGGAWLQFRIRYYMFALVFVVFDVETVFLYPWAMSFDVLGISVFIEAFIFVLILVVGLVYAWRKGALEWS'

def insert(sample,p=0.01, char_type=char_useless,spread=True):
  """ Randomly select a spot to insert noise by breaking up sequence to list"""
  noise_ls = gen_noise(sample,p,char_type,spread)
  sample = list(sample)
  while bool(noise_ls): #<--- noise_ls is random, perform until noise_ls empty
    sample.insert(random.randint(1,len(sample)),noise_ls.pop()) 
  return ''.join(sample)

def gen_noise(sample,p,char_type,spread): #<-- frequency probability 
  """
  DECIDE what to insert to one of specific case (TOTAL 12 variations)
  --list of WHAT to insert: homogenous vs mixed
  --calculate HOW MANY to insert (frequency function of length): 0.1%, 1%, 10%
  --decide HOW to insert (together or spread)
  """
  length = len(sample)
  noise_ls = random.choices(char_type, k=int(p*length))
  if not spread:
    return [''.join(noise_ls)] #<--- Noise all bunched up
  random.shuffle(noise_ls)
  return noise_ls



  

with open(".\\data\\train_data.fa",'r') as f:
    database = f.readlines()
p=0.01
f_out = open(f".\\perturb\\test_data_perturb_{str(p)}.fa",'w') #<------- Need to specify type of perturb
for i in range(0,len(database),2):
  f_out.write(database[i])
  f_out.write(insert(database[i+1]))  
f_out.close()
