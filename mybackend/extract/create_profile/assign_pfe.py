import json
import numpy as np
from scipy.spatial.distance import cosine
from .classifier_script import get_classification
from deep_translator import GoogleTranslator
from langdetect import detect
import ast

def load_profiles(file_path):
    with open(file_path, 'r') as file:
        profiles_data = json.load(file)
    return profiles_data

def calculate_cosine_similarity(input_vector, profile_vector):

    return 1 - cosine(input_vector.flatten(), profile_vector.flatten())
    

def normalize_vector(vector, all_keys, isInput, keep_top_n=3):
    # Sort the input vector in descending order by values and keep only the top n elements
    if isInput:
        sorted_items = sorted(vector.items(), key=lambda item: item[1], reverse=True)[:keep_top_n]
    else:
        sorted_items = sorted(vector.items(), key=lambda item: item[1], reverse=True)
    
    if isInput:
        print(sorted_items)
    # Create a dictionary with all keys set to 0
    normalized_vector = {key: 0.0 for key in all_keys}
    
    # Update the values in the normalized vector
    for key, value in sorted_items:
        normalized_vector[key] = value
        
    return np.array(list(normalized_vector.values()))

def find_top_similar_profiles(input_text, profiles_data):
    class_probabilities = get_classification(input_text)
    print("hahooowaaa :" )
    
    # Get all research areas (keys) from the profiles
    all_keys = set().union(*(profile.keys() for profile in profiles_data.values()))
    
    # Normalize the input vector and keep only the top 3 biggest values
    w = True
    input_vector = normalize_vector(class_probabilities, all_keys, True, keep_top_n=23 )
    print(input_vector)
    profile_similarities = []
    
    w = False
    for profile_email, profile_vector in profiles_data.items():
        profile_vector = normalize_vector(profile_vector, all_keys, False, keep_top_n=3)
        similarity = calculate_cosine_similarity(input_vector, profile_vector)
        profile_similarities.append((profile_email, similarity))
    
    profile_similarities.sort(key=lambda x: x[1], reverse=True)
    top_similarities = profile_similarities[:12]
    
    return top_similarities, profile_similarities


def get_top_sim(input_text, profiles_data):
    #json_file_path = "final_profiles_fixed.json"
    
    print(profiles_data)

    #profiles_data = load_profiles(json_file_path)

    #input_text = input("Enter a value: ")

    lang = detect(input_text)
    if lang!="en":
        try: 
            input_text = GoogleTranslator(source='auto', target='en').translate(input_text) 
            print("not english, it is : ", lang)
            print(input_text)
        except:
            print("Marconda")
    
    subject_classes = get_classification(input_text)
    sorted_data = sorted(subject_classes.items(), key=lambda x: x[1], reverse=True)

    top_3_elements = sorted_data[:3]
    
    top_similarities, all_sim = find_top_similar_profiles(input_text, profiles_data)
    print(all_sim)
    return all_sim, top_3_elements
    #for i, (profile_email, similarity) in enumerate(top_similarities, 1):
    #    print(f"{i}. Profile: {profile_email}, Similarity: {similarity:.4f}")

def get_sim_profiles(subject_classes, profiles_data):
    print(profiles_data)
    new = json.loads(subject_classes)
    print(new)
    sorted_data = sorted(new.items(), key=lambda x: x[1], reverse=True)
    class_probabilities = sorted_data
    all_keys = set().union(*(profile.keys() for profile in profiles_data.values()))
    print(class_probabilities)
    w = True
    class_probabilities = {item[0]: item[1] for item in class_probabilities}
    input_vector = normalize_vector(class_probabilities, all_keys, True, keep_top_n=23 )
    print(input_vector)
    profile_similarities = []
    
    w = False
    print(profiles_data)
    for profile_email, profile_vector in profiles_data.items():
        
        profile_vector = normalize_vector(profile_vector, all_keys, False, keep_top_n=3)
        similarity = calculate_cosine_similarity(input_vector, profile_vector)
        profile_similarities.append((profile_email, similarity))
    
    profile_similarities.sort(key=lambda x: x[1], reverse=True)
    top_similarities = profile_similarities[:4]
    return top_similarities
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    print(all_sim)
    return top_3_elements
    
    
