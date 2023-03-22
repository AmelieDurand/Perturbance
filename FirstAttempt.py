import random

#initialize LIST of useless characters + char <--- GLOBAL
char_useless = list('BJOUXZ'.lower()) #<--- REMOVE lower() later
char_main = list('ACDEFGHIKLMNPQRSTVWY'.lower())

#Pass 1 sequence string here
#sequence = 'MFLLHEYDIFWAFLIIASLIPILAFWISALLAPVREGPEKLSSYESGIEPMGGAWLQFRIRYYMFALVFVVFDVETVFLYPWAMSFDVLGISVFIEAFIFVLILVVGLVYAWRKGALEWS'

#General insert randomly
def insert(sample,p=0.01, char_type=char_useless,spread=True):
  """ Randomly select a spot to insert ONE thing by concatenating in 3 parts
      take in noise as list"""
  noise_ls = gen_noise(sample,p,char_type,spread)
  sample = list(sample)
  while bool(noise_ls): #<--- noise_ls is random
    sample.insert(random.randint(1,len(sample)),noise_ls.pop()) #<-- MUST shuffle ls later
  return ''.join(sample)

def gen_noise(sample,p,char_type,spread): #<-- frequency probability 
  length = len(sample)
  noise_ls = random.choices(char_type, k=int(p*length))
  random.shuffle(noise_ls)
  return noise_ls

#DECIDE what to insert to one of specific case (TOTAL 8 cases)
# list of WHAT to insert: homogenous vs mixed
# Calculate HOW MANY to insert (frequency function of length): 0.1%, 1%, 10%

# decide HOW to insert (tgether or spread)

  

with open(".\\data\\train_data.fa",'r') as f:
    database = f.readlines()
p=0.01
f_out = open(f".\\perturb\\test_data_perturb_{str(p)}.fa",'w') #<------- Need to specify type of perturb
for i in range(0,len(database),2):
  f_out.write(database[i])
  f_out.write(insert(database[i+1]))  #<--- Fix: what if pass extra val to insert
f_out.close()
