import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image

def format_amount(amount)-> pd.Series :
    return amount.apply(lambda x: f'{x:,}'.replace(',','.')) 

def mapping_player_nation_geo(name):
    if name in map_geojson:
        return map_geojson[name]
    else:
        return name

icon = Image.open("UNED.png") 
st.set_page_config(page_title="Estadísticas de rendimientos y valores de mercado de futbolistas de clubes europeos", layout="wide",
                   page_icon=icon)
icon1=":material/thumb_up:"
icon2=":material/thumb_up:"
icon3=":material/thumb_up:"
icon4=":material/thumb_up:"
icon5=":material/thumb_up:"

st.markdown('<style>#vg-tooltip-element{z-index: 1000051}</style>',
             unsafe_allow_html=True)
## https://github.com/vega/vega-tooltip/pull/507 fix multiple creation of tooltip element for each chart in document, fix tooltip added to the correct document.body 
## or document.fullscreenElement (depending on fullscreen mode)

## Desactivo el maximo de filas a mostrar de Altair, porque pueden ser muchas
alt.data_transformers.disable_max_rows()   

with st.expander("Jugadores por temporada..."):
    ### PRIMER GRÁFICO CON EL NUMERO DE JUGADORES POR TEMPORADA
    st.markdown(" ### NÚMERO DE JUGADORES POR TEMPORADA")
    st.markdown(" Mostramos en una gráfico de lineas el número de jugadores distintos de que disponemos por temporada. "\
                "Vemos que los datos recogidos son de entre 2008/2009 y 2015/2016")
    
    df_mkt_player_team_matches = pd.read_csv('df_mkt_player_team_matches_v2.csv', header=0)
    df_altair1 = pd.DataFrame(index=['numero_jugadores'])    
    for i in np.arange(2009,2017):
        count = len(df_mkt_player_team_matches.loc[df_mkt_player_team_matches['season']==i]\
            .groupby(['player_api_id']))
        df_altair1[str(i)] = count 
    
    chart1 = alt.Chart(df_altair1.T.reset_index()).mark_line().encode(
          alt.X('index:N',title="Año"),
          alt.Y('numero_jugadores:Q',title="Número de Jugadores" )
    ).properties(
        width=500)
    
    st.altair_chart(chart1)



with st.expander("Valor de mercado de futbolistas por jugadores y años en una selección de países..."):
    ### SEGUNDO GRÁFICO CON EL REPARTO DEL VALOR DE MERCADO DE LOS FUTBOLISTAS POR TEMPORADA Y POR NACIONALIDAD DEL FUTBOLISTA
    st.markdown(" ### REPARTO DEL VALOR DE MERCADO DE LOS FUTBOLISTAS POR TEMPORADA Y POR NACIONALIDAD DEL FUTBOLISTA ")
    df_altair2 = df_mkt_player_team_matches.loc[:,['player_name','player_nation', 'season', 'market_val_amnt']]
    df_altair2.drop_duplicates(inplace=True)
    df_altair2.dropna(axis=0, how='any', subset=['market_val_amnt'], inplace=True)
    df_altair2.sort_values(by=['season'])
    
    df_altair2['tooltip'] = df_altair2['player_name'] + ' from '+ df_altair2['player_nation'] \
        + ', Valor de mercado: ' + format_amount(df_altair2['market_val_amnt'])
    
    selected_nation_players= ["France", "Spain", "United States", "England", "Wales", "Argentina"," Germany", \
                              "Italy", "Poland","Brazil", "Croatia","Belgium", "Portugal", "Colombia", "Netherlands", \
                              "Gabon", "Algeria", "Austria", "Serbia", "Bosnia-Herzegovina", "Austria", "Uruguay", \
                              "Paraguay", "Nigeria", "Scotland", "Slovenia", "Morocco", "Mali"]
    
    chart2 = alt.Chart(df_altair2).transform_filter(
        filter={"field": 'player_nation',
                "oneOf": selected_nation_players}).mark_bar().encode(
          alt.X('season:N', title='Año'),
          alt.Y('market_val_amnt:Q', title='Valor de mercado acumulado desglosado por pais', scale=alt.Scale(domain = [0, 4e9])),
          color='player_nation',
          tooltip='tooltip:N',
    ).properties(
        width=800, height=650).interactive()
    
    st.altair_chart(chart2)
    
