from docx2python import docx2python
import os
import aspose.words as aw
import json
import cv2
import numpy as np 
import warnings
from glob import glob
import re
import os
import win32com.client as win32
from win32com.client import constants
warnings.filterwarnings("ignore")

def extract_json(file_path) :
    def treat_value_biopsie(value):
            keys_permitted_apart_CIN=["Cancer",'Normale',"Dystrophie","Adénocarcinome"]
            CIN_List=["CIN1","CIN2","CIN3"]
            
            T=[False]*3
            did_find=False
            for i in range (len(CIN_List)) :
                if CIN_List[i].lower() in value.lower() :
                    did_find=True
                    T[i]=True
            if did_find :
                return "".join([CIN_List[i]+" " for i in range(3) if T[i]==True]).strip().upper()
            else :
                for i in range(len(keys_permitted_apart_CIN)) :
                    if keys_permitted_apart_CIN[i].lower() in value.lower() :
                        return(keys_permitted_apart_CIN[i].upper())

                for i in range(2) :
                        if ["MMI","ECTROPION"][i].lower() in value.lower() :
                            return "NORMALE"
            return ""
        
    def treat_geno_str(string_0):
                
        if "NON" in string_0.upper() and "16" in string_0.upper() and "18" in string_0.upper() and "45" in string_0.upper() :
            return "NON.16.18.45"
        elif   "NON" in string_0.upper() and "16" in string_0.upper() and "18" in string_0.upper() :
            return "NON.16.18"
        else :
            numbers=["16", "18","31","33","45","52","58"]
            result=""
            for el in numbers :
                if  el in string_0  :
                    result=result+"."+el
            return result[1:]
        
    def preprocessing_frottis(frotti):
        frottis_class=["Normale","ASC-US","L-SIL","H-SIL","ASC-H","AGC","Cancer"]
        result=""
        for el in frottis_class:
            if el.upper() in frotti.upper() :
                result=result+" "+el.upper()
        return " ".join(result.split())
                
    def preprocessing_HPV(HPV):
        HPV_list=['Positif IHC','Positif ARNM','Positif HC','Positif ARN','Positif PERSISTANT','Positif HIS','Positif',
    'Négatif IHC NEG' ,'Négatif IIHC','Négatif IHC','Négatif']
        if HPV.upper()=='Positif ARN M'.upper() :
            HPV='Positif ARNM'
        for el in HPV_list:
            if el.upper() in HPV.upper() :
                return el.upper()
        return ''
    
    def save_as_docx(path,target_path):
        # Opening MS Word
        word = win32.gencache.EnsureDispatch('Word.Application')
        doc = word.Documents.Open(path)
        doc.Activate ()

        # Save and Close
        word.ActiveDocument.SaveAs(
            target_path, FileFormat=constants.wdFormatXMLDocument
        )
        doc.Close(False)
        
    def mse(imageA, imageB):
        imageA_ = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        imageB_ = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
    
        imageA_ = cv2.resize(imageA, (400,400), interpolation = cv2.INTER_AREA)

        imageB_ = cv2.resize(imageB, (400,400), interpolation = cv2.INTER_AREA)


        err = np.sum((imageA_.astype("float") - imageB_.astype("float")) ** 2)
        err /= float(imageA_.shape[0] * imageA_.shape[1])

        return err<100
    directory=os.path.dirname(__file__)
    
    img_2 = cv2.imread(os.path.join(directory,"images_to_delete","Image.ExportImages.2_.png"))
    img_1 = cv2.imread(os.path.join(directory,"images_to_delete","Image.ExportImages.1_.png"))
    img_3 = cv2.imread(os.path.join(directory,"images_to_delete","Image.ExportImages.0_.png"))
    img_4 = cv2.imread(os.path.join(directory,"images_to_delete","Image.ExportImages.0_.jpeg"))



    historical_information={"Vaccin" :False  }
    #"Génotypage"
    keys_motif_de_consultation=[("Frottis",preprocessing_frottis),("HPV",preprocessing_HPV),("Biopsie",treat_value_biopsie)]
    keys=["Date",
          "Impression Colposcopique",
        "Madame",
        "Age",
        "Génotypage",
        "Frottis (1)","Frottis (2)","Frottis (3)","Frottis (4)",
        "Date Frottis (1)","Date Frottis (2)","Date Frottis (3)","Date Frottis (4)",
        "Biopsie", "Biopsie (1)", "Biopsie (2)", "Biopsie (3)",
        "Date Biopsie", "Date Biopsie (1)", "Date Biopsie (2)" , "Date Biopsie (3)" 
        , "ERAD", "ERAD (2)", "ERAD (3)" , "ERAD (4)" , "ERAD (5)"
        ,"DATE INTERVENTION", "DATE INTERVENTION (2)", "DATE INTERVENTION (3)" , "DATE INTERVENTION (4)"  ,"DATE INTERVENTION (5)" 
    ]

    
    directory=os.path.dirname(__file__)
    target_path=os.path.join(directory,"temp","temp.docx")
    save_as_docx(file_path,target_path)
    doc_result = docx2python(target_path)

               
    did_find=False
    for el in list(doc_result.body) :
        
        for el_1 in el :
            
            for el_2 in el_1 :
                
                for el_3 in el_2 :
                    
                    # print("start")
                    # print(el_3)
                    # print("end")
                    if "GARDASIL" in el_3 :
                        historical_information["Vaccin"]=True
                        
                    
                    for key,process in keys_motif_de_consultation :
                     key=key.upper()
                     if key not in historical_information.keys() :
                        index=el_3.upper().find(key.upper()+":")
                        true_index=index+len(key+":")
                        if index==-1 :
                            index=el_3.upper().find(key.upper()+" :")
                            true_index=index+len(key+" :")
