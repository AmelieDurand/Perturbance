from random import randint, choice, choices
#initialize LIST of useless characters <--- GLOBAL
# for each: letter, number, special char
num = [0,1]
char = list('bjouxz')

sample = 'MFLLHEYDIFWAFLIIASLIPILAFWISALLAPVREGPEKLSSYESGIEPMGGAWLQFRIRYYMFALVFVVFDVETVFLYPWAMSFDVLGISVFIEAFIFVLILVVGLVYAWRKGALEWS'

#General insert randomly
def insert1(noise):
  """ Randomly select a spot to insert ONE thing by concatenating in 3 parts"""
  try:
    assert type(noise) is str
    
    i = randint(1, len(sample))
    return sample[:i] + noise + sample[i:]
  except:
    print('noise input should be STRING')

#DECIDE what to insert to one of specific case (TOTAL 8 cases)
# list of WHAT to insert
# Calculate HOW MANY to insert (frequency)
# decide HOW to insert (tgether or spread)
def spread_insert(noise_ls):
  noise_ls = choices(char, k=5)
  


print(insert1(choice(char)))
