from ast import Param
import torch
import torch.nn as nn
import config_historique as config
import torch.nn.functional as F
from convnext import convnext_small
import torch.nn.init as init


class MedicalModel(nn.Module):
    def __init__(self, width_mult=1.):
        
        super(MedicalModel, self).__init__()
        
        model=convnext_small(True,True,drop_path_rate=0.9)

        self.net=model
        self.firstlinearlayer=nn.Linear(config.convnext_config_shape,config.historical_info_shape)
        
        self.frottis_embedding=torch.nn.Embedding(len(config.frottis_value_to_key), config.embed_dim, padding_idx=0)
        
        self.biopsie_embedding=torch.nn.Embedding(len(config.Biopsie_Erad_value_to_key), config.embed_dim, padding_idx=0)
        
        self.erad_embedding=torch.nn.Embedding(len(config.Biopsie_Erad_value_to_key), config.embed_dim, padding_idx=0)

        self.HPV_embedding=torch.nn.Embedding(len(config.HPV_value_to_key), config.embed_dim, padding_idx=0)
                
        self.HPV_type_linear=nn.Linear(len(config.HPV_type_value_to_key),2*config.embed_dim)
        
        self.Vaccin_embedding=torch.nn.Embedding(2, config.embed_dim)
        
        self.classfier=Classifier(config.historical_info_shape*2,len(config.Diagno),intermediate_drop=0.5,final_drop=0.5)
        
        self.classfier_visual=Classifier(config.historical_info_shape,len(config.Diagno),intermediate_drop=0.5,final_drop=0.5)
        self.classfier_historical=Classifier(config.historical_info_shape,len(config.Diagno),intermediate_drop=0.5,final_drop=0.5)
        
        self.classifier_histo=Classifier_Histo(config.embed_dim*27+17,config.historical_info_shape,intermediate_drop=0.5)
        
        self.layer_norm_0=torch.nn.LayerNorm(config.historical_info_shape)
        self.layer_norm_1=torch.nn.LayerNorm(config.historical_info_shape)
        
        for m in self.modules():
            try:
                init.xavier_uniform(m.weight)
                if m.bias is not None:
                    m.bias.data.zero_()
            except:
                pass
        
        self.dropout_embeddings=  nn.Dropout(0.5)      
        self.dropout_layer=nn.Dropout(0.5)
        self.dropout_layer_visual=nn.Dropout(0.5)

        
        
        

class Classifier(nn.Module):
        def __init__(self,in_dimension,out_dimension,inter_dim=4096,input_drop=0,intermediate_drop=0.5,final_drop=0.5):
            
            super(Classifier, self).__init__()

            self.layer_0 = nn.Linear(in_dimension, inter_dim)
            self.layer_1 = nn.Linear(inter_dim , inter_dim)
            self.layer_2 = nn.Linear(inter_dim , out_dimension)


            self.input_dropout_layer = nn.Dropout(p=input_drop)
            self.intermediate_dropout_layer = nn.Dropout(p=intermediate_drop)
            self.final_dropout_layer = nn.Dropout(p=final_drop)


        def forward(self, input):
            """
            This function outputs the predicted character probabilities of the current decoding step
            Parameters
            ----------
            context_vector : Pytorch Tensor
                the weighted sum of the feature map vectors using the attention weights


            Returns
            -------
            logits : Pytorch Tensor
                the current decoding step classification logits batch


            """
            input=self.input_dropout_layer(input)
            
            input=F.relu(self.layer_0(input))
            
            input = self.intermediate_dropout_layer(input)

            input =  F.relu(self.layer_1(input ) )
            
            input = self.final_dropout_layer(input)
             
            logits =  self.layer_2(input )

            return logits
        
class Classifier_Histo(nn.Module):
        def __init__(self,in_dimension,out_dimension,inter_dim=4096,input_drop=0,intermediate_drop=0.5,final_drop=0):
            
            super(Classifier_Histo, self).__init__()

            self.layer_0 = nn.Linear(in_dimension, inter_dim)
            self.layer_1 = nn.Linear(inter_dim , inter_dim)
            self.layer_2 = nn.Linear(inter_dim , inter_dim)
            self.layer_3 = nn.Linear(inter_dim , inter_dim)
            self.layer_4 = nn.Linear(inter_dim , out_dimension)


            self.input_dropout_layer = nn.Dropout(p=input_drop)
            self.intermediate_dropout_layer = nn.Dropout(p=intermediate_drop)
            self.final_dropout_layer = nn.Dropout(p=final_drop)

            

        def forward(self, input):
            """
            This function outputs the predicted character probabilities of the current decoding step
            Parameters
            ----------
            context_vector : Pytorch Tensor
                the weighted sum of the feature map vectors using the attention weights


            Returns
            -------
            logits : Pytorch Tensor
                the current decoding step classification logits batch


            """

            input=self.input_dropout_layer(input)
            
            input_1=self.intermediate_dropout_layer(F.leaky_relu(self.layer_0(input)))
            
            input_2 =  self.intermediate_dropout_layer(F.leaky_relu(self.layer_1(input_1)))
            
            input_3 =  self.intermediate_dropout_layer(F.leaky_relu(self.layer_2(input_2)))
            
            input_4 =  self.intermediate_dropout_layer(F.leaky_relu(self.layer_3(input_3)))
            
            input_5 =  F.leaky_relu(self.layer_4(input_4))
                        

            return input_5
        
        