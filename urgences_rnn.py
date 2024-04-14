from keras.models import Model
from keras.layers import (Input, LSTM, Dense, concatenate)
from sklearn.model_selection import train_test_split
from matplotlib import pyplot
from datetime import datetime as dt
from keras.saving import load_model
import pickle
import numpy as np
import os

from urgences_donnees import *
from urgences_utils import *

pam_couches = (16,32,128,96)
pam_epochs = 30

# batir modele reçoit les formats des structures
def batir_modele(xh_shape, x_shape):
  input_xh = Input(shape=xh_shape)

  lstm = LSTM(pam_couches[0], return_sequences=True)(input_xh)
  lstm = LSTM(pam_couches[1])(lstm)

  input_x = Input(shape=x_shape)

  input_combo = concatenate([lstm, input_x])

  dense = Dense(pam_couches[2], activation="relu")(input_combo)
  dense = Dense(pam_couches[3], activation="relu")(dense)
  res = Dense(1, activation="sigmoid")(dense)

  model = Model(inputs=[input_xh, input_x], outputs=res)
  model.compile(optimizer='adam', loss='mse')

  return model
  

def entrainer_modele():
  # docu = charger_historique({})
  docu = charger_historique({"horodateur":{"$gte": dt(2024,3,1), "$lt": dt(2024,4,1)}})
  x_h = np.asarray(docu["x_h"])
  # réduire x_h, au besoin pour les tests, si on veut diminuer le nombre de pas de temps
  # x_h = np.asarray([xxhh[12:] for xxhh in x_h])
  x = np.asarray(docu["x"])
  y = np.asarray(docu["y"])

  # mise à l'échelle
  echelle = [np.max(x_h, axis=(0,1)), np.max(y, axis=(0))]
  x_h /= echelle[0]
  y /= echelle[1]
  x_train, x_test, x_h_train, x_h_test, y_train, y_test = train_test_split(x, x_h, y, test_size=0.2)

  model = batir_modele(x_h.shape[1:], x.shape[1:])

  # Entraînement du modèle
  model.fit([x_h_train, x_train], y_train, epochs=pam_epochs, batch_size=32, validation_data=([x_h_test, x_test], y_test))
  y_predict = model.predict((x_h_test, x_test))

  base_nf = dt.strftime(dt.now(), "%Y%m%d%H%M%S")

  with open(f"modele/modele_{base_nf}.txt", "w") as f:
    model.summary(print_fn=lambda x: f.write(x + "\n"))
    logstr(f, f"Couches: {pam_couches}. Epochs: {pam_epochs}\n")
    logstr(f, f"Cible à battre: {np.mean([pow(xxhh[xxhh.shape[0]-1,2]-yy,2) for xxhh, yy in zip(x_h,y)])}\n")
    logstr(f, f"Score: {np.mean([pow(yt - yp,2) for yt, yp in zip(y_test, y_predict)])}\n")
    logstr(f, f"Shapes: {x_h.shape} - {x.shape}")
    logstr(f, f"Echelle: {echelle}")
  model.save(f"modele/modele_{base_nf}.keras")
  with open(f"modele/modele_{base_nf}.echelle", "wb") as f:
    pickle.dump(echelle, f)
  
def charger_modele(base_nf="modele/modele"):
  with open(f"{base_nf}.echelle", "rb") as f:
    echelle = pickle.load(f)
  modele = load_model(f"{base_nf}.keras")
  return (modele, echelle)

def predire(docu):
  modele, echelle = charger_modele()
  x_h = np.asarray(docu["x_h"]) / echelle[0]
  x = np.asarray(docu["x"])
  y = modele.predict((x_h, x)) * echelle[1]
  # retourner un vecteur simple (éliminer la deuxième dimension)
  return y.reshape(y.shape[0])

if __name__ == "__main__":
  entrainer_modele()
