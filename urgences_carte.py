from urgences_donnees import *
from colour import Color
import plotly.graph_objects as go
from datetime import datetime as dt, timedelta as td

def batir_gradient():
  c_r = Color("red")
  c_j = Color("yellow")
  c_v = Color("green")
  c_n = Color("black")
  # vert      ->jaune (4)
  # orange    ->rouge (2)
  # rouge foncés (2)
  return [x.hex for x in (
          list(c_v.range_to(c_j,4))+
          list(c_j.range_to(c_r,3))[1:] +
          list(c_r.range_to(c_n,5))[1:-2])]

def batir_carte(df=None):
  # pas à utiliser pour l'échelle, en pourcentage d'occupation
  PAS_ECHELLE=.25

  couleurs = batir_gradient()
  legende_couleurs = []
  for i in range(0, len(couleurs)-1):
    legende_couleurs += [f"De {int(i*PAS_ECHELLE*100)} à {int((i+1)*PAS_ECHELLE*100)}%"]
  legende_couleurs += [f"Plus de {int((len(couleurs)-1)*PAS_ECHELLE*100)}%"]

  if (df is None):
    df_i = charger_installations()
    df_s = charger_situations(max=True)
    df = pd.merge(df_i, df_s, on="installation")
  
  df["couleur"] = df["taux_occupation"].apply(
    lambda x: couleurs[min(int(x/PAS_ECHELLE), len(couleurs) -1)]
    )

  heure_pred = df.horodateur.apply(lambda x: x.strftime("%H:%M"))
  df["texte"] = (df.installation_nom + "<br>" +
                 df["adresse"] + "<br>" +
                 "Taux occupation prévu: " + round(df.taux_occupation*100, 2).astype(str) + "% à " + heure_pred + "<br>" )

  fig = go.Figure()
  for couleur,legende in zip(couleurs,legende_couleurs):
    installations = df[df["couleur"]==couleur]
    if len(installations):
      fig.add_trace(go.Scattermapbox(
                    lon=installations["longitude"],
                    lat=installations["latitude"],
                    name=legende,
                    mode="markers",
                    text=installations["texte"],
                    hoverinfo="text",
                    marker=dict(
                        color=couleur,
                        size=10)))

  fig.update_layout(
      mapbox = {
          'style': "open-street-map",
          'center': {'lon': -71.21, 'lat': 46.81 },
          'zoom': 5},
      legend_title= "Taux d'occupation",
      title = "Situation dans les urgences")

  fig.write_html("carte/carte_quebec.html")
  
def afficher_carte():
  import webbrowser
  df = charger_installations()
  batir_carte()
  webbrowser.open(os.path.join(os.getcwd(), "carte/carte_quebec.html"))



if __name__ == "__main__":
  batir_carte()
  
