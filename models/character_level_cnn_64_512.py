# -*- coding: utf-8 -*-
"""Copy of Character Level CNN

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1M-6z1mno0dg8q7ty-yGM8helANpAc-4m
"""

#ATENTIE! Din motive de compatibilitate, versiunea de Tensorflow folosita este 1.6.0
#Notebookul se poate rula direct in Google Colab
#Datele sunt incarcate de pe Google Drive, se poate pastra calea data Drive-ului daca se pune setul de date in drive in folderul 'Colab Notebooks'
#Sau se pot pune oriunde in drive si ajusta calea
! pip install tensorflow==1.6.0
import keras
import pandas as pd
import numpy as np
import re
import time
import numpy as np
import nltk
from sklearn.metrics import accuracy_score
import math
from google.colab import drive
drive.mount('/content/drive')
from sklearn.metrics import f1_score
from keras.layers import Input, Embedding, Activation, Flatten, Dense
from keras.layers import Conv1D, Dropout
from keras.models import Model

#citirea etichetelor
#a se seta calea din drive
train_labels = pd.read_csv('/content/drive/My Drive/Colab Notebooks/ml-2020-unibuc-3/train_labels.txt', sep='\t',header=None) 
test_labels = pd.read_csv('/content/drive/My Drive/Colab Notebooks/ml-2020-unibuc-3/validation_labels.txt', sep='\t',header=None)

#a se seta calea din drive
#citirea datelor de intrare 
with open('/content/drive/My Drive/Colab Notebooks/ml-2020-unibuc-3/train_samples.txt', encoding='utf-8') as q:
    train_data = q.readlines()

#liste ce vor conține id-urile, repsectiv conținutele textelor
train_ids=[]
train_texts=[]

#separarea id-urilor de texte
for data in train_data:
  id,text=data.split('\t')
  train_ids.append(id)
  train_texts.append(text)
print(train_texts[0])

#a se seta calea din drive
#citirea datelor de validare
with open('/content/drive/My Drive/Colab Notebooks/ml-2020-unibuc-3/validation_samples.txt', encoding='utf-8') as q:
    test_data = q.readlines()
print(test_data[0])

#liste ce vor conține id-urile, repsectiv conținutele textelor
test_ids=[]
test_texts=[]

#separarea id-urilor de texte
for data in test_data:
  id,text=data.split('\t')
  test_ids.append(id)
  test_texts.append(text)
print(test_texts[0])

import textwrap

train_labels=[c for c in train_labels[1].values]

#vom imparti date in texte de lungime maxim 300

train_text=[]
train_label=[]

#pentru toate textele de lungime 300, vrem sa adaugam si eticheta textului initial din care fac parte
#pentru a segmenta, vom folosi textwrap
test_label=np.array([c for c in test_labels[1].values])
for i,sample in enumerate(train_texts):
    s=textwrap.wrap(sample,300)
    for sample in s:
       train_text.append(sample)
       train_label.append(train_labels[i])

#adaugarea etichetelor de testare
test_label=np.array([c for c in test_labels[1].values])

#vom coda fiecare caracter cu un numar>0. 0 se va pastra pentru padding
d = {}
for sample in train_text:
  for c in sample:
    if c not in d:
      d[c]=len(d)+1
print(d)

#vom transforma textele codând cliterele cu cifrele corespunzătoare din dictionarul d
#caracterele care nu se gasesc in dictionar in setul de testare, respectiv validare, vor fi codificate cu len(d)+1

train_sequences=np.zeros((len(train_text),300), dtype='int64')
for i,sample in enumerate(train_text):
  for j in range(len(sample)):
    train_sequences[i][j]=d[sample[j]]

#transformarea textelor de testare in secvente; pentru acestea vom folosi doar primele 300 de caractere
test_sequences=np.zeros((len(test_texts),300), dtype='int64')
for i,sample in enumerate(test_texts):
  for j in range(min(300,len(sample))):
    if sample[j] in d:
      test_sequences[i][j]=d[sample[j]]
    else:test_sequences[i][j]=len(d)+1

print(train_sequences[0])

#matricea de embedding
#primul vector de 0-ori este pentru padding
#urmatoarele len(d)+1 sunt pentru len(d) caractere + 1 pentru toate caracterele intalnite care nu fac parte din alfabet

embedding_w=np.zeros((len(d)+2,len(d)+1))
embedding_w[1:,:]=np.eye(len(d)+1, dtype=int)
print(embedding_w.shape)

#crearea stratului de embedding
embedding_layer=Embedding(len(d)+2,len(d)+1,input_length=300,weights = embedding_w )

##!!Aceasta secventa trebuie rulata de 2 ori din cauza erorii de keras, insa functioneaza corect

from keras.backend import sigmoid

#am pastrat definitiile functiilor sigmoid si swish aici, chiar daca pentru aceasta predictie nu se vor folosi
def swish(x, beta = 1):
  return (x * sigmoid(beta * x))
 
def elliot(x):
  return 0.5 * x / (abs(x) + 1) + 0.5 

#importarea straturilor
from keras.layers import GlobalAveragePooling1D,Reshape, multiply
from keras.layers import LeakyReLU
from keras.initializers import glorot_uniform
from keras.utils.generic_utils import get_custom_objects
from keras.layers import Activation
from keras.initializers import lecun_normal

