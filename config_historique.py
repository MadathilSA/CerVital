frottis=["",'ASC-US AGC', 'L-SIL ASC-H', 'L-SIL ASC-H AGC', 'L-SIL H-SIL', 'L-SIL AGC', 'ASC-H', 'H-SIL', 'ASC-US L-SIL', 'L-SIL', 'L-SIL CANCER', 'CANCER', 'AGC', 'H-SIL AGC', 'ASC-US', 'ASC-H AGC']

frottis_value_to_key=dict(zip(frottis,range(len(frottis))))

Frottis_to_ignore=['ASC-US AGC', 'L-SIL ASC-H', 'L-SIL ASC-H AGC', 'L-SIL H-SIL', 'L-SIL AGC', 'ASC-US L-SIL', 'L-SIL CANCER', 'CANCER', 'H-SIL AGC',  'ASC-H AGC']
for el in Frottis_to_ignore :
    frottis_value_to_key[el]=0
frottis_key_to_value={v:k for k,v in frottis_value_to_key.items()}
#date 2014-04-01

HPV=["",'Positif IHC','Positif ARNM','Positif HC','Positif ARN','Positif PERSISTANT','Positif HIS','Positif',
'Négatif IHC NEG' ,'Négatif IIHC','Négatif IHC','Négatif']

HPV=[el.upper() for el in HPV]
HPV_value_to_key=dict(zip(HPV,range(len(HPV))))
Positif=['Positif IHC','Positif ARNM','Positif HC','Positif ARN','Positif PERSISTANT','Positif HIS','Positif']
Negative=['Négatif IHC NEG' ,'Négatif IIHC','Négatif IHC','Négatif']

for el in Positif :
    HPV_value_to_key[el.upper()]=7
    
for el in Negative :
    HPV_value_to_key[el.upper()]=11
    



HPV_key_to_value={v:k for k,v in HPV_value_to_key.items()}
#à voir avec le DR
#prendre compte de genotypage hpv ?? NON 16.18 ?!


Biopsie_Erad=["",'NORMALE','CIN1', 'CIN2', 'CIN3', 'CIN1 CIN2', 'CIN2 CIN3','CIN1 CIN3', 'DYSTROPHIE','ADÉNOCARCINOME','CANCER' ]

Biopsie_Erad_value_to_key=dict(zip(Biopsie_Erad,range(len(Biopsie_Erad))))

Biopsie_Erad_value_to_key["CANCER"]=4
Biopsie_Erad_value_to_key["ADÉNOCARCINOME"]=4
Biopsie_Erad_value_to_key["DYSTROPHIE"]=1
Biopsie_Erad_value_to_key['CIN1 CIN2']=3
Biopsie_Erad_value_to_key['CIN2 CIN3']=4
Biopsie_Erad_value_to_key["CIN1 CIN3"]=4




Biopsie_Erad_key_to_value={v:k for k,v in Biopsie_Erad_value_to_key.items()}

Diagno=['NORMALE', 'CIN2' ]
Diagno_value_to_key=dict(zip(Diagno,range(len(Diagno))))
Diagno_value_to_key['CIN1']=0
Diagno_value_to_key['CANCER']=1
Diagno_value_to_key['CIN3']=1


Diagno_key_to_value={v:k for k,v in Diagno_value_to_key.items()}


HPV_type=["NON.16.18.45","NON.16.18","16", "18","31","33","45","52","58"]
HPV_type_value_to_key=dict(zip(HPV_type,range(len(HPV_type))))


# DYSTROPHIE==> normale, ADÉNOCARCINOME==>cancer
#CIN1 CIN3 + erad CIN1 what to take ???

#erad : histoire d'erad preventive vs ERAD test : how to see this (think does a deff) ??

#should I consider laser ??

#apparat dic others are year first

# took diff <=9
#il y'a pas biopsie : on prend erad ?
#all normal + TZ1 ==> prend normale

#4600 exploitable

path_for_data_train=r"path/to/trainingdata.json"
path_for_data_test=r"path/to/testingdata.json"


batch_size=1

base_width= 380
h_size= 288

weights_initial_path=r"path/to/mobilenetv2_1.0-0c6065bc.pth"

path_for_data_train=r"path/train.json"

path_for_data_test=r"path/test.json"

weights_save_path=r"path\save_histo.pth"

weights_save_path_0=r"path\ProjectXProjet"

path_for_excels= r"path\ProjectXProjet"

convnext_base_path=r"path\ProjectXProjet\convnext_base_22k_224.pth"

convnext_small_path=r"path/convnext_small_22k_224.pth"

mobilent_path=r"path\mobilenetv2_1.0-0c6065bc.pth"

mobilenet_config_shape=1280

convnext_config_shape=768

historical_info_shape=2048

epochs=  11

embed_dim=128

max_learning_rate=  5e-6
min_learning_rate=1e-20

#we did fenetre de 9 mois
#add tabac +(vaccin and other thing in doc that I didn't find)
