from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.express as px
import re
from plotly.io import to_json
import numpy as np

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    """
    Simple fonction pour la page d'accueil
    :return: Renvoi vers home.html (page d'accueil
    """
    return render_template("home.html")


@app.route('/var', methods=['GET'])
def variables():
    """
    Fonction qui traite toutes les colonnes de notre CSV afin de les décrirent sous forme quantitative ou qualitative
    :return: Renvoi vers variables.html
    """

    # Adaptez le chemin à votre poste
    df = pd.read_csv(
        r"C:\Users\Bloup\OneDrive\Project_FLASK_2/ina-barometre-jt-tv-donnees-mensuelles-2005-2018-nombre-de-sujets.csv",
        encoding='1252', delimiter=';')

    # Reformate la date
    df["MOIS"] = pd.to_datetime(df["MOIS"], format="%d/%m/%Y")

    ################################################################
    # Description Variable Année

    df2 = df

    df2["ANNEE"] = pd.DatetimeIndex(df2["MOIS"]).year
    date_toto = df2.iloc[:, [8, 9]].groupby(["ANNEE"]).sum()
    date_mean = round(df2.iloc[:, [8, 9]].groupby(["ANNEE"]).mean(), 2)
    date_std = round(df2.iloc[:, [8, 9]].groupby(["ANNEE"]).std(), 2)

    df2["MONTH"] = pd.DatetimeIndex(df2["MOIS"]).month
    month_toto = df2.iloc[:, [8, 10]].groupby(["MONTH"]).sum()

    ################################################################
    # Description Variable Thématique

    thematique_grouped = df.groupby("THEMATIQUES").sum()
    grouped_total = thematique_grouped.iloc[:, 6]
    effectif_thematique = thematique_grouped.iloc[:, 6].sum()
    percent_tot = round((grouped_total / effectif_thematique) * 100, 2)

    ################################################################
    # Description Variables Chaînes

    mean_tot_chaine = round(df.iloc[:, 2:8].mean(), 2)
    std_tot_chaine = round(df.iloc[:, 2:8].std(), 2)
    sum_tot_chaine = df.iloc[:, 2:8].sum()

    ################################################################
    # Graph Variable Année

    fig_date_toto = px.line(date_toto, x=date_toto.index, y=date_toto["Totaux"], labels={
                                                                                            "ANNEE": "",
                                                                                            "Totaux": ""
                                                                                        })
    fig_date_toto.update_traces(mode='markers+lines')

    fig_date_toto.update_layout({
                                    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                                })

    figure_date_toto = to_json(fig_date_toto)

    ################################################################
    # Graph Variable Thématique
    fig = px.pie(grouped_total, names=grouped_total.index, values="Totaux")
    fig.update_layout({
                            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                      })
    fig.update_layout(legend=dict(
                                        yanchor="top",
                                        y=0.99,
                                        xanchor="left",
                                        x=0
                                  ))
    figure_thematique = to_json(fig)

    ################################################################
    # Graph Variables Chaînes
    fig_tot_chaine = px.histogram(std_tot_chaine, x=std_tot_chaine.index, y=sum_tot_chaine, color=std_tot_chaine.index
                                  , labels={
                                                "index": "",
                                                "count": "",
                                                "sum of y": "",
                                                "y": ""
                                            })
    fig_tot_chaine.update_layout({
                                    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                                  })
    figure_chaines = to_json(fig_tot_chaine)

    return render_template("variables.html", date_mean=date_mean, date_std=date_std,
                           grouped_total=grouped_total, percent_tot=percent_tot, mean_tot_chaine=mean_tot_chaine,
                           std_tot_chaine=std_tot_chaine, figure_date_toto=figure_date_toto,
                           figure_thematique=figure_thematique, figure_chaines=figure_chaines)


@app.route('/formulaire', methods=['GET', 'POST'])
def form():
    """
    Fonction qui affiche un formulaire et renvoi ces informations sur un graphique
    :return: Renvoi vers formulaire.html afin de choisir les variables à afficher dans le graph
             Renvoi vers graphique.html pour l'affichage du graph selon les variables du formulaire
    """

    # Adaptez le chemin à votre poste
    df = pd.read_csv(
        r"C:\Users\Bloup\OneDrive\Project_FLASK_2/ina-barometre-jt-tv-donnees-mensuelles-2005-2018-nombre-de-sujets.csv",
        delimiter=";", sep=r'\s*,\s*', encoding='1252')

    # Reformate la date
    df["MOIS"] = pd.to_datetime(df["MOIS"], format="%d/%m/%Y")

    nom_thematique = df.iloc[:, 1].unique()
    nom_chaines = df.iloc[:0, [2, 3, 4, 5, 6, 7]]
    df2 = df
    df2["ANNEE"] = pd.DatetimeIndex(df2["MOIS"]).year
    schema_theme_date = []

    if request.method == "POST":
        retour_html_theme = request.form.get('nom_thematique')
        retour_html_chaines = request.form.get('nom_chaines')

        # Si uniquement un thème est choisi
        if retour_html_theme != "all" and retour_html_chaines == "all":
            df3 = df2.query('THEMATIQUES == "' + retour_html_theme + '"')
            date_toto = df3.iloc[:, [8, 9]].groupby(["ANNEE"]).sum()
            schema_theme_date = px.line(date_toto, x=date_toto.index, y=date_toto["Totaux"],
                                        labels={
                                                    "ANNEE": "",
                                                    "Totaux": ""
                                                })

        # Si uniquement une chaîne est choisi
        elif retour_html_chaines != "all" and retour_html_theme == "all":
            df4 = df2.loc[:, [retour_html_chaines, "ANNEE"]]
            date_toto = df4.groupby(["ANNEE"]).sum()
            schema_theme_date = px.line(date_toto, x=date_toto.index, y=date_toto[retour_html_chaines],
                                        labels={
                                                    "ANNEE": "",
                                                    "Totaux": ""
                                                })
            schema_theme_date.update_traces(mode='markers+lines')

        # Si rien n'est choisi
        elif retour_html_chaines == "all" and retour_html_theme == "all":
            return render_template("formulaire.html", nom_thematique=nom_thematique, nom_chaines=nom_chaines)

        # Si tout est choisi
        else:
            df3 = df2.query('THEMATIQUES == "' + retour_html_theme + '"')
            df4 = df3.loc[:, [retour_html_chaines, "ANNEE"]]
            date_toto = df4.groupby(["ANNEE"]).sum()
            schema_theme_date = px.line(date_toto, x=date_toto.index, y=date_toto[retour_html_chaines],
                                        labels={
                                                    "ANNEE": "",
                                                    "Totaux": ""
                                                })
            schema_theme_date.update_traces(mode='markers+lines')

        schema_theme_date = to_json(schema_theme_date)
        return render_template("graphique.html", schema_theme_date=schema_theme_date,
                               retour_html_theme=retour_html_theme)

    return render_template("formulaire.html", nom_thematique=nom_thematique, nom_chaines=nom_chaines)


if __name__ == '__main__':
    app.run()
