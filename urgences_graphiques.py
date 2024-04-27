from urgences_donnees import *
from datetime import datetime as dt, timedelta as td
from matplotlib import pyplot as plt, dates as mdates, ticker as mtick

dfs = charger_situations(heures=24)
dfp = charger_predictions(heures=24)
dfi = charger_installations()

# retirer les prédictions du df des situations
dfs.loc[dfs.niveau_prediction!=0, "taux_occupation"] = None

for _, i in dfi.iterrows():
  plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
  plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
  plt.plot(dfs[dfs.installation==i.installation].horodateur,
           dfs[dfs.installation==i.installation].taux_occupation,
           label="Situation réelle")
  plt.plot(dfp[dfp.installation==i.installation].horodateur,
           dfp[dfp.installation==i.installation].taux_occupation,
           label="Notre prédiction")
  plt.legend(loc='center left')

  n = i.installation_nom
  n = n.replace("CENTRE MULTISERVICES DE SANTÉ ET DE SERVICES SOCIAUX", "CENTRE MULTISERVICES")
  n = n.replace("L'HÔPITAL", "HÔPITAL")
  n = n.replace("L'HÔTEL", "HÔTEL")
  plt.title(n, fontsize=11)  
  plt.suptitle(f"Situation à l'urgence ({dt.now().strftime('%d/%m/%Y')})")
  plt.xlabel("Heure du jour")  # Titre de l'axe x
  plt.ylabel("Taux d'occupation")  # Titre de l'axe y

  plt.savefig(f"graphiques/{i.installation}.png")
  plt.close()
