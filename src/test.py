import re
import string
 
text = "test text is {very {good|bad}|{good|bad}} at its job"
desired_text = "test text is {very good|very bad|good|bad} at its job"

def gen_phrases(s):
    exclude = set(string.punctuation) - set([' ', '|', '{', '}'])
    s = ''.join(ch for ch in s.lower() if ch not in exclude)
    crude_split = re.split("\{(.+?)\}", s)
    return [x.split("|") for x in crude_split if x.strip() != ""]
    
    
count = 0
in_spin_group = False
spin_start = -1
spin_end = -1
dividers = []
for i, ch in enumerate(text):
    if ch == "{":
        if count == 0:
            in_spin_group = True
            spin_start = i
        count += 1
    if ch == "}":
        if count == 1:
            spin_end = i
        count -= 1
    if ch == "|" and count == 1:
        dividers.append(i)
    # Found end of spin group
    if in_spin_group and count == 0:
        print "SPIN GROUP FROM {0} to {1}, DIVIDERS AT {2}".format(spin_start, spin_end, dividers)
        in_spin_group = False
        spin_start = -1
        spin_end = -1
        dividers = []
        
    
    