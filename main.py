import pandas as pd
import openpyxl as pxl
import gunicorn
import dash
import plotly.express as px
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

pd.options.display.width= None
pd.options.display.max_columns= None
pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 5000)



pref_rec_data = pd.read_csv('PREFERENTIE_RECEPTVERWERKING_MERGE_CGM_NCHECKER_AG_DASHBOARD.csv')
# print(pref_rec_data.columns)
# print(pref_rec_data['Verzekeraar'].unique())



mnd_jr_keuzes = pref_rec_data[['MAAND_x', 'JAAR_x', 'MAAND-JAAR_x']]
sorted_m_j_keuzes = mnd_jr_keuzes.sort_values(by=[ 'MAAND_x','JAAR_x', 'MAAND-JAAR_x'])
maand_jaar_keuze_dropdown = sorted_m_j_keuzes.drop_duplicates()

#======== grafiek met totaal aan gemiste 'voorradige' verstrekkingen per medewerker per maand ==================================================================#

mw_pref = pref_rec_data.groupby(by=['MAAND-JAAR_x', 'Verzekeraar' ,'APOTHEEK', 'MW', 'Vrd'])['MW'].count().to_frame(name='verstrekkingen gemist/mw/maand').reset_index()   # dataframe voor grafiek
mw_pref_filter = mw_pref.loc[(mw_pref['MAAND-JAAR_x'] == '11-2023') & (mw_pref['APOTHEEK'] == 'HANZEPLEIN')& (mw_pref['Vrd'] == 'Ja')]                     # filters voor de callbacks (APOTHEEK, MAAND-JAAR, OP vrd bij mosadex)

# ==========grafiek met totaal aan gemiste 'voorradige' verstrekkingen per medewerker per maand(artikelen zichtbaar per medewerker) ======================================================================

mw_art_pref = pref_rec_data.groupby(by=['MAAND-JAAR_x', 'Verzekeraar', 'ZI-ETIKETNAAM NIET PREF VERSTR.', 'ZI-ETIKETNAAM PREF.', 'MW', 'Vrd', 'APOTHEEK', ])['MW'].count().to_frame(name='gemiste verstr/mw/prod/mnd').reset_index()   # dataframe voor grafiek
mw_art_pref_filter = mw_art_pref.loc[(mw_art_pref['APOTHEEK']=='OOSTERPOORT') & (mw_art_pref['MAAND-JAAR_x'] == '11-2023') & (mw_art_pref['Vrd'] == 'Ja')]                                                              # filters voor de callbacks (APOTHEEK, MAAND-JAAR_x, Vrd mos)


#======== grafiek met totaal aan gemiste 'voorradige' verstrekkingen per product per maand ==================================================================#

pref_product = pref_rec_data.groupby(by=['MAAND-JAAR_x', 'Verzekeraar', 'ZI-ETIKETNAAM PREF.', 'APOTHEEK', 'Vrd'])['ZI-ETIKETNAAM PREF.'].count().to_frame(name='telling gemiste producten/mnd').reset_index()                     # Dataframe voor de grafiek
pref_product_filter = pref_product.loc[(pref_product['APOTHEEK']=='HANZEPLEIN')&(pref_product['MAAND-JAAR_x']=='01-2023')&(pref_product['Vrd']=='Ja')].nlargest(n=20, columns=['telling gemiste producten/mnd'])   # Filters voor de callbacks (APOTHEEK, MAAND-JAAR, Op vrd ja/nee bij mosadex, top zoveel)


# ===============================================================================================================================================================================================






