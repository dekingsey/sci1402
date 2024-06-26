from urgences_donnees import *
from urgences_collecte import *
from urgences_rnn import *
from urgences_carte import *
from os import environ

def afficher_menu():
  # Affichage du menu
  print("Menu:")
  print("1) Charger les fichiers CSV du répertoire data")
  print("2) Entraîner modèle")
  print("3) Démarrer la boucle de lecture")
  print("x) Sortie")

def main():
  if not "MONGO_URI" in environ:
    print("La variable MONGO_URI doit être définie pour pouvoir établir une connexion à la base de données MongoDB.")
    print(".")
    return
  while True:
    afficher_menu()
    choix = input("Entrez votre choix: ")

    if choix == "1":
      ajouter_situations_fichiers_csv()
    elif choix == "2":
      entrainer_modele()
      print("Un fichier .keras et un fichier .echelle ont été créés. Remplacer modele.keras et modele.echelle par ces fichiers pour utiliser le nouveau modele.")
    elif choix == "3":
      # si les données comportent des données manquantes, utiliser la moyenne
      # pendant les 24 premières heures, ces données ajustées seront utilisées
      # après 24 heures, les prédictions seront utilisées
      remplir_donnees()
      demarrer_boucle_collecte()
    elif choix.lower() == "x":
      print("Au revoir!")
      break
    else:
      print("Choix invalide.")

if __name__ == "__main__":
  main()