with st.expander("Valor de mercado a nivel mundial por años..."):
    ### TERCER GRÁFICO CON EL REPARTO DEL VALOR DE MERCADO DE LOS FUTBOLISTAS POR TEMPORADA Y POR NACIONALIDAD DEL FUTBOLISTA EN MAPA MUNDIAL
    st.markdown(" ## VALOR DE MERCADO DE LOS FUTBOLISTAS POR TEMPORADA Y POR NACIONALIDAD DEL FUTBOLISTA.  ")
    st.markdown(" ##### ( Los países no mostrados no tienen datos en ese año. ) ")
    map_geojson ={
    "Bosnia-Herzegovina":"Bosnia and Herzegovina",
    "Brunei Darussalam":"Brunei",
    "Chinese Taipei (Taiwan)": "Taiwan",
    "Congo": "Republic of Congo",
    "DR Congo": "Democratic Republic of the Congo",
    "Cote d'Ivoire": "Ivory Coast",
    "Curacao": "Curaçao",
    "England":"United Kingdom",  
    "Guinea-Bissau": "Guinea Bissau",
    "Hongkong": "Hong Kong S.A.R.",
    "Macao": "Macao S.A.R",
    "Neukaledonien": "New Caledonia",
    "North Macedonia": "Macedonia",
    "Northern Ireland": "United Kingdom",
    "Palästina": "Palestine",
    "Scotland":"United Kingdom", 
    "Serbia":"Republic of Serbia", 
    "St. Lucia": "Saint Lucia",
    "Tanzania": "United Republic of Tanzania",
    "The Gambia": "Gambia",
    "United States":"United States of America",
    "Wales":"United Kingdom"
    }
        
    df_altair_geonations_season = df_altair2.copy()
    player_nation_geo = df_altair_geonations_season['player_nation'].apply(mapping_player_nation_geo)
    df_altair_geonations_season.insert(2,'player_nation_geo', player_nation_geo)
    df_altair_geonations_season.drop('player_name', axis=1, inplace=True)
    df_altair_geonations_season.drop('player_nation', axis=1, inplace=True)
    df_altair_geonations_season.drop('tooltip', axis=1, inplace=True)
    
    df_altair_geonations_seasons = df_altair_geonations_season.groupby(['season', 'player_nation_geo']).sum('market_val_amnt')
    df_altair_geonations_seasons.reset_index(level=[0,1], inplace=True)
    
    df_altair_geonations_seasons['tooltip'] = df_altair_geonations_seasons['player_nation_geo'] + ', Valor de mercado: '+ \
         format_amount(df_altair_geonations_seasons['market_val_amnt']) + ' en el año ' + \
        df_altair_geonations_seasons['season'].astype('string')
    
    df_altair_geo_sea_dict = {} 
    for i in np.arange(2009,2022):
        df_altair_geo_sea_dict[str(i)] = df_altair_geonations_seasons.loc[df_altair_geonations_seasons['season']==i]
    
        
    countries_geojson = "https://raw.githubusercontent.com/openlayers/ol3/6838fdd4c94fe80f1a3c98ca92f84cf1454e232a/examples/data/geojson/countries.geojson"
    geodata = alt.Data(
      url=countries_geojson, format=alt.DataFormat(property="features", type="json")
    )
    
    year_filter = [str(i) for i in np.arange(2009,2022)]
    col1, col2, col3, col4 = st.columns(4)
    with col1:    
        year_selection = st.selectbox(label="Seleccione un año:", key="chloropleth", options=sorted(year_filter))
    with col2:        
        pass;
    with col3:        
        pass;
    with col4:        
        pass;
    
    
    click_country = alt.selection_point(fields=["player_nation_geo"])
    color_cond = alt.condition(
        click_country, 
        alt.Color('market_val_amnt:Q',
                  scale = alt.Scale(scheme="yelloworangebrown"),
                  legend=alt.Legend(orient="left", direction='vertical', 
                                                titleAnchor='middle',  title="Valor de mercado acumulado")),
        alt.value("lightgray")
        )
    
    chart3 = alt.Chart(geodata).mark_geoshape(
            stroke='white', strokeWidth=0.5
        ).transform_lookup(
                       lookup="properties.name",
                       from_=alt.LookupData(
                           data=df_altair_geo_sea_dict[year_selection],
                           key="player_nation_geo",
                           fields=["player_nation_geo", "season", "market_val_amnt", "tooltip"]
                       ),
        ).encode(
            color=color_cond,
            tooltip='tooltip:N'
        ).add_params(click_country).project(
            type='equalEarth', 
        ).properties(width=900,height=600).interactive()
    
    st.altair_chart(chart3)



