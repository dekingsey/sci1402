# urgences_donnees.py:
# fonctions utilitaires pour extraire et modifier les données du projet
# le projet utilise deux collections:
# - situations: données horaires sur les situations dans les urgences
#               les données sont lues à chaque heure
#               les données des situations sont des données statistiques et
#               servent à la prédiction des taux d'occupation
#               les donnees prédites ont une valeur pour la colonne niveau_prediction
#               le niveau_prediction indique le temps écoulé depuis que les données réelles
#               ont été collectées pour l'installation
#               la clé est "installation","horodateur"
# - installations: liste des emplacements qui offrent des services d'urgence
#                  les installations conservées pour ce projet ne sont celles qui
#                  sont trouvées dans les situations
#                  les données qu'on retrouve dans ces documents ne sont que
#                  descriptifs
#                  la clé est "installation"
import requests
import os
import json
import numpy as np
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import pymongo
from datetime import datetime as dt, timedelta as td
import pandas as pd
from urgences_utils import *

# ouvrir une base de donnée mongodb - locale ou sur Atlas
# MONGO_URI doit être défini pour une base sur Atlas
# pour une base locale, un accès anonyme est requis
def ouvrir_mongodb(sur_atlas=True):
  if sur_atlas:
    if ("MONGO_URI" in os.environ):
      # usr="mongo"
      # pwd="jkNaszX3tsL69LbU"
      # uri=f"mongodb+srv://{usr}:{pwd}@cluster0.5w33wio.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
      uri=os.environ["MONGO_URI"]
      client = MongoClient(uri, server_api=ServerApi('1'))
  else:
    client = MongoClient()
  db = client.get_database("cluster0")

  return db

# chargement des installations
# les installations sont généralement insérées lors de la lectures des
# situations
def charger_installations(cond={}, journal=None):
  df = None
  try:
    db = ouvrir_mongodb()
    installations = db.get_collection("installations")
    installations_liste = [x for x in installations.find(cond)]
    df = pd.DataFrame.from_dict(installations_liste)
  except Exception as ex:
    logstr(journal, f"Exception lors du chargement des installations: {ex}")
  finally:
    if not db is None:
      db.client.close()
  return df

# fonction utilitaire lisant la valeur maximale de horodateur pour la collection
# reçue en paramètres
def lire_heure_max(col):
  return col.find_one({}, sort=[("horodateur", pymongo.DESCENDING)])["horodateur"]

# chargement des situation à partir de la base de données
# Paramètres:
# - cond:    toutes les données sont chargées. Condition à appliquer lors du chargement
# - heures:  lorsque spécifié, lire les données plus récente que ce nombre d'heures dans le passé
# - max:     lorsque spécifié, lire seulement les informations pour la dernière entrée de chaque installation
#            "heures" est ignoré si max est utilisé
def charger_situations(cond={}, heures=None, max=False, journal=None):
  df = None
  try:
    db = ouvrir_mongodb()
    situations = db.get_collection("situations")

    if max:
      cond["horodateur"] = lire_heure_max(situations)
    elif heures is not None:
      cond["horodateur"] = {"$gte": dt.now() - td(hours=heures)}

    tout = [elem for elem in situations.find(cond)]
    df = pd.DataFrame.from_dict(tout)

  except Exception as ex:
    logstr(journal, f"Exception lors du chargement des situations: {ex}")
  finally:
    db.client.close()
  return df

def charger_predictions(heures=None, journal=None):
  df = None
  try:
    db = ouvrir_mongodb()
    predictions = db.get_collection("predictions")

    cond = {"horodateur": {"$gte": dt.now() - td(hours=heures)}}

    tout = [elem for elem in predictions.find(cond)]
    df = pd.DataFrame.from_dict(tout)

  except Exception as ex:
    logstr(journal, f"Exception lors du chargement des predicitons: {ex}")
  finally:
    db.client.close()
  return df