#obtinem activari pentru swish si eliot
get_custom_objects().update({'swish': Activation(swish)})
get_custom_objects().update({'elliot': Activation(elliot)})

#definirea inputului
inputs = Input(shape = (300,), name='input',dtype='float64')

#stratul de embedding
x = embedding_layer(inputs)
print(x.shape)

#primul strat convolutional
x= Conv1D(64, 7)(x)
x =LeakyReLU(alpha=0.00005)(x)
init=x
print(init.shape)

#primul bloc de Squeeze and Excitation
x=GlobalAveragePooling1D()(x)
x=Dense(2)(x)
x= Activation('relu')(x)              #128 cu 64 , 10 epoci sau 128 cu 512, 10 epoci
x= Dense(64, activation='sigmoid')(x)
print(x.shape)
x= multiply([init,x])
print(x.shape)


#al doilea bloc convolutional
x= Conv1D(64, 7)(x)
x =LeakyReLU(alpha=0.00005)(x)
#x =Activation('swish')(x)
init=x
print(init.shape)
#al doilea bloc de Squeeze and Excitation
x=GlobalAveragePooling1D()(x)
x=Dense(2)(x)
x= Activation('relu')(x)
x= Dense(64, activation='sigmoid')(x)
print(x.shape)
x= multiply([init,x])
print(x.shape)

#al treilea bloc convolutional
x= Conv1D(64, 3)(x)
x =LeakyReLU(alpha=0.00005)(x)
init=x
print(init.shape)
#al treilea bloc Squeeze and Excitation
x=GlobalAveragePooling1D()(x)
x=Dense(2)(x)
x= Activation('relu')(x)
x= Dense(64, activation='sigmoid')(x)
print(x.shape)
x= multiply([init,x])
print(x.shape)

x=Flatten()(x)

#blocurile complet conectate
x= Dense(512,activation='relu', kernel_initializer=lecun_normal(seed=12345))(x) #seed-ul potrivit
x= Dropout(0.5)(x)                  
x= Dense(512, activation='relu', kernel_initializer=lecun_normal(seed=12345))(x) #seed si aici
x= Dropout(0.5)(x)

#stratul de output
pred=Dense(2, activation='softmax',)(x)

from keras import backend as K

def recall_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall

def precision_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision

def f1_m(y_true, y_pred):
    precision = precision_m(y_true, y_pred)
    recall = recall_m(y_true, y_pred)
    return 2*((precision*recall)/(precision+recall+K.epsilon()))

#optimizatorul folosit este Adam cu learning rate de 0.0005
from keras.optimizers import Adam
optimizer = Adam(lr=0.0005)

#transformam in to_categorical pentru model
from keras.utils import to_categorical
y_train=to_categorical(train_label)
y_test=to_categorical(test_label)

#declaram si compilam modelul

model = Model(inputs,pred)
model.compile(optimizer=optimizer,  loss='binary_crossentropy', metrics=[recall_m, precision_m, f1_m,'accuracy'])

model.summary()

model.fit(train_sequences, y_train, validation_data=(test_sequences, y_test), batch_size=64, epochs=10)

#prezicem pe setul de validare
proba=model.predict(test_sequences,batch_size=64)
#alegem un prag pentru predictii pentru a maximiza rezultatul
#iteram prin toate pragurile de la {0,0.1, 0.2,..., 0.8, 0.9}
#s-a dovedit ca pragul de 0.6 este cel mai potrivit in majoritatea cazurilor
for i in range(0,10):
  th=i/10
  for i in range(len(test_labels)):
    if(proba[i][1]>th):
      preds[i]=1
    else: 
      preds[i]=0
    # if(preds[i]!=test_label[i]):
    #    print(len(test_texts[i]))
  print(f1_score(test_label, preds,average='macro'),accuracy_score(test_label, preds))

import csv
#citirea datelor pentru setul de testare
#a se seta calea din drive
with open('/content/drive/My Drive/Colab Notebooks/ml-2020-unibuc-3/test_samples.txt', encoding='utf-8') as q:
    final_data = q.readlines()
print(final_data[0])
final_ids=[]
final_texts=[]
for data in final_data:
  id,text=data.split('\t')
  final_ids.append(id)
  final_texts.append(text)
print(final_texts[0])



#transpunerea datelor in secvente
final_sequences=np.zeros((len(final_texts),300), dtype='int64')
for i,sample in enumerate(final_texts):
  for j in range(min(300,len(sample))):
    if sample[j] in d:
      final_sequences[i][j]=d[sample[j]]
    else: 
      final_sequences[i][j]=len(d)+1
      print(sample[j])
final_sequences = np.array(final_sequences, dtype='float32')
print(final_sequences)

proba=model.predict(final_sequences, batch_size=64,)

#scrierea fisierului
with open('/content/drive/My Drive/Colab Notebooks/innovatorsnn-cript.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["id", "label"])
    count=0
    for i in range(len(final_sequences)):
        p=0
        if(proba[i][1]>0.6):
            p=1
        else: 
            p=0
            count+=1
        writer.writerow([final_ids[i], p])
    print(count)
