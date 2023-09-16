import csv
import ast
from deep_translator import GoogleTranslator
from langdetect import detect
import json
import pandas as pd
import re
from .classifier_script import get_classification





def remove_duplicates_ignore_case(input_list):
    seen = set()
    unique_list = []
    for item in input_list:
        lower_item = item.lower()
        if lower_item not in seen:
            seen.add(lower_item)
            unique_list.append(item)
    return unique_list
    
def find_matching_classes(item, data):
    status = ""
    matching_classes = set()    
    for class_data in data:
        if item.lower() in [text.lower() for text in class_data["textList"]]:
            matching_classes.add(class_data["class"])      
    if len(list(matching_classes)) == 1 and item.lower()!="logic":
        if " " not in item:
            cpt=0
            for class_data in data:
                text_list = [text.lower() for text in class_data["textList"]]
                if any(item.lower()+" " in string.lower() or item.lower()+")" or string.lower().startswith(item.lower()) or string.lower().endswith(item.lower()) for string in text_list):
                    cpt +=1
                    matching_classes.add(class_data["class"])      
            if cpt>=2:
                status= "imposter"
    return matching_classes, status


def parse_list(s):
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        return []


def extract_interests_from_csv(file_path):
    data = []
    interests_data = {}
    with open(file_path, 'r', newline='',encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile,  delimiter=";")
        for row in reader:
            auth_id = row['auth_id'].strip()
            interests = parse_list(row["interests"])
            data.append({"auth_id": auth_id, "interests": interests})
            interests_data[auth_id] = interests
    df = pd.DataFrame(data)
    #print(df.shape)
    return df


def get_keys_with_values_above_threshold(email_data, email):
    print("here we go")
    print(email_data)
    keys_above_threshold = []
    for key, value in email_data.items():
        if value > 0.03:
            keys_above_threshold.append(key)
    return keys_above_threshold

def find_index_of_item(list_of_strings, search_string):
    try:
        index = list_of_strings.index(search_string)
        return index
    except ValueError:
        return -1

def process_data(matched, left_interests, auth_id, model_data):
    matched = [list(t) for t in matched]
    def matched_acm_class(aList, model_top_classes):
        voted_class = ""
        a = -1
        for k in aList: 
            my_ind = find_index_of_item(model_top_classes[::-1], k)
            if my_ind!=-1 and my_ind>a:
                a = my_ind
                new_class = model_top_classes[::-1]
                voted_class = new_class[my_ind]
        return voted_class
    
    matched_percentage = 0
    interests_percentage = 0
    percentages = {}
    model_top_classes =get_keys_with_values_above_threshold(model_data, auth_id)
    if len(matched) == 1: matched_percentage = 0.1
    elif len(matched) >= 2: matched_percentage = 0.2
    for index, x in enumerate(matched): 
        if len(x[1])>=3 and len(set(x[1])) == len(x[1]):
            unified_class = matched_acm_class(x[1], model_top_classes)
            matched[index][1] = {unified_class}
    list_classes = []
    list_items = []
    for x in matched:
        if len(list(x[1]))!=1 or list(x[1])[0] != '':
            list_classes.extend(list(x[1]))
            list_items.append(x[0])
        elif len(list(x[1]))==1 and list(x[1])[0] == '':
            left_interests.append("NNN_"+x[0])
    
    print("----------------------------------")
    print("auth_id: ", auth_id)
    #print("list_classes and items : ", list_classes, " ", list_items)
    #print("left interests: ", left_interests)
    interests_list = []
    for mot in left_interests:
        lang = detect(mot)
        if lang!="en":
            try: 
                mot = GoogleTranslator(source='auto', target='en').translate(mot) 
            except:
                print("Marconda")
        interests_list.append(mot)
    input_text = ", ".join(interests_list)
    model_result = get_classification(input_text)
    first_key = next(iter(model_result))
    first_value = model_result[first_key]
    print(first_key)
    pred_list = []

    weight_matched_keywords = len(list_items)
    weight_model_keywords = len(left_interests)
    confidence_model_keywords = first_key
    coeff_matched = {}
    for x in list_classes:
        coeff = 1
        if x.endswith("(2)"): 
            coeff = 0.5
            x = x.rstrip("(2)").strip()
        if x in coeff_matched:
            coeff_matched[x] += coeff
        else:
            coeff_matched[x] = coeff
    #if weight_matched_keywords!=0:
        #print("Weight of matched keywords : ", weight_matched_keywords)
        #print(coeff_matched)
    #if weight_model_keywords!=0:
        #print("Weight of model keywords : ", weight_model_keywords)
        #print(first_value, " : ", first_key)
    percentage_model = 0
    percentage_match = 0
    if weight_matched_keywords>=2: percentage_match = 0.15
    elif weight_matched_keywords==1: percentage_match = 0.1
    if weight_model_keywords >= 3 and first_value>=0.3 and first_value<0.5: percentage_model = 0.1
    elif weight_model_keywords >= 3 and first_value>=0.5 and first_value<0.7 : percentage_model = 0.12 
    elif weight_model_keywords >= 3 and first_value>=0.7: percentage_model = 0.15
    elif weight_model_keywords == 2: percentage_model = 0.05
    #print("percentage_match : ", percentage_match)
    #print("percentage_model : ", percentage_model)
    if percentage_match > 0:
        for x in coeff_matched:
            valeur = x
            poids = coeff_matched[x]
            final_percentage = (percentage_match * poids)/weight_matched_keywords
            percentages[x] = final_percentage
    if percentage_model>0:
        if first_key in percentages:
            percentages[first_key]+= percentage_model
        else:
            percentages[first_key]= percentage_model
    #print(percentages)    
    
    desired_data = {
        "auth_id": auth_id,
        "percentage": percentage_model + percentage_match,
        "values": [{key: value} for key, value in percentages.items()]
    }
    return desired_data
    
