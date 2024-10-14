import os
import json
import cv2
import numpy as np
import re
import warnings
from docx2python import docx2python
import win32com.client as win32
from win32com.client import constants
from datetime import datetime

warnings.filterwarnings("ignore")

def extract_json(file_path, output_json_path, output_images_dir):
    def treat_value_biopsie(value):
        keys_permitted_apart_CIN = ["Cancer", "Normale", "Dystrophie", "Adénocarcinome"]
        CIN_List = ["CIN1", "CIN2", "CIN3"]
        T = [False] * 3
        did_find = False
        for i in range(len(CIN_List)):
            if CIN_List[i].lower() in value.lower():
                did_find = True
                T[i] = True
        if did_find:
            return "".join([CIN_List[i] + " " for i in range(3) if T[i]]).strip().upper()
        else:
            for key in keys_permitted_apart_CIN:
                if key.lower() in value.lower():
                    return key.upper()
            if any(keyword.lower() in value.lower() for keyword in ["MMI", "ECTROPION"]):
                return "NORMALE"
        return ""
    
    def treat_geno_str(string_0):
        if all(keyword in string_0.upper() for keyword in ["NON", "16", "18", "45"]):
            return "NON.16.18.45"
        elif all(keyword in string_0.upper() for keyword in ["NON", "16", "18"]):
            return "NON.16.18"
        else:
            numbers = ["16", "18", "31", "33", "45", "52", "58"]
            result = ".".join([el for el in numbers if el in string_0])
            return result

    def preprocessing_frottis(frotti):
        frottis_class = ["Normale", "ASC-US", "L-SIL", "H-SIL", "ASC-H", "AGC", "Cancer"]
        result = " ".join([el.upper() for el in frottis_class if el.upper() in frotti.upper()])
        return result

    def preprocessing_HPV(HPV):
        HPV_list = [
            'Positif IHC', 'Positif ARNM', 'Positif HC', 'Positif ARN', 'Positif PERSISTANT', 
            'Positif HIS', 'Positif', 'Négatif IHC NEG', 'Négatif IIHC', 'Négatif IHC', 'Négatif'
        ]
        if HPV.upper() == 'Positif ARN M'.upper():
            return 'Positif ARNM'
        for el in HPV_list:
            if el.upper() in HPV.upper():
                return el.upper()
        return ''
    
    def save_as_docx(path, target_path):
        word = win32.gencache.EnsureDispatch('Word.Application')
        doc = word.Documents.Open(path)
        doc.Activate()
        word.ActiveDocument.SaveAs(target_path, FileFormat=constants.wdFormatXMLDocument)
        doc.Close(False)

    def treat_date(date):
        date_split = date.split("/")
        if len(date_split) == 1:
            return date_split[0]
        elif len(date_split) == 2:
            return f"{date_split[1]}-{date_split[0]}"
        elif len(date_split) == 3:
            return f"{date_split[2]}-{date_split[1]}-{date_split[0]}"
        return ""
    
    # Load DOCX file and convert to temp DOCX format
    directory = os.path.dirname(__file__)
    target_path = os.path.join(directory, "temp", "temp.docx")
    save_as_docx(file_path, target_path)
    doc_result = docx2python(target_path)

    historical_information = {"Vaccin": False}
    output = {
        "Frottis": {}, "HPV": {}, "Biopsie": {}, "Erad": {}, "Vaccin": "", 
        "Age": "40", "date_colposcopie": "2022-11-31"
    }

    # Extract information
    for el in list(doc_result.body):
        for el_1 in el:
            for el_2 in el_1:
                for el_3 in el_2:
                    if "GARDASIL" in el_3:
                        historical_information["Vaccin"] = True
                        
                    # Process keys and motif consultations as per your second file logic
                    for key in ["Frottis", "HPV", "Biopsie"]:
                        processed_value = None
                        if key == "Frottis":
                            processed_value = preprocessing_frottis(el_3)
                        elif key == "HPV":
                            processed_value = preprocessing_HPV(el_3)
                        elif key == "Biopsie":
                            processed_value = treat_value_biopsie(el_3)
                        
                        if processed_value:
                            output[key][treat_date(historical_information.get("Date", "2022-11-31"))] = processed_value

    # Set additional fields for the output JSON
    output["Vaccin"] = "oui" if historical_information["Vaccin"] else "non"
    if "AGE" in historical_information:
        output["Age"] = historical_information["AGE"]
    if "Date" in historical_information:
        output["date_colposcopie"] = treat_date(historical_information["Date"])

    # Save JSON data
    with open(output_json_path, 'w') as json_file:
        json.dump(output, json_file)

    # Process images and save them
    image_paths = ["path/to/image1.png", "path/to/image2.png"]  # Define paths to images
    saved_image_paths = []
    for i, image_path in enumerate(image_paths):
        image = cv2.imread(image_path)
        if image is not None:
            save_image_path = os.path.join(output_images_dir, f"image_{i+1}.png")
            cv2.imwrite(save_image_path, image)
            saved_image_paths.append(save_image_path)

    return output, saved_image_paths
