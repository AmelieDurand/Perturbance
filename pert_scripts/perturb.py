import random

#initialize LIST of useless characters + char <--- GLOBAL
char_useless = list('BJOUXZ') #<--- REMOVE lower() later
char_main = list('ACDEFGHIKLMNPQRSTVWY')

#Pass 1 sequence string here
#sequence = 'MFLLHEYDIFWAFLIIASLIPILAFWISALLAPVREGPEKLSSYESGIEPMGGAWLQFRIRYYMFALVFVVFDVETVFLYPWAMSFDVLGISVFIEAFIFVLILVVGLVYAWRKGALEWS'

#General insert randomly
def insert(sample,p, char_type,spread):
  """ Randomly select a spot to insert ONE thing by concatenating in 3 parts
      take in noise as list"""
  noise_ls = gen_noise(sample,p,char_type,spread)
  sample = list(sample)
  while bool(noise_ls): #<--- noise_ls is random
    sample.insert(random.randint(1,len(sample)),noise_ls.pop()) #<-- MUST shuffle ls later
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

  

with open(".\\data\\test_data.fa",'r') as f:
    database = f.readlines()

# CHANGE THE OPTIONS HERE
p=0.01
char_type= char_main
spread=True

f_out = open(f".\\perturb\\test_data_perturb_{str(p)+char_type[0]+str(spread)}.fa",'w') 


for i in range(0,len(database),2):
  f_out.write(database[i])
  f_out.write(insert(database[i+1],p,char_type,spread))  
f_out.close()