#
                        if index!=-1 :
                            # end_index=el_3.find("\t",true_index) 
                            # if end_index==-1 :
                            #    end_index=len(el_3)+1
                            # value=el_3[true_index:end_index].strip()
                            # end_index=value.find("-") 
                            # if end_index==-1 :
                            #    end_index=len(value)+1
                            # value=value[:end_index].strip()
                            
                            # end_index=value.find("   ") 
                            # if end_index==-1 :
                            #    end_index=len(value)+1
                            # value=value[:end_index].strip()
                            
                            # end_index=value.find("\n") 
                            # if end_index==-1 :
                            #    end_index=len(value)+1
                            # value=value[:end_index].strip()
                            
                            # end_index=value.find("\r") 
                            # if end_index==-1 :
                            #    end_index=len(value)+1
                            
                            # print(key)
                            # if key=="GÉNOTYPAGE" :
                            #     print(true_index)
                            #     print(value)
                            value=el_3[true_index:].strip()
                            import re
                            date_=re.search(r"\d{0,2}([/.]){0,1}\d{0,2}([/.]){0,1}\d{4}",value)
                            try :
                                date_=date_.group()
                                date_=date_.replace(".","/")
                            except :
                                date_=""
                            if len(value)!=0 and len(date_)!=0 :
                                historical_information[key]=process(value.upper())
                                historical_information["DATE "+key]=date_
                                
                    for key in keys :
                     key=key.upper()
                     if key not in historical_information.keys() :
                      
                        
                        index=el_3.upper().find(key.upper()+":")
                        true_index=index+len(key+":")
                        if index==-1 :
                            index=el_3.upper().find(key.upper()+" :")
                            true_index=index+len(key+" :")
