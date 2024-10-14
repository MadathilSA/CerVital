import torch
import torch.nn as nn
from transformers import T5Tokenizer, T5EncoderModel
from torchvision import transforms
import json
import cv2
import os
from convnext import ConvNeXt  
from parsing import extract_json 
from datetime import datetime


class ClinicalFeaturesExtractor(nn.Module):
    def __init__(self):
        super(ClinicalFeaturesExtractor, self).__init__()
        self.encoder = T5EncoderModel.from_pretrained('google/flan-t5-small')
        self.feature_dim = 512

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        clinical_features = outputs.last_hidden_state[:, 0, :]
        return clinical_features

class Classifier(nn.Module):
    def __init__(self, input_dim, num_classes):
        super(Classifier, self).__init__()
        self.classifier = nn.Sequential(
            nn.Linear(input_dim, input_dim),
            nn.GELU(),
            nn.Linear(input_dim , input_dim),
            nn.GELU(),
            nn.Linear(input_dim, num_classes)
        )

    def forward(self, x):
        return self.classifier(x)

class MultimodalModel(nn.Module):
    def __init__(self, num_classes):
        super(MultimodalModel, self).__init__()
        self.visual_backbone = ConvNeXt(in_chans=3, num_classes=1536)  # Adapt based on convnext.py
        self.clinical_extractor = ClinicalFeaturesExtractor()
        self.visual_classifier = Classifier(self.visual_backbone.num_classes, num_classes)
        self.clinical_classifier = Classifier(self.clinical_extractor.feature_dim, num_classes)
        self.combined_classifier = Classifier(
            self.visual_backbone.num_classes + self.clinical_extractor.feature_dim, num_classes
        )

    def forward(self, images=None, input_ids=None, attention_mask=None):
        outputs = {}
        visual_features = self.visual_backbone(images) if images is not None else None
        clinical_features = self.clinical_extractor(input_ids, attention_mask) if input_ids is not None else None

        if visual_features is not None:
            outputs['visual_logits'] = self.visual_classifier(visual_features)
        if clinical_features is not None:
            outputs['clinical_logits'] = self.clinical_classifier(clinical_features)
        if visual_features is not None and clinical_features is not None:
            combined_features = torch.cat([visual_features, clinical_features], dim=1)
            outputs['combined_logits'] = self.combined_classifier(combined_features)

        return outputs


# Helper function to format clinical history
def format_clinical_text(clinical_data):
    base_date_str = clinical_data.get('date_colposcopie')
    base_date = datetime.strptime(base_date_str, "%Y-%m-%d") if base_date_str else None
    
    clinical_text = []
    for key, value in clinical_data.items():
        if key == 'date_colposcopie' or not value:
            continue
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                date = datetime.strptime(sub_key, "%Y-%m-%d")
                days_difference = (base_date - date).days if base_date else "N/A"
                clinical_text.append(f"{sub_value} : {days_difference}")
        else:
            days_difference = 0  # Default to 0 if no specific date provided
            clinical_text.append(f"{value} : {days_difference}")
    
    return " ".join(clinical_text)


def initialize_model(model_path, num_classes=5):
    model = MultimodalModel(num_classes=num_classes)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    return model


def inference(docx_file_path, model, output_json_path, output_images_dir):
    clinical_data, image_paths = extract_json(docx_file_path, output_json_path, output_images_dir)

    clinical_text = format_clinical_text(clinical_data)

    tokenizer = T5Tokenizer.from_pretrained('google/flan-t5-small')
    encoding = tokenizer(
        clinical_text, padding='max_length', truncation=True, max_length=2048, return_tensors='pt'
    )

    transform = transforms.Compose([
        transforms.Resize(224),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    preprocessed_images = [transform(cv2.imread(image_path)) for image_path in image_paths]
    preprocessed_images = torch.stack(preprocessed_images)

    with torch.no_grad():
        outputs = model(
            images=preprocessed_images,
            input_ids=encoding['input_ids'],
            attention_mask=encoding['attention_mask']
        )
        
    predictions = {}
    if 'visual_logits' in outputs:
        _, predicted_label_visual = outputs['visual_logits'].max(1)
        predictions['visual'] = predicted_label_visual.item()
    if 'clinical_logits' in outputs:
        _, predicted_label_clinical = outputs['clinical_logits'].max(1)
        predictions['clinical'] = predicted_label_clinical.item()
    if 'combined_logits' in outputs:
        _, predicted_label_combined = outputs['combined_logits'].max(1)
        predictions['combined'] = predicted_label_combined.item()

    prediction_output = {
        "Visual Only Prediction": predictions.get('visual', 'N/A'),
        "Clinical Only Prediction": predictions.get('clinical', 'N/A'),
        "Combined Prediction": predictions.get('combined', 'N/A')
    }
    
    with open(output_json_path.replace(".json", "_predictions.json"), 'w') as f:
        json.dump(prediction_output, f)

    return prediction_output, preprocessed_images


# Example Usage
model_path = 'model_checkpoint.pth'
model = initialize_model(model_path)  # Load the model once

# Inference on a specific document
docx_file_path = 'data.docx'
output_json_path = 'output/data.json'
output_images_dir = 'output/images'
predictions, processed_images = inference(docx_file_path, model, output_json_path, output_images_dir)
print(predictions)