# ajout d'une installation par son id - l'installation est lue sur le site
# de donneesquebec.ca
def ajouter_installation(id_installation, journal=None):
  try:
    db = ouvrir_mongodb()
    installations_collection = db.get_collection("installations")

    url = "https://www.donneesquebec.ca/recherche/api/3/action/datastore_search"
    params = {
        'resource_id': '2aa06e66-c1d0-4e2f-bf3c-c2e413c3f84d',
        'q': id_installation
    }

    reponse = requests.get(url, params=params)

    if reponse.status_code == 200:
      if "result" in reponse.json() and "records" in reponse.json()["result"]:
        records = reponse.json()["result"]["records"]
        # puisque la recherche cherche dans tous les elements, vérifions que c'est
        # bien le INSTAL_COD qui a été trouvé
        trouve = False
        for rec in records:
          if ("INSTAL_COD" in rec and
              rec["INSTAL_COD"].isnumeric and
              int(rec["INSTAL_COD"]) == id_installation):
            logstr(journal, f"INFORMATION - Ajout de l'installation {id_installation}")
            installation = {
                            "installation": int(id_installation),
                            "installation_nom": rec["INSTAL_NOM"],
                            "rss": rec["RSS_CODE"],
                            "rss_nom": rec["RSS_NOM"],
                            "etablissement": rec["ETAB_CODE"],
                            "etablissement_nom": rec["ETAB_NOM"],
                            "adresse": rec["ADRESSE"],
                            "code_postal": rec["CODE_POSTA"],
                            "municipalite": rec["MUN_NOM"],
                            "longitude": float(rec["LONGITUDE"]),
                            "latitude": float(rec["LATITUDE"])
            }
            installations_collection.insert_one(installation)
            trouve = True
            break
        if not trouve:
          logstr(journal, f"Installation {id_installation} non trouvée sur donneesquebec")
      else:
        logstr(journal, f"Structure invalide {reponse.json().keys()}")
    else:
      logstr(journal, f"La requête a échoué avec le code d'état : {reponse.status_code}")
  except Exception as ex:
    logstr(journal, f"Erreur lors de la lecture de l'installation {id_installation}: {ex}")

# ajout des situations "réelles" lues sur le site de donnéesquébec. le format reçu
# est donc celui des données brutes et converti dans notre format par
# cette fonction
def ajouter_situations(df, situations, journal):
  # dans le format csv que nous utilisons, il y a des tabs (\t) dans les titres
  # des colonnes - renommer les colonnes
  renommer = {}
  for e in df.columns:
    renommer[e] = e.strip()
  df = df.rename(columns=renommer)
  horodateur = None

  if not "Mise_a_jour" in df.columns:
    logstr(journal, f"Données invalides. Colonne Mise_a_jour introuvable dans données brutes.")
  else:
    try:
      maj = dt.strptime(df.loc[0, "Mise_a_jour"], "%Y-%m-%dT%H:%M")
      horodateur = dt(maj.year, maj.month, maj.day, maj.hour)
      # arrondissement de l'horodateur à l'heure la plus près
      if maj.minute >= 30:
        horodateur += td(hours=1)

    except Exception as ex:
      logstr(journal, f"Erreur lors de la récupération de l'horodateur. {ex}")

  # vérifions si les données pour cette mise à jour existe déjà
  # note: si des données prédites existent, ne pas en tenir compte - elles seront détruites suite à l'insertion
  #       (condition sur le niveau_prediction)
  if horodateur and situations.find_one({"horodateur":horodateur, "$or":[{"niveau_prediction":0},{"niveau_prediction":{"$exists":False}}]}):
    logstr(journal, f"INFORMATION - Des données existent déjà pour {horodateur}")
  elif horodateur:
    # nous accumulons les documents à insérer dans une liste qui est insérée à la fin
    # par souci de performance
    documents = []
    # chargement préalable de la liste des installations connues
    # si une installation inconnue est trouvée, nous l'ajouterons
    installations = [x.installation for _, x in charger_installations().iterrows()]
    for _, donnee in df.iterrows():
      # note: ce "try" échouera si des données ne peuvent pas être converties dans le type attendu
      try:
        if ("No_permis_installation" in donnee and
            donnee["No_permis_installation"].isnumeric() and
            int(donnee["Nombre_de_civieres_fonctionnelles"]) != 0):
          donnee_json = {}
          id_installation = int(donnee["No_permis_installation"])
          donnee_json["installation"] = id_installation
          donnee_json["horodateur"] = horodateur
          donnee_json["mise_a_jour"] = maj
          donnee_json["rss"] = donnee["RSS"]
          donnee_json["civieres"] = int(donnee["Nombre_de_civieres_fonctionnelles"])
          donnee_json["civieres_utilisees"] = int(donnee["Nombre_de_civieres_occupees"])
          donnee_json["attente24"] = int(donnee["Nombre_de_patients_sur_civiere_plus_de_24_heures"])
          donnee_json["attente48"] = int(donnee["Nombre_de_patients_sur_civiere_plus_de_48_heures"])
          donnee_json["patients"] = int(donnee["Nombre_total_de_patients_presents_a_lurgence"])
          donnee_json["patients_attente"] = int(donnee["Nombre_total_de_patients_en_attente_de_PEC"])
          donnee_json["dms_civiere"] = float(donnee["DMS_sur_civiere"])
          donnee_json["dms"] = float(donnee["DMS_ambulatoire"])
          donnee_json["jour_semaine"] = donnee_json["horodateur"].weekday()
          donnee_json["heure"] = donnee_json["horodateur"].hour
          donnee_json["taux_occupation"] = donnee_json["civieres_utilisees"] / donnee_json["civieres"]
          donnee_json["niveau_prediction"] = 0
          documents.append(donnee_json)
          # nouvelle installation trouvée: nous l'ajoutons dans la base de données
          if not id_installation in installations:
            ajouter_installation(id_installation)

      except Exception as e:
        logstr(journal, f'Traitement de {donnee["No_permis_installation"]}')
        logstr(journal, f"INFORMATION - Données ignorées. {e}")
        donnee = None
    situations.insert_many(documents)
    # destruction des données prédites pour chaque installation pour laquelle ont été insérées
    # des données réelles
    predictions_a_detruire = [{"installation":x["installation"]} for x in documents]
    situations.delete_many({"horodateur":horodateur, "$or":predictions_a_detruire, "niveau_prediction":{"$ne":0}})
    # lorsque de nouvelles données réelles sont ajoutées, détruire les prédictions futures
    situations.delete_many({"horodateur":{"$gt": horodateur}})

    return len(predictions_a_detruire)
  
  return 0