def get_teachers_interests_classes(auth_id, myinterests, model_data):    
    file_path = 'interests_unified.csv'
    #result = extract_interests_from_csv(file_path)
    with open("KB.json", 'r') as json_file:
        json_content = json.load(json_file)
        
        
    #with open("final_profiles_fixed.json", "r") as file:
    #    model_data = json.load(file)   
        
        
    #result = result.sort_values(by='auth_id')
    #result['interests'] = result['interests'].apply(lambda x: x if isinstance(x, list) else [x])
    #result = result.groupby('auth_id')['interests'].agg(lambda x: sum(x, [])).reset_index()
    #result['interests'] = result['interests'].apply(lambda lst: [item for item in lst if item != ""])
    cpt = 0
    cpt_inner = 0
    auth_list = []
    final_file = []
    
    imposter_list = []
    m_classes=[]
    interests_to_remove = []
    model_top_classes = get_keys_with_values_above_threshold(model_data, auth_id)
    interests = remove_duplicates_ignore_case(myinterests)
    for item in interests:
        original_item = item
        cpt_inner += 1
        lang = detect(item)
        if lang!="en":
            try: 
                item = GoogleTranslator(source='auto', target='en').translate(item) 
            except:
                print("Marconda")
        
        match_classes, status = find_matching_classes(item, json_content)
        if status == "imposter":
            imposter_list.append((item, original_item, match_classes))
        else:        
            if len(match_classes)!=0:
                interests_to_remove.append(original_item)
                if len(match_classes)==2: 
                    match_classes = set([string + "(2)" for string in match_classes])
                    
                m_classes.append((item, match_classes))
        interests = [x for x in interests if x not in interests_to_remove]
        
    result_list = [item for s in [second_element for _, second_element in m_classes] for item in s]
    for element in imposter_list:
        voted_class = ""
        a = 0
        for k in element[2]: 
            if result_list.count(k)>a:
                a = result_list.count(k)
                voted_class = k
        a=-1
        if voted_class == "":
            for k in element[2]: 
                my_ind = find_index_of_item(model_top_classes[::-1], k)
                if my_ind!=-1 and my_ind>a:
                    a = my_ind
                    new_class = model_top_classes[::-1]
                    voted_class = new_class[my_ind]
        if voted_class != "":
            interests.remove(element[1])
            m_classes.append((element[0], {voted_class}))
    desired_data = process_data(m_classes, interests, auth_id, model_data)
    final_file.append(desired_data)
        
    return final_file      

