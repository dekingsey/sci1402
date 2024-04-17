#  Fonctionnement

## Collecte des données
Les données sont collectées de façon horaire à partir du site de Données Québec, épurées et stockées dans une base de données MongoDB sur la plateforme Atlas.

Les données sont stockées dans deux collections: `situations` qui contient les données horaires pour chaque installation, et `installations` qui contient les données des différentes installations.

## Production de données prédites
Un modèle  combiné utilisant la librairie keras est entraîné à l’aide de ces données. Le modèle choisi est un réseau de neurones LSTM profond dont le résultat est combiné à des données non-temporelles pour être traité par trois couches de neurones Dense produisant un prédiction des taux d'occupation:
![Réseau de neurones](/ressources/RNA.png)

La performance du modèle a été mesurée en calculant l'erreur quadratique moyenne (MSE) entre la prédiction et la valeur réelle. L'objectif à atteindre avec le modèle était une performance supérieure à l'utilisation de la dernière donnée précédent la donnée à prédire. 
```
Cible à battre: 0.00213267531385084
Score: 0.0020986351166595576
```

## Création de la carte

Suite à l'acquisition de nouvelles données ou lorsque les prédictions ne sont valides que pour 15 minutes ou moins, des prédicitons sont faites en utilisant ce modèle et stockée dans la base de données. Par la suite une carte des installations affichant ces prédictions est produite en utilisant la librairie `pyplot.graph_objects`:
![Réseau de neurones](/ressources/carte.png)

## Utilisation

### Prérequis

Une base de données MongoDB. La variable environnementale `MONGO_URI` doit contenir la chaîne de connexion pour cette base de données. 
### Librairies requises
Les libraires suivantes sont requises pour ce projet :
- `pymongo`
- `keras`
- `pickle`
- `pandas`
- `plotly`

### Première utilisation

Après avoir défini la variable environnementale `MONGO_URI`, installé les librairies requises et téléchargé l'entièreté du projet, lancer `urgences_menu.py`. Le menu suivant sera affiché:
[Menu](ressources/menu.png)
Appliquer les étapes suivantes:
 - Utiliser l'option 1 pour créer la base de données initiale. Si le projet est arrêté pour une période, cette étape permet aussi de mettre à niveau la base de données avec de nouveaux fichiers CSV.
 - Ensuite, utiliser l'option 2 pour regénérer le modèle de réseau de neurones. Le fichiers générés devront remplacer les fichiers `modele/modele.keras` et `modele/modele.echelle`.
 - À cette étape, la base de données contient les données nécessaires à la prédiction de données et la production de la carte. L'option 3 lance une boucle qui se charge de cette tâche.
