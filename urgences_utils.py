from datetime import datetime as dt
import os

# affiche et à l'écran et écrit dans le fichier journal s'il est défini
# f = fichier journal
# s = chaîne de caractères à imprimer
def logstr(f,s):
  if f:
    f.write(f"{s}\n")
    f.flush()
  print(s)

# ouverture du fichier journal dans le répertoire logs
def ouvrir_journal(base):  
  if not os.path.exists("logs"):
    os.makedirs("logs")
  
  fn = f"logs/{base}_{dt.strftime(dt.now(), '%Y%m%d%H%M%S')}.log"
  return open(fn, "w")

# transformer les valeurs en catégories, par exemple, si on a 4 valeurs possibles,
# 1,2,3 deviendra (1,0,0,0), (0,1,0,0) et (0,0,1,0)
def en_categorie(val, min, max):
  return [val==i for i in range(min, max + 1)]

