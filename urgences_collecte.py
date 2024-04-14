import requests
from urgences_utils import *
from urgences_donnees import *
from urgences_rnn import *
import pandas as pd
from io import StringIO
import time
from datetime import timedelta as td, datetime as dt

def collecter_situations(journal=None):
  CSV_URL = "https://www.msss.gouv.qc.ca/professionnels/statistiques/documents/urgences/Releve_horaire_urgences_7jours_nbpers.csv"

  db = None
  try:
    db = ouvrir_mongodb()
    situations = db.get_collection("situations")

    response = requests.get(CSV_URL)

    if response.status_code == 200:
      content = response.content.decode('latin-1')
      df = pd.read_csv(StringIO(content))
      ajouter_situations(df, situations, journal)
      return True
    else:
      logstr(journal, f"La requête vers {CSV_URL} a échoué.")
      return False
  except Exception as ex:
    logstr(journal, ex)
  finally:
    if db is not None:
      db.client.close()

def ajouter_prediction(journal=None):
  histo = charger_historique_prediction(journal=journal)
  if histo is None:
    return False
  
  preds = predire(histo)
  db = ouvrir_mongodb()
  col = db.get_collection("situations")
  horodateur = histo["date"] + td(hours=1)
  base = {"horodateur":  horodateur,
          "jour_semaine": horodateur.weekday(),
          "heure": horodateur.hour}
  situations = []
  if col.find_one({"horodateur":horodateur}):
    logstr(journal, f"Il y a déjà des prédictions pour {horodateur}")
  else:
    for installation, pred in zip(histo["installations"], preds):
      # ne pas conserver le _id lors de l'insertion
      situation = {
        **installation,
        **base,
        "taux_occupation": pred
      }
      situation["niveau_prediction"]+=1
      situation["mise_a_jour"]=None
      del situation["_id"]
      situations.append(situation)
    
    col.insert_many(situations)
  return True

def demarrer_boucle_collecte():
  journal = None
  try:
    journal = ouvrir_journal("collecte")
    while True:
      collecter_situations(journal)
      ajouter_prediction(journal)
      time.sleep(600)
  except Exception as ex:
    logstr(journal, f"Exception lors du chargement {ex}")
    if journal:
      journal.close()

if __name__ == "__main__":
  demarrer_boucle_collecte()