with st.sidebar:
    choose = option_menu(        
        "Seleccione por posición del futbolista en el campo",
        ["Cualquiera", "Delanteros", "Defensas", "Porteros", "Centrocampistas"]
        )
        
age_domain = [15, 20, 25, 30, 35] 

with st.expander("Datos de rendimiento de futbolistas"):

    if choose == 'Cualquiera':
        st.markdown(" ### COMPARACIÓN RENDIMIENTO GENERAL ENTRE FUTBOLISTAS")
        st.markdown(" Ahora vamos a mostrar un gráfico de dispersión por cada año de entre los que tengamos suficientes datos.  En el Eje X se va a mostrar el rendimiento medio de un futbolista en un año, "\
                    "mientras que en el eje Y se mostrará el valor de mercado medio de ese futbolista en ese año")
        df_mkt_player_team_matches_attributes = pd.read_csv('df_mkt_player_team_matches_attributes.csv', header=0)
        
        df_altair3 = df_mkt_player_team_matches_attributes.loc[:,['player_name','season','season_player_age','team_long_name', \
                                                                      'market_val_amnt', 'overall_rating']]
        df_altair3.drop_duplicates(inplace=True)
        df_altair3.dropna(axis=0, how='any', inplace=True)
        
        df_altair3['tooltip'] = df_altair3['player_name'] + ' jugando en '+ df_altair3['team_long_name']
        df_altair3.info()
        
        print('\nMínimo overall rating: ',df_altair3['overall_rating'].min())
        print('Máximo overall rating: ',df_altair3['overall_rating'].max())
        print('\nMínimo market val.: ',df_altair3['market_val_amnt'].min())
        print('Máximo market val.: ',df_altair3['market_val_amnt'].max())
    
           
        sca_list = {}
        for i in np.arange(2009,2017):
            sca=alt.Chart(df_altair3).mark_point().encode(                  
                  alt.X('mean(overall_rating):Q', title="Rendimiento medio jugador en ese año", 
                        scale=alt.Scale(domain=[45,100])),
                  alt.Y('mean(market_val_amnt):Q', title="Valor de mercado", axis=alt.Axis(titleAngle=-65, titlePadding=35)),                  
                  tooltip='tooltip',
                  color=alt.Color('season_player_age:N', scale=alt.Scale(scheme='lightgreyred', reverse=True, type="bin-ordinal", domain=age_domain), 
                                  legend=alt.Legend(orient="top", direction='horizontal', 
                                                    titleAnchor='middle',  title="Edad del jugador"))
            ).transform_filter(
                'datum.season=='+str(i)
            ).properties(width=800, height=600 ).interactive()              
            
            sca_list[str(i)] = sca    
            
        col1, col2, col3 = st.columns(3)
        with col1:   
            year_filter2 = [str(i) for i in np.arange(2009,2017)] #Filtro de años
            year_selection2 = st.selectbox(label="Seleccione un año:", key="overall_rating", options=sorted(year_filter2))
        with col2:        
            pass;
        with col3:        
            pass;
        sca_list[str(year_selection2)]           
        
        
    if choose == 'Delanteros':
        st.markdown(" ### DELANTEROS Y GOLES")
        st.markdown("En el siguiente gráfico vamos a medir la capacidad goleadora de los delanteros, así que primero vamos a filtrar los jugadores cuya demarcación hace que se espere de ellos una cierta cantidad de goles")
        df_mkt_player_team_matches_goals = pd.read_csv('df_mkt_player_team_matches_goals.csv', header=0)
        df_altair4_only_attackers = df_mkt_player_team_matches_goals.loc[df_mkt_player_team_matches_goals['player_pos'].isin(['AM', 'LW', 'RW', 'CF', 'SS', 'attack'])]
        df_altair4 = df_altair4_only_attackers.loc[:,['player_api_id','player_name','season','season_player_age' \
                                                         ,'market_val_amnt']].sort_values(by=['season','player_api_id'])
        df_altair4.drop_duplicates(inplace=True)
        df_altair4.dropna(axis=0, how='any', inplace=True)
    
        season_goals = df_altair4_only_attackers.groupby(['season','player_api_id'])['id'].count()
        season_goals = season_goals.reset_index(level=[0,1])
        df_altair4 = pd.merge(df_altair4, season_goals, on=['player_api_id', 'season'])
        df_altair4.rename(columns={'id':'goals'}, inplace=True)
        df_altair4['tooltip'] = df_altair4['player_name'] +', '+  format_amount(df_altair4['goals']) +' goles\n'+'Valor de mercado: '\
                            +  format_amount(df_altair4['market_val_amnt'])
        
        sca_list_2 = {}
        for i in np.arange(2009,2017):
            scatter2=alt.Chart(df_altair4).mark_point().encode(
              alt.Y('mean(market_val_amnt):Q', title="Valor de mercado", axis=alt.Axis(titleAngle=-65, 
                                                            titlePadding=35, titleFontStyle="bold", )),
              alt.X('goals:Q', title="Goles jugador en ese año", sort='ascending',  
                    axis=alt.Axis(titlePadding=5)),
              tooltip='tooltip',
              color=alt.Color('season_player_age:N', scale=alt.Scale(scheme='lightgreyred', reverse=True, type="bin-ordinal", domain=age_domain), 
                                  legend=alt.Legend(orient="top", direction='horizontal', 
                                                    titleAnchor='middle',  title="Edad del delantero"))            ).transform_filter(
                'datum.season=='+str(i)
            ).properties(width=800, height=600).interactive()                        
            sca_list_2[str(i)] = scatter2    
            
        col1, col2, col3 = st.columns(3)
        with col1:
            year_filter3 = [str(i) for i in np.arange(2009,2016)] #Filtro de años
            year_selection3 = st.selectbox(label="Seleccione un año:", key="forwarders_goals", options=sorted(year_filter3))
        with col2:        
            pass;
        with col3:        
            pass;
        sca_list_2[str(year_selection3)]           
    
    if choose == 'Defensas':                        
        st.markdown(" ### DEFENSAS Y TARJETAS")    
        st.markdown("En el siguiente gráfico, vamos a medir cuantas tarjetas amarillas y rojas han recibido por temporada los defensas "\
                    "y por tanto, saber cual es el riesgo de que les expulsen por tarjeta roja.")
        df_mkt_player_team_matches_cards = pd.read_csv('df_mkt_player_team_matches_cards.csv', header=0)  
        df_altair5_only_defences = df_mkt_player_team_matches_cards.loc[df_mkt_player_team_matches_cards['player_pos'].isin(['RB', 'CB', 'LB', 'DM', 'defence'])]
        df_altair5 = df_altair5_only_defences.loc[:,['player_api_id','player_name','season','season_player_age' \
                                                         ,'market_val_amnt']].sort_values(by=['season','player_api_id'])
        df_altair5.drop_duplicates(inplace=True)
        df_altair5.dropna(axis=0, how='any', inplace=True)
    
        season_cards = df_altair5_only_defences.groupby(['season','player_api_id', 'card_type'])[['id']].count()
        season_cards = season_cards.reset_index(level=[0,1,2])
        df_altair5 = pd.merge(df_altair5, season_cards, on=['player_api_id', 'season'])
        df_altair5['card_type'].replace('y','Amarilla', inplace=True)
        df_altair5['card_type'].replace('y2','Roja', inplace=True)
        df_altair5['card_type'].replace('r','Roja', inplace=True)
        df_altair5.rename(columns={'id':'cards'}, inplace=True)
        df_altair5['tooltip'] = df_altair5['player_name'] +', '+  format_amount(df_altair5['cards']) +' tarjeta(s) ' \
            +df_altair5['card_type']
            
        sca_list_3 = {}    
        for i in np.arange(2009,2016):
            scatter3=alt.Chart(df_altair5).mark_square().encode(

                  alt.Y('mean(market_val_amnt):Q', title="Valor de mercado", axis=alt.Axis(titleAngle=-65, 
                                                                    titlePadding=35, titleFontStyle="bold")),
                  alt.X('cards:Q', title="Tarjetas jugador en ese año", sort='ascending', 
                        axis=alt.Axis(titlePadding=5)),          
                  tooltip='tooltip',
                  color=alt.Color('card_type:O', scale=alt.Scale(scheme='yelloworangered'), 
                                  legend=alt.Legend(orient="top", direction='horizontal', 
                                                    titleAnchor='middle',  title="Color Tarjeta"))
            ).transform_filter(
                'datum.season=='+str(i)
            ).properties(width=800, height=600).interactive()
                        
            scatter3.configure_point(
                    size=300,
                    color='lightyellow',
                    filled=False
                )   
    
            sca_list_3[str(i)] = scatter3
            
        col1, col2, col3 = st.columns(3)
        with col1:
            year_filter4 = [str(i) for i in np.arange(2009,2016)] #Filtro de años para este gráfico
            year_selection4 = st.selectbox(label="Seleccione un año:", key="defenders_cards", options=sorted(year_filter4))
        with col2:        
            pass;
        with col3:        
            pass;
        sca_list_3[str(year_selection4)]     
        
    if choose == 'Porteros':                        
        st.markdown(" ### PORTEROS")        
        st.markdown("En este gráfico, examinaremos distintas características de los porteros para tener un análisis completo "\
                    "en relación al precio de mercado")
        df_mkt_player_team_matches_attributes = pd.read_csv('df_mkt_player_team_matches_attributes.csv', header=0)    
        df_altair6_only_goalkeepers = df_mkt_player_team_matches_attributes.loc[df_mkt_player_team_matches_attributes['player_pos'] \
                                            .isin(['GK'])]
        df_altair6 = df_altair6_only_goalkeepers.loc[:,['player_name','season','season_player_age','team_long_name', \
            'market_val_amnt', 'overall_rating', 'gk_diving', 'gk_handling', 'gk_kicking', 'gk_positioning', 'gk_reflexes']]
        df_altair6.drop_duplicates(inplace=True)
        df_altair6.dropna(axis=0, how='any', inplace=True)

        df_altair6['tooltip'] = df_altair6['player_name'] + ' jugando en '+ df_altair6['team_long_name']
                
                
        sca_list_4 = {} 
        attribs_gk={"Lanzarse hacia el balón" : "gk_diving", 
                    "Juego con las manos" :"gk_handling", 
                    "Juego con los pies" : "gk_kicking", 
                    "Colocación" : "gk_positioning", 
                    "Reflejos" : "gk_reflexes",
                    "Valoración general": "overall_rating"}
        col1, col2, col3 = st.columns(3)
        with col1:
            year_filter5 = [str(i) for i in np.arange(2009,2016)] #Filtro de años para este gráfico
            year_selection5 = st.selectbox(label="Seleccione un año:", key="gk_attribs_years", 
                                           options=sorted(year_filter5))
        with col2:        
            gk_attrib_selection= st.selectbox(label="Seleccione un atributo medible del portero:", 
                                              key="attribs_gk", options=(attribs_gk))
        with col3:        
            pass;        
        for i in range(2009,2016):
            scatter4=alt.Chart(df_altair6).mark_point().encode(
                  alt.X(f"mean({attribs_gk[gk_attrib_selection]}):Q", title = gk_attrib_selection),
                  alt.Y('mean(market_val_amnt):Q', title="Valor de mercado", axis=alt.Axis(titleAngle=-65, titlePadding=35)),
                  tooltip='tooltip',                        
                  color=alt.Color('season_player_age:Q', scale=alt.Scale(scheme='lightgreyred', reverse=True, type="bin-ordinal", domain=age_domain),  
                                  legend=alt.Legend(orient="top", direction='horizontal', 
                                                    titleAnchor='middle',  title="Edad del portero"))
            ).transform_filter(
                'datum.season=='+str(i)
            ).properties( width=800, height=500 ).interactive()
            sca_list_4[str(i)] = scatter4
            
        sca_list_4[str(year_selection5)]         
        

    if choose == 'Centrocampistas':                        
        st.markdown(" ### CENTROCAMPISTAS")        
        st.markdown("En este último gráfico, examinaremos distintas características de los centrocampistas "\
                    "en relación al precio de mercado")
        df_mkt_player_team_matches_attributes = pd.read_csv('df_mkt_player_team_matches_attributes.csv', header=0)    
        df_altair7_only_midfielders = df_mkt_player_team_matches_attributes.loc[df_mkt_player_team_matches_attributes['player_pos'] \
                                            .isin(['DM', 'LM', 'RM', 'CM', 'midfield', 'AM'])]
        df_altair7 = df_altair7_only_midfielders.loc[:,['player_name','season','season_player_age','team_long_name', \
            'market_val_amnt', 'overall_rating', 'short_passing', 'long_passing', 'ball_control', 'stamina', 'positioning', 'vision']]
        df_altair7.drop_duplicates(inplace=True)
        df_altair7.dropna(axis=0, how='any', inplace=True)

        df_altair7['tooltip'] = df_altair7['player_name'] + ' jugando en '+ df_altair7['team_long_name']
                
        sca_list_5 = {}        
        attribs_mf={"Pase corto" :"short_passing", 
                    "Pase largo" : "long_passing", 
                    "Control de balón" : "ball_control", 
                    "Resistencia" : "stamina",
                    "Posicionamiento" : "positioning",
                    "Visión de juego" : "vision",
                    "Valoración general": "overall_rating"}
        col1, col2, col3 = st.columns(3)
        with col1:
            year_filter6 = [str(i) for i in np.arange(2009,2016)] #Filtro de años para este gráfico
            year_selection6 = st.selectbox(label="Seleccione un año:", key="mf_attribs_years", 
                                           options=sorted(year_filter6))
        with col2:        
            mf_attrib_selection= st.selectbox(label="Seleccione un atributo medible del centrocampista:", 
                                              key="attribs_mf", options=(attribs_mf))
        with col3:        
            pass;        
        for i in range(2009,2016):
            scatter5 = alt.Chart(df_altair7).mark_point().encode(
                  alt.X(f"mean({attribs_mf[mf_attrib_selection]}):Q", title = mf_attrib_selection),
                  alt.Y('mean(market_val_amnt):Q', title="Valor de mercado", axis=alt.Axis(titleAngle=-65, titlePadding=35)),
                  tooltip='tooltip',                        
                  color=alt.Color('season_player_age:Q', scale=alt.Scale(scheme='lightgreyred', reverse=True, type="bin-ordinal", domain=age_domain),  
                                  legend=alt.Legend(orient="top", direction='horizontal', 
                                                    titleAnchor='middle',  title="Edad del centrocampista"))
            ).transform_filter(
                'datum.season=='+str(i)
            ).properties( width=800, height=500 ).interactive()
            sca_list_5[str(i)] = scatter5
            
        sca_list_5[str(year_selection6)]                 