#
                        if index!=-1 :
                            value=el_3[true_index:].strip()
                      
                            # end_index=el_3.find("\t",true_index) 
                            # if end_index==-1 :
                            #    end_index=len(el_3)+1
                            # value=el_3[true_index:end_index].strip()
                            # end_index=value.find("-") 
                            # if end_index==-1 :
                            #    end_index=len(value)+1
                            # value=value[:end_index].strip()
                            end_index=value.find("  ") 
                            if end_index==-1  :
                               end_index=len(value)+1
                            if  end_index!=0 :
                                value=value[:end_index].strip()
                     
                            
                            end_index=value.find("\n") 
                            if end_index==-1 :
                               end_index=len(value)+1
                            if  end_index!=0 :
                                value=value[:end_index].strip()
                        
                            
                            end_index=value.find("\r") 
                            if end_index==-1 :
                               end_index=len(value)+1
                           
                            
                            if  end_index!=0 :
                                value=value[:end_index].strip()
                           
                            import re
                            date_=re.search(r"\d{0,2}([.]{0,1})\d{4}",value)
                            try :
                                date_=date_.group()
                            except :
                                date_=""
                            
                            if key=="AGE":
                                value=re.search(r"\d{2}",value)
                                try :
                                    value=value.group()
                                except :
                                    value="50"
                                
                                
                            if len(value)!=0:
                              
                                historical_information[key]=value.upper()
                                if "DATE" in key :
                                    date_=re.search(r"\d{0,2}([/])\d{0,2}([/])\d{4}",value)
                                    try :
                                        date_=date_.group()
                                    except :
                                        date_=""
                                    historical_information[key]=date_
                                            
                                if date_!="" and  "DATE "+key not in historical_information and "DATE" not in key:
                                    historical_information["DATE "+key]=date_.replace(".","/")
 
    def treat_date(date) :
        date_split=date.split("/")
        if len(date_split)==1 :
            return date_split[0]
        elif len(date_split)==2 :
            return date_split[1]+"-"+date_split[0]
        elif len(date_split)==3 :
            return date_split[2]+"-"+date_split[1]+"-"+date_split[0]
        return ""
            
    ouput={"Frottis": {}, "HPV": {}, "Biopsie": {}, "Erad": {}, "Vaccin": "" , "Age": "40", "date_colposcopie" : "2022-11-31"}              

    for key in ["DATE INTERVENTION", "DATE INTERVENTION (2)", "DATE INTERVENTION (3)" , "DATE INTERVENTION (4)"  ,"DATE INTERVENTION (5)" ] :
        if key in historical_information :
            historical_information[key.replace("DATE INTERVENTION","DATE ERAD")]=historical_information.pop(key)

    Vaccin="oui" if historical_information["Vaccin"]==True else "non"
    ouput["Vaccin"]=Vaccin

    if "AGE" in historical_information.keys() :
        ouput["Age"]=historical_information["AGE"]
        
    if "Date".upper() in historical_information.keys() :
        ouput['date_colposcopie']=treat_date(historical_information["Date".upper()])

    if "Génotypage".upper() in historical_information.keys() and "HPV".upper() in historical_information.keys() and "DATE HPV".upper() in historical_information.keys() :
        date=treat_date(historical_information["DATE HPV"])
        ouput["HPV"][date]=[historical_information["HPV"],historical_information["Génotypage".upper()]]
        
    for key_dict in historical_information.keys() :
        if "Frottis".upper() in key_dict and "DATE "+key_dict in historical_information.keys() :
            date=treat_date(historical_information["DATE "+key_dict])
            ouput["Frottis"][date]=historical_information[key_dict]
            
    for key_dict in historical_information.keys() :
        if "Biopsie".upper() in key_dict and "DATE "+key_dict in historical_information.keys() :
            date=treat_date(historical_information["DATE "+key_dict])
            ouput["Biopsie"][date]=historical_information[key_dict]
            
    for key_dict in historical_information.keys() :
        if "ERAD".upper() in key_dict and "DATE "+key_dict in historical_information.keys() :
            date=treat_date(historical_information["DATE "+key_dict])
            ouput["Erad"][date]=historical_information[key_dict]
            
    try :
        ouput["IMPRESSION COLPOSCOPIQUE"]=historical_information["IMPRESSION COLPOSCOPIQUE"]
    except :
        ouput["IMPRESSION COLPOSCOPIQUE"]=""
        
    try :
        ouput["MADAME"]=historical_information["MADAME"]
    except :
        ouput["IMPRESSION COLPOSCOPIQUE"]="Madame"
    
    # print(ouput)
    directory=os.path.dirname(__file__)
    save_path= os.path.join(directory,"temp","data.json")


    dict_json = json.dumps(ouput)



    # open file for writing, "w" 
    f = open(save_path,"w") 
        
    # write json object to file
    f.write(dict_json)

    # close file
    f.close()
    
        
                    