import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px

# Charger le jeu de données des ventes automobiles
data = pd.read_csv('historical_automobile_sales.csv')

# Initialiser l'application Dash
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

# Liste des années de 1980 à 2013 incluses
year_list = [i for i in range(1980, 2014, 1)]

# ==========================================
# DISPOSITION DE L'APPLICATION (TÂCHES 2.1 à 2.3)
# ==========================================
app.layout = html.Div(children=[
    # TÂCHE 2.1 : Ajouter le titre requis avec son style exact
    html.H1(
        "Tableau de bord des statistiques de ventes automobiles",
        style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 24}
    ),
    
    # Éléments de contrôle (Menus déroulants)
    html.Div([
        # TÂCHE 2.2 : Menu déroulant pour le type de rapport
        html.Div([
            html.Label("Sélectionnez le type de rapport :"),
            dcc.Dropdown(
                id='dropdown-statistics',
                options=[
                    {'label': 'Statistiques de période de récession', 'value': 'Recession Period Statistics'},
                    {'label': 'Statistiques annuelles', 'value': 'Yearly Statistics'}
                ],
                placeholder='Select a report type',
                value='Select Statistics',
                style={'width': '80%', 'padding': '3px', 'fontSize': '20px', 'textAlign': 'center'}
            )
        ], style={'padding': '10px'}),
        
        # TÂCHE 2.2 : Menu déroulant pour la sélection de l'année
        html.Div([
            html.Label("Sélectionnez l'année :"),
            dcc.Dropdown(
                id='select-year',
                options=[{'label': i, 'value': i} for i in year_list],
                placeholder='Select-year',
                value='Select-year',
                style={'width': '80%', 'padding': '3px', 'fontSize': '20px', 'textAlign': 'center'}
            )
        ], style={'padding': '10px'})
    ]),
    
    # TÂCHE 2.3 : Division conteneur pour afficher les graphiques en sortie
    html.Div([
        html.Div(id='output-container', className='chart-grid', style={'display': 'flex', 'flexDirection': 'column'})
    ])
])

# ==========================================
# FONCTIONS DE RAPPEL (TÂCHES 2.4 à 2.6)
# ==========================================

# TÂCHE 2.4 : Rappel pour activer/désactiver le choix de l'année
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value')
)
def update_input_container(selected_statistics):
    if selected_statistics == 'Yearly Statistics': 
        return False
    else: 
        return True


# TÂCHES 2.5 et 2.6 : Rappel principal pour générer et afficher les graphiques
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'),
     Input(component_id='select-year', component_property='value')]
)
def update_output_container(selected_statistics, input_year):
    # ---- TÂCHE 2.5 : STATISTIQUES DE PÉRIODE DE RÉCESSION ----
    if selected_statistics == 'Recession Period Statistics':
        recession_data = data[data['Recession'] == 1]
        
        # Graphique 1 : Fluctuation des ventes (Ligne)
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec, x='Year', y='Automobile_Sales', 
                           title="Fluctuation moyenne des ventes d'automobiles par année pendant les récessions")
        )
        
        # Graphique 2 : Ventes moyennes par type de véhicule (Barres)
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(
            figure=px.bar(average_sales, x='Vehicle_Type', y='Automobile_Sales', 
                          title="Nombre moyen de véhicules vendus par type de véhicule durant la récession")
        )
        
        # Graphique 3 : Part des dépenses publicitaires (Secteurs)
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(
            figure=px.pie(exp_rec, values='Advertising_Expenditure', names='Vehicle_Type', 
                          title="Part des dépenses publicitaires totales par type de véhicule")
        )
        
        # Graphique 4 : Effet du taux de chômage par type de véhicule (Barres)
        unemp_data = recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(
            figure=px.bar(unemp_data, x='unemployment_rate', y='Automobile_Sales', color='Vehicle_Type',
                          labels={'unemployment_rate': 'Unemployment Rate', 'Automobile_Sales': 'Average Sales'},
                          title='Effet du taux de chômage sur le type de véhicule et les ventes')
        )
        
        # Grille 2x2 pour le rapport de récession
        return [
            html.Div([
                html.Div(children=R_chart1, style={'width': '50%'}),
                html.Div(children=R_chart2, style={'width': '50%'})
            ], style={'display': 'flex'}),
            html.Div([
                html.Div(children=R_chart3, style={'width': '50%'}),
                html.Div(children=R_chart4, style={'width': '50%'})
            ], style={'display': 'flex'})
        ]

    # ---- TÂCHE 2.6 CORRIGÉE : STATISTIQUES ANNUELLES ORDRE CHRONOLOGIQUE ----
    elif (input_year and selected_statistics == 'Yearly Statistics'):
        try:
            year_val = int(input_year)
        except ValueError:
            return []
            
        yearly_data = data[data['Year'] == year_val]
        
        # Définir l'ordre chronologique exact pour l'axe X du graphique mensuel
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        
        # Graphique 1 : Ventes moyennes globales par année (Ligne)
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(yas, x='Year', y='Automobile_Sales', 
                           title="Ventes annuelles d'automobiles sur l'ensemble de la période")
        )
        
        # Graphique 2 : Ventes mensuelles totales avec ordre chronologique appliqué
        mas = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(
            figure=px.line(mas, x='Month', y='Automobile_Sales', 
                           category_orders={"Month": month_order},
                           title=f"Ventes mensuelles totales d'automobiles pour l'année {input_year}")
        )
        
        # Graphique 3 : Nombre moyen de véhicules vendus par type (Barres)
        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(
            figure=px.bar(avr_vdata, x='Vehicle_Type', y='Automobile_Sales', 
                          title=f"Nombre moyen de véhicules vendus par type en {input_year}")
        )
        
        # Graphique 4 : Dépenses publicitaires totales par véhicule (Secteurs)
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(
            figure=px.pie(exp_data, values='Advertising_Expenditure', names='Vehicle_Type', 
                          title=f"Dépenses publicitaires totales pour chaque véhicule en {input_year}")
        )
        
        # Grille 2x2 pour le rapport annuel
        return [
            html.Div([
                html.Div(children=Y_chart1, style={'width': '50%'}),
                html.Div(children=Y_chart2, style={'width': '50%'})
            ], style={'display': 'flex'}),
            html.Div([
                html.Div(children=Y_chart3, style={'width': '50%'}),
                html.Div(children=Y_chart4, style={'width': '50%'})
            ], style={'display': 'flex'})
        ]
        
    return []

# Lancer l'application
if __name__ == '__main__':
    app.run(debug=True)