# par souci de robustesse et pour l'initialisation d'une base de données, un programme
# un planifié est exécuté sur un serveur externe et garde les données en format csv
# les données collectées par ce programme peuvent être insérées dans la base de données
# en appelant cette fonction
# les fichiers csv doivent se trouver dans le répertoire csv
# il est possible de passer un filtre pour spécifier les fichiers à inclure
def ajouter_situations_fichiers_csv(filtre=""):
  dir_data = "data"
  try:
    journal = ouvrir_journal("chargement_massif")
    db = ouvrir_mongodb()
    situations = db.get_collection("situations")

    tous_fichiers = os.listdir(dir_data)
    tous_fichiers.sort()
    for nom_fichier in tous_fichiers:
      # ne traiter que les fichiers inclus dans le filtre
      if nom_fichier.find(filtre) < 0:
        continue
      nom_fichier = os.path.join(dir_data, nom_fichier)
      logstr(journal, f"Traitement du fichier {nom_fichier}...")
      if os.path.isfile(nom_fichier) and os.path.getsize(nom_fichier) != 0:
        df = pd.read_csv(nom_fichier, encoding="latin-1")
        ajouter_situations(df,situations,journal)
      else:
        print(f"Fichier {nom_fichier} vide.")

  except Exception as ex:
    print(f"Exception: {ex} sur {nom_fichier}")
  finally:
    db.client.close()
    journal.close()

# fonction utilisée pour remplir les données manquantes lors de l'initialisation d'une nouvelle
# base de données 
# pendant 24 heures après l'initialisation, des données approximatives sont utilisées
# après 24 heures d'utilisation, les données qui servent à remplacer les données manquantes 
# sont les données prédites par le système
def remplir_donnees():
  db = ouvrir_mongodb()
  col = db.get_collection("situations")
  # seulement pour les dernières 24 heures
  h = dt.now() - td(1)
  h = dt(h.year,h.month,h.day,h.hour)
  df = charger_situations({"horodateur":{"$gte":h}})

  # utiliser la moyenne des données
  df2 = df[["attente24","attente48","taux_occupation","rss","installation","civieres"]]
  df2 = df2.groupby("installation").mean().reset_index()
  situations = []
  base_h = h
  for _, i in charger_installations().iterrows():
    h = base_h
    while h < dt.now() + td(minutes=15):
      # si les données n'existent pas,, utiliser la moyenne
      if len(df[(df["installation"]==i.installation)&(df["horodateur"]==h)]) == 0:
        sit = df2[(df2["installation"]==i.installation)].to_dict(orient="records")[0]
        sit["jour_semaine"] = h.weekday()
        sit["heure"] = h.hour
        sit["horodateur"] = h
        sit["rempli"] = 1
        sit["niveau_prediction"] = 1
        situations.append(sit)
        print(sit)
      h += td(hours=1)
  print(situations)
  col.insert_many(situations)

