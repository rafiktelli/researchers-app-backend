from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import AutoConfig
import torch

def classify_text(text, model, tokenizer, id2label):
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=1)
    predicted_class_id = torch.argmax(probabilities, dim=1).item()
    predicted_class_name = id2label[predicted_class_id]
    class_probabilities = {id2label[i]: prob.item() for i, prob in enumerate(probabilities[0])}
    sorted_class_probabilities = {k: v for k, v in sorted(class_probabilities.items(), key=lambda item: item[1], reverse=True)}

    return predicted_class_name, sorted_class_probabilities

def get_classification(input_text):
    model_path = "C:/F/django-app/mybackend/mybackend/extract/create_profile/23_classes_ACM_66"
    
    model_config = AutoConfig.from_pretrained(model_path)

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)

    predicted_class, class_probabilities = classify_text(input_text, model, tokenizer, model_config.id2label)

    
    return class_probabilities