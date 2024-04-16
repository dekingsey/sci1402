#  Fonctionnement

## Collecte des données
Les données sont récoltées de façon horaire à partir du site de Données Québec, épurées et stockées dans une base de données MongoDB sur la plateforme Atlas.

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