# utiliser cette fonction pour extraire les données utilisées pour produire les prédictions
# retourne un dictionnaire composé des éléments suivants pour chaque installation éligible:
# - x_h: pour les 24 dernières heures, le nombre de patients pour civière pour 24 et 48 heures 
#        et le taux d'occupation de l'installation
# - x: le moment de la journée (période de 3 heures au cours de la journée), le jour de la semaine
#      la région sociosanitaire et le nombre de civières. Le nombre de civière est divisé par 100
#      pour être entre 0 et 1. Les autres données sont "catégorisées", c'est à dire transformées en
#      vecteurs d'une longueur égale au nombre de  valeurs possibles où chaque valeur est
#      représentée par un 1 ou un 0
# - installations: la dernière situation connue ou prédite
# le dictionnaire contient aussi "date", la date de la donnée la plus récente lue de la base de données
# pour être éligible, une installation doit avoir des données au cours de chaque heure précédente
# que ces données soient prédites ou réelles
def charger_historique_prediction(duree=24, journal=None):
  db = ouvrir_mongodb()
  col = db.get_collection("situations")
  try:
    # chercher date maximale
    dt_max = lire_heure_max(col)

    # si nous n'avons pas de données réelles disponibles et que les
    # données prédites encore valides pour 15 minutes
    if (not col.find_one({"horodateur": dt_max, "niveau_prediction": 0}) and
        dt_max > dt.now() + td(minutes=15)):
      logstr(journal, f"Des prédictions existent déjà pour {dt_max}")
      return None

    # aller chercher 24 heures au total, donc date - 23
    dt_min = dt_max - td(hours=(duree-1))
    df = charger_situations({"horodateur":{"$gte":dt_min}}, journal=journal)

    # trier par installations et par date afin de bâtir les données temporelles
    df = df.sort_values(by=["installation","horodateur"])
    x_h = []
    x = []
    y = []
    installations = []
    donnees_h = []

    precedent_inst = None
    for _, rec in df.iterrows():
      inst = rec.installation
      if precedent_inst is not None and precedent_inst != inst:
        logstr(journal, f"ERREUR: l'installation {precedent_inst} n'a que {len(donnees_h)} données.")
        donnees_h = []
      
      donnees_h.append(np.asarray([rec.attente24, rec.attente48, rec.taux_occupation]))
      if len(donnees_h) == duree:
        x_h.append(np.asarray(donnees_h))
        x.append(np.concatenate((
          en_categorie(int(rec.heure/3), 0, 7),
          en_categorie(rec.jour_semaine, 0, 6),
          # présentement on a entre 1 et 16 mais prévoyons un peu d'espace
          en_categorie(rec.rss, 0, 20),
          # ici je prévois un max de 100 civières, présentement 54, et je normalise d'avance
          (rec.civieres/100.0,)
          )))
        installations.append(rec.to_dict())
        donnees_h = []
        inst = None
      precedent_inst = inst

    return {"x_h": x_h, 
            "x": x, 
            "installations": installations,
            "date": dt_max}

  except Exception as ex:
    logstr(journal, f"Erreur en chargeant les données nécessaires à la prédiction: {ex}")
  finally:
    db.client.close()

# fonction qui prépare les données dans le format nécessaire à entraîner le réseau de neurones
# - x_h: pour les 24 dernières heures, le nombre de patients pour civière pour 24 et 48 heures 
#        et le taux d'occupation de l'installation
# - x: le moment de la journée (période de 3 heures au cours de la journée), le jour de la semaine
#      la région sociosanitaire et le nombre de civières. Le nombre de civière est divisé par 100
#      pour être entre 0 et 1. Les autres données sont "catégorisées", c'est à dire transformées en
#      vecteurs d'une longueur égale au nombre de  valeurs possibles où chaque valeur est
#      représentée par un 1 ou un 0
# - y: le taux d'occupation réel à déterminer, autrement dit, la cible utilisée lors de l'entraînement
def charger_historique(cond={}, duree=24, journal=None):
  df = charger_situations(cond, journal=journal)
  df_i = charger_installations(journal=journal)
  dt_min = min(df.horodateur)
  dt_max = max(df.horodateur)
  x_h = []
  x = []
  y = []
  for _, i in df_i.iterrows():
    logstr(journal, f"Traitement de l'installation {i.installation}")
    donnees_h = []
    dt_cur = dt_min
    while dt_cur < dt_max:
      sous_df = ((df.installation == i.installation) & (df.horodateur==dt_cur))

      # combien de rangées?
      # - 0, on recommence, pas assez d'historique...
      # - >1, pas bon du tout, il y a des données en double!
      if sum(sous_df) == 0:
        donnees_h = []
      elif sum(sous_df) != 1:
        raise Exception(f"Données en double. Installation: {i}, Horodateur: {dt_cur}.")
      else:
        donnees_h.append(np.asarray(df.loc[sous_df, ["attente24","attente48","taux_occupation"]])[0])
        if len(donnees_h) > duree:
          # si on atteint duree, garder les données dans le df ...
          x_h.append(np.asarray(donnees_h[:-1]))
          x.append(np.concatenate((
            en_categorie(int(dt_cur.hour/3), 0, 7),
            en_categorie(df[sous_df]["jour_semaine"].iloc(0), 0, 6),
            # présentement on a entre 1 et 16 mais prévoyons un peu d'espace
            en_categorie(df[sous_df]["rss"].iloc(0), 0, 20),
            # ici je prévois un max de 100 civières, présentement 54, et je normalise d'avance parce que plus simple!
            (df[sous_df]["civieres"].iloc[0]/100.0,)
            )))
          y.append(df.loc[sous_df, "taux_occupation"])
          # ... puis retirer la première données
          donnees_h = donnees_h[1:]
      dt_cur += td(hours=1)
  return {"x_h": x_h, "x": x, "y": y}