load_figure_template('bootstrap')

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.layout = html.Div([

    dbc.Row([
        html.H1('DASHBOARD AG APOTHEKEN',
                style={'textAlign': 'center'})
    ]),
    html.Br(),
    html.Br(),

    dbc.Row([
        html.H5('Stap 1: Kies een Apotheek',
                style={'textAlign':'center'})
    ]),

    dbc.Row([
        dbc.Col([], width=4),
        dbc.Col([
            dcc.Dropdown(id='kies apotheek',
                         options=pref_rec_data['APOTHEEK'].unique(),
                         value=pref_rec_data['APOTHEEK'].min(),
                         style={'textAlign':'center'})

        ], width=4),
        dbc.Col([

        ], width=4)


    ]),

    html.Br(),
    html.Br(),

    dbc.Row([
        dbc.Col([], width=4),
        dbc.Col([
            html.H5('Kies een verzekeraar', style={'textAlign':'center'}),
            dcc.Dropdown(id='kies verzekeraar',
                         options=pref_rec_data['Verzekeraar'].unique(),
                         value=pref_rec_data['Verzekeraar'].min(),
                         style={'textAlign':'center'})
        ]),
        dbc.Col([], width=4)
    ]),

    html.Br(),
    html.Br(),

    dbc.Row([
        html.H5('Stap 2: Kies een maand',
                style={'textAlign': 'center'})
    ]),


    dbc.Row([
        dbc.Col([], width=4),
        dbc.Col([
            dcc.Dropdown(id='kies maand',
                         options=maand_jaar_keuze_dropdown['MAAND-JAAR_x'].unique(),
                         value=maand_jaar_keuze_dropdown['MAAND-JAAR_x'].max(),
                         style={'textAlign':'center'})
        ], width=4),
        dbc.Col([], width=4)
    ]),

    html.Br(),
    html.Br(),

    dbc.Row([
        dbc.Col([], width=4),
        dbc.Col([
            html.H5('Was het product op voorraad bij mosadex?', style={'textAlign':'center'}),
            dcc.RadioItems(id= 'op voorraad?',
                       options=pref_rec_data['Vrd'].unique(),
                       value=pref_rec_data['Vrd'].min(),
                       style={'textAlign':'center'},
                       inline=True)

        ], width=4),
        dbc.Col([], width=4)

    ]),

    html.Br(),
    html.Br(),

    dbc.Row([
        html.H5('AANTAL GEMISTE VERSTREKKINGEN PER MEDEWERKERSCODE', style={'textAlign': 'center'}),
        dcc.Graph(id='grafiek 1: preferentie per medewerker')
    ]),

    html.Br(),
    html.Br(),

    dbc.Row([
        html.H5('AANTAL GEMISTE PREFERENTE VERSTREKKINGEN PER MEDEWERKERSCODE MET VERSTREKT PRODUCT', style={'textAlign': 'center'}),
        dcc.Graph(id='grafiek 2: preferentie per medewerker met product')
    ]),

    html.Br(),
    html.Br(),

    dbc.Row([
        html.H5('TOP GEMISTE PREFERENTE VERSTREKKINGEN OVER DE MAAND', style={'textAlign': 'center'}),



    ]),

    html.Br(),
    html.Br(),
    dbc.Row([
        dbc.Col([], width=4),
        dbc.Col([
            html.H6('Kies de top-x aantal gemiste preferente verstrekkingen',style={'textAlign': 'center'}),
            dcc.RadioItems(id='top x gemiste verstrekkingen',
                       options=[10, 20, 30, 50, 100],
                       value=10,
                       inline=True,
                       style={'textAlign':'center'})

        ], width=4),
        dbc.Col([], width=4)
    ]),

    html.Br(),
    html.Br(),

    dbc.Row([
    dcc.Graph(id='grafiek 3: top zoveel gemiste verstrekkingen per product')
    ])




])

@callback(
    Output('grafiek 1: preferentie per medewerker', 'figure'),
    Output('grafiek 2: preferentie per medewerker met product', 'figure'),
    Output('grafiek 3: top zoveel gemiste verstrekkingen per product', 'figure'),
    Input('kies apotheek', 'value'),
    Input('kies maand', 'value'),
    Input('kies verzekeraar', 'value'),
    Input('top x gemiste verstrekkingen', 'value'),
    Input('op voorraad?', 'value')
)

