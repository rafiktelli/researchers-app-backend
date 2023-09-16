import json

def process_json_files(auth_id, values_dict, entry):
    print("/////////////////////////////////////////////////////////////")
    print(auth_id)
    print(values_dict)
    print(entry)
    print("/////////////////////////////////////////////////////////////")
    
    result_list = []
    if entry[0]['auth_id'] == auth_id:
        percentage = entry[0]['percentage']
        values = entry[0]['values']
        x = 1 - percentage

        for k, v in values_dict.items():
            values_dict[k] = v * x

        for value_entry in values:
            for k, v in value_entry.items():
                if k in values_dict:
                    values_dict[k] += v

        print(f"Auth_id: {auth_id}")
        print("Modified Values:")
        values_dict = dict(sorted(values_dict.items(), key=lambda item: item[1], reverse=True))
        result_list.append({auth_id: values_dict})
        print("\n")
           

    return values_dict