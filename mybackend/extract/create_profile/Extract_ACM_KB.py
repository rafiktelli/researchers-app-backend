import csv
import json

def read_csv(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            data_uri = str(row[0])
            text = row[1]
            data.append((data_uri, text))
    return data

def extract_other_IS(data):
    text_list = [text for data_uri, text in data if "10002951" in data_uri and "10002951.10003317" not in data_uri and "10002951.10002952" not in data_uri and "10002951.10003227.10003351" not in data_uri]
    return text_list

def extract_other_AI(data): 
    text_list = [text for data_uri, text in data if "10010147.10010178" in data_uri and "10010147.10010178.10010179" not in data_uri and "10010147.10010178.10010219" not in data_uri and "10010147.10010178.10010224" not in data_uri]
    print(len(text_list))
    return text_list
 
    print(len(text_list))
def generate_json(classes, data):
    result = []
    for class_text in classes:
        class_data_uris = [str(data_uri) for data_uri, text in data if text == class_text]
        text_list = [text for data_uri, text in data if class_data_uris[0] in data_uri  ]
        class_item = {
            "class": class_text,
            "data-uri": class_data_uris[0],
            "textList": text_list
        }
        result.append(class_item)
    
    otherISList = extract_other_IS(data)
    class_item = {
        "class": "other.IS",
        "data-uri": "nothing",
        "textList": otherISList
    }
    result.append(class_item)
    
    otherAIList = extract_other_AI(data)
    class_item = {
        "class": "other.AI",
        "data-uri": "nothing",
        "textList": otherAIList
    }
    result.append(class_item)
    
    
    return result

def main():
    csv_file_path = 'acm.csv'
    data = read_csv(csv_file_path)

    classes = [ "Machine learning", "Information retrieval", "Data mining", "Data management systems", "Natural language processing", "Mathematics of computing", "Theory of computation", "Computer vision", "Social and professional topics", "Modeling and simulation", "Security and privacy", "Software organization and properties", "Distributed artificial intelligence", "Computer systems organization", "Hardware", "Computer graphics", "Networks", "Human-centered computing", "Software notations and tools", "Software creation and management" ]

    json_data = generate_json(classes, data)
    with open('other_output.json', 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, indent=2)

if __name__ == "__main__":
    main()
