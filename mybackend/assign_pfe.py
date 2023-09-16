import json
import numpy as np
from scipy.spatial.distance import cosine
from classifier_script import get_classification
from deep_translator import GoogleTranslator
from langdetect import detect


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
    
    return top_similarities


# Assuming your JSON file containing profiles is named "profiles.json"
json_file_path = "final_profiles_fixed.json"

# Assuming you have the `get_classification` function defined

# Load profiles data from the JSON file
profiles_data = load_profiles(json_file_path)

# Example input text
input_text = input("Enter a value: ")

lang = detect(input_text)
if lang!="en":
    try: 
        input_text = GoogleTranslator(source='auto', target='en').translate(input_text) 
        print("not english, it is : ", lang)
        print(input_text)
    except:
        print("Marconda")


# Call the function to find top similar profiles
top_similarities = find_top_similar_profiles(input_text, profiles_data)

# Print the results
for i, (profile_email, similarity) in enumerate(top_similarities, 1):
    print(f"{i}. Profile: {profile_email}, Similarity: {similarity:.4f}")