def update_grafieken(apotheek, maand, verzekeraar, top, voorraad):

    mw_pref_filter = mw_pref.loc[(mw_pref['MAAND-JAAR_x'] == maand) & (mw_pref['APOTHEEK'] == apotheek) & (mw_pref['Vrd'] == voorraad)& (mw_pref['Verzekeraar'] == verzekeraar)]

    grafiek_1_preferentie_per_medewerker = px.bar(mw_pref_filter, x='MW', y='verstrekkingen gemist/mw/maand')


    mw_art_pref = pref_rec_data.groupby(by=['MAAND-JAAR_x', 'Verzekeraar','ZI-ETIKETNAAM NIET PREF VERSTR.', 'ZI-ETIKETNAAM PREF.', 'MW', 'Vrd', 'APOTHEEK', ])['MW'].count().to_frame(name='gemiste verstr/mw/prod/mnd').reset_index()  # dataframe voor grafiek
    mw_art_pref_filter = mw_art_pref.loc[(mw_art_pref['APOTHEEK'] == apotheek) & (mw_art_pref['MAAND-JAAR_x'] == maand) & (mw_art_pref['Vrd'] == voorraad)& (mw_art_pref['Verzekeraar'] == verzekeraar)]  # filters voor de callbacks (APOTHEEK, MAAND-JAAR_x, Vrd mos)

    grafiek_2_preferentie_per_medewerker_per_product = px.bar(mw_art_pref_filter, x='MW', y='gemiste verstr/mw/prod/mnd', color='ZI-ETIKETNAAM NIET PREF VERSTR.')


    pref_product = pref_rec_data.groupby(by=['MAAND-JAAR_x', 'Verzekeraar', 'ZI-ETIKETNAAM PREF.', 'APOTHEEK', 'Vrd'])['ZI-ETIKETNAAM PREF.'].count().to_frame(name='telling gemiste producten/mnd').reset_index()  # Dataframe voor de grafiek
    pref_product_filter = pref_product.loc[(pref_product['APOTHEEK'] == apotheek) & (pref_product['MAAND-JAAR_x'] == maand) & (pref_product['Vrd'] == voorraad)& (pref_product['Verzekeraar'] == verzekeraar)].nlargest(n=top, columns=['telling gemiste producten/mnd'])  # Filters voor de callbacks (APOTHEEK, MAAND-JAAR, Op vrd ja/nee bij mosadex, top zoveel)

    grafiek_3_top_zoveel_gemiste_verstrekkingen_per_product = px.bar(pref_product_filter, x='ZI-ETIKETNAAM PREF.', y='telling gemiste producten/mnd')

    return grafiek_1_preferentie_per_medewerker, grafiek_2_preferentie_per_medewerker_per_product, grafiek_3_top_zoveel_gemiste_verstrekkingen_per_product


if __name__ == '__main__':
    app.run_server(debug=True)







#
# vs = pd.read_excel('verstrekkingen_ex_distr.xlsx')
# print(vs.head())
#
#
# app = Dash(__name__)
# server = app.server
#
# app.layout = html.Div([
#
#     html.H1('Vul het ZI nummer in en zoek het aantal verstrekkingen per maand',
#             style={'textAlign':'center'}),
#
#     dcc.Input(id='aaa',
#               type='number',
#               debounce=True), #debounce, zodat je eerst een 'enter' moet intoetsen voor je iets gaat zien,
#
#     dcc.RadioItems(id='wel_geen_cf',
#                    options=['GEEN CF','WEL CF'],
#                    value='WEL CF'),
#
#     html.H3('Verstrekkingen per maand in apotheek Hanzeplein',
#             style={'textAlign':'center'}),
#
#     dcc.Graph(id='verstrekkingen per maand'),
#
#
# ])
#
# @callback(
#
#     Output('verstrekkingen per maand', 'figure'),
#     Input('aaa', 'value'),
#     Input('wel_geen_cf', 'value')
# )
#
#
# def update_grafiek(zi, cf):
#
#     filtered = vs.loc[vs['ZI'] == zi] # hier zorg je ervoor dat je in het dataframe een zi gaat zoeken
#
#     if cf == 'WEL CF':                                                            # als de waarde in de radio items 'WEL CF' is laat je het dataframe onaangeroerd
#         filtered_cf = filtered
#     else:
#         filtered_cf = filtered.loc[filtered['RECEPTHERKOMST'] != 'CF']            # als de waarde in de radio items iets anders is ga je zo fileren dat de CF verstrekkingen er niet in zitten
#
#     fig = px.bar(filtered_cf,                                                     # maak een grafiek van het resultaat van je ifelse loop
#                  x='MAAND-JAAR',
#                  y='verstrekkingen per maand',
#                  color='ZI - ETIKETNAAM',
#                  title='VERSTREKKINGEN/MAAND/INCL CF')
#
#     return fig                                                                    # laat de grafiek zien in de app van het resultaat
#
# if __name__ == '__main__':                                                        # draai de app
#     app.run(debug=True)
#
