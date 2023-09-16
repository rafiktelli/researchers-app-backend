from .classifier_script import get_classification
import pandas as pd
import json
import re
from deep_translator import GoogleTranslator
from langdetect import detect

def give_coeff_contribution(a, b):
    if a == None: return 1
    if a == 1: return 1 
    switch_cases = {
        2: {2: 0.8},
        3: {2: 0.7, 3: 0.5},
        4: {2: 0.6, 3: 0.4, 4:0.2}
    }
    if b>4:
        b=4
        if a>4: a=4
    if b in switch_cases:
        inner_switch = switch_cases[b]
        if a in inner_switch:
            return inner_switch[a]

def get_the_author_order(order):
    print(order)
    if order == "nan" or order=="nothing": return None, None
    pattern = r"\((\d+(\.\d+)?)/(\d+(\.\d+)?)\)"  # Define the regex pattern

    match = re.search(pattern, order)

    if match:
        number1 = match.group(1)
        number2 = match.group(3)
        return float(number1), float(number2)
    else:
        return None, None
    return None, None


# Here it begins
def generate_profile(auth_id, group):
    modified_probs = {}
    nb_pubs_max = 50
    alpha = 0.5
    pubs_proba = []
    num_rows = 0
    class_probabilities_sum = {}
    list_coeff = []
    nb_pubs = min( len(group) ,nb_pubs_max)
    print("nombre de publication de : ", auth_id ," est : ", nb_pubs)
    nb_titles = 0
      
    for _, row in group.iterrows():
        order = row['order']
        a, b = get_the_author_order(order)
        coeff = give_coeff_contribution(a, b)
        print(row['title'])
        print("the other ", row['auth_id'] ," was ranked ", a, " over ", b , " authors. He got a coefficient of : ", coeff)
        
        
        if num_rows >= nb_pubs_max:
            break
            
        abstract = str(row['abstract'])
        if pd.notna(row['title']): 
            title = str(row['title'])
        else: 
            title = ''
        if row['source']!='dblp' and pd.notna(row['journal']): 
            journal=str(row['journal'])
        else: 
            journal = ''
        if pd.notna(abstract):  
            input_text = str(title)+". "+str(abstract)+". "+str(journal)
        else:  
            input_text = str(title)+ ". "+str(journal)
            nb_titles += 1
        try:
            lang = detect(input_text)
        except:
            lang = "en"
        if lang!="en":
            try: 
                input_text = GoogleTranslator(source='auto', target='en').translate(input_text) 
                print("not english, it is : ", lang)
                print(input_text)
            except:
                print("Marconda")
        class_probabilities = get_classification(input_text[:min(len(input_text), 1350)])
        print(row['title'])
        print(class_probabilities)
        pubs_proba.append(class_probabilities)
        if pd.notna(abstract): 
            new_proba = 1 * coeff
            list_coeff.append(1*coeff)
        else:
            new_proba = alpha * coeff
            list_coeff.append(alpha*coeff)
        for class_name, probability in class_probabilities.items():
            class_probabilities_sum[class_name] = class_probabilities_sum.get(class_name, 0) + probability * new_proba

        num_rows += 1
    #averaged_probabilities = {class_name: prob_sum / ( (alpha*nb_titles + (num_rows-nb_titles))) for class_name, prob_sum in class_probabilities_sum.items()}
    print(list_coeff)
    averaged_probabilities = {class_name: prob_sum / ( sum(list_coeff) ) for class_name, prob_sum in class_probabilities_sum.items()}

    sorted_averaged_probabilities = dict(sorted(averaged_probabilities.items(), key=lambda item: item[1], reverse=True))

    max_prob = max(sorted_averaged_probabilities.values())

    modified_probabilities = {class_name: 1.0 if v == max_prob else v / max_prob for class_name, v in sorted_averaged_probabilities.items()}
    modified_probabilities = sorted_averaged_probabilities
    modified_probs[auth_id] = modified_probabilities
    print(modified_probs)
    return pubs_proba, modified_probabilities, list_coeff
'''
with open("final_profiles_fixed.json", "w") as json_file:
    json.dump(modified_probs, json_file, indent=4)

for auth_id, modified_probabilities in modified_probs.items():
    print(f"Author ID: {auth_id}")
    for class_name, probability in modified_probabilities.items():
        print(f"{class_name}: {probability}")
    print()
    
'''