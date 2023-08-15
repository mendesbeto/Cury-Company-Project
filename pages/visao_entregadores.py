from datetime import datetime
import pandas as pd
import numpy as np
from folium import Marker, folium
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image

st.set_page_config(page_title='Visão Entregadores', page_icon='', layout='wide')

# ============================================================
# Funções
# ============================================================
def clean_code(df1):
    ''' Essa função tem a responsabilidade de limpar dataframe
        Tipos de lipeza:
        1. Remoção dos 'NaN'
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variaveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo( remoção do texto da variavel numerica )

        imput: datarame
        output: dataframe   
    
    '''
    # limpesa de espaços em branco
    df1['ID'] = df1['ID'].str.strip()
    df1['Delivery_person_ID'] = df1['Delivery_person_ID'].str.strip()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].str.strip()
    df1['Time_Orderd'] = df1['Time_Orderd'].str.strip()
    df1['Road_traffic_density'] = df1['Road_traffic_density'].str.strip()
    df1['Type_of_order'] = df1['Type_of_order'].str.strip()
    df1['Type_of_vehicle'] = df1['Type_of_vehicle'].str.strip()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].str.strip()
    df1['Festival'] = df1['Festival'].str.strip()
    df1['City'] = df1['City'].str.strip()
    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.strip()

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min)')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    # Remover linhas com "NaN"
    linhas = ((df1['Delivery_person_Age'] != 'NaN')
            & (df1['Time_Orderd'] != 'NaN')
            & (df1['multiple_deliveries'] != 'NaN')
            & (df1['City'] != 'NaN')
            & (df1['Festival'] != 'NaN'))
    df1 = df1.loc[linhas,:].copy()

    # converter propriedades das colunas
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'],format='%d-%m-%Y')
    df1['Time_Orderd'] = pd.to_datetime(df1['Time_Orderd'],format='%H:%M:%S')
    df1['Time_Order_picked'] = pd.to_datetime(df1['Time_Order_picked'],format='%H:%M:%S')
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    return df1

def media_por_transito(df1):
                df_trafic = (df1
                             .loc[:,['Road_traffic_density','Delivery_person_Ratings']]
                             .groupby('Road_traffic_density')
                             .agg({'Delivery_person_Ratings':['mean','std']}))
                
                df_trafic.columns = ['delivery_mean','delivery_std']
                df3 = df_trafic.reset_index()
                
                return df3

def media_por_clima(df1):
                df_trafic = (df1
                             .loc[:,['Weatherconditions','Delivery_person_Ratings']]
                             .groupby('Weatherconditions')
                             .agg({'Delivery_person_Ratings':['mean','std']}))
                
                df_trafic.columns = ['Weather_mean','Weather_std']
                df4 = df_trafic.reset_index()

                return df4


def top_delivery(df1, top_asc):
                rapido = (df1
                          .loc[:,['City','Delivery_person_ID','Time_taken(min)']]
                          .groupby(['City','Delivery_person_ID']).mean()
                          .sort_values(['City','Time_taken(min)'], ascending=top_asc).reset_index())
                
                Urban = rapido.loc[rapido['City']=='Urban',:].head(10)
                Metropolitian = rapido.loc[rapido['City']=='Metropolitian',:].head(10)
                Semi_Urban = rapido.loc[rapido['City']=='Semi-Urban',:].head(10)

                df3 = pd.concat([Metropolitian,Urban,Semi_Urban]).reset_index(drop=True)
                
                return df3




# =========================== Inicio da estrutura dos codigos logicos ===========================

# Importação de arquivo
df = pd.read_csv('train.csv')

# Limpando arquivo
df1 = clean_code(df)


#==============================================
# Barra Lateral 
#==============================================
st.header('Marketplace - Visão Entreggadores')

#image_path = 'alvo.webp'
image = Image.open( 'Alvo.webp' )
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Faster Dejivery in Town')
st.sidebar.markdown('''___''')

st.sidebar.markdown('## Selecione uma das data limite')
data_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime (2022, 4, 13),
    min_value=datetime (2022, 2, 11),
    max_value=datetime (2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect(
    'Quais condições do transito?',
    ['low', 'Medium', 'High', 'Jam'],
    default=['low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Comunidade DS')

linha_selecionada = df1['Order_Date'] < data_slider
df1 = df1.loc[linha_selecionada,:]

# Filtro de Trafico
linha_selecionada = df1['Road_traffic_density'].isin( traffic_options)
df1 = df1.loc[linha_selecionada,:]

#==============================================
# Layout no Streamlit
#==============================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão ...'])

with tab1:
    with st.container():
        st.title( 'Overall Metrics')
        col1, col2, col3, col4 = st.columns( 4, gap='large')
        with col1:
            #st.title( 'Maior idade')
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
        
        with col2:
            #st.title( 'Menor idade')
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
        with col3:
            #st.title( 'Melhor veiculo')
            melhor_veiculo = df1.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor Veículo', melhor_veiculo)

        with col4:
            #st.title( 'Pior veiculo')
            pior_veiculo = df1.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior Veículo', pior_veiculo)

    with st.container():
        st.markdown('''---''')
        st.title('Avaliações')

        col1, col2 = st.columns( 2, gap='large')
        with col1:
            st.markdown('##### Avaliação medias por entregador')

            df_avg_entr = (df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']]
                                .groupby('Delivery_person_ID')
                                .mean().reset_index())
            st.dataframe(df_avg_entr)
        with col2:
            st.markdown('##### Avaliação media por transito')
            df3 = media_por_transito(df1)
            st.dataframe(df3)
                
            st.markdown('##### Avaliação media por clima')
            df4 = media_por_clima(df1)
            st.dataframe(df4)

    with st.container():
        st.markdown('''---''')
        st.title('Velocidade de Entrega')

        col1, col2 = st.columns( 2, gap='large')
        with col1:
            st.markdown('##### Top Entregadores maio rapidos')
            df3 = top_delivery(df1, top_asc=True)
            st.dataframe(df3)

        with col2:
            st.markdown('##### Top Entregadres mais lentos')
            df3 = top_delivery(df1, top_asc=False)
            st.dataframe(df3)
st.markdown('''---''')
st.markdown('Comunidade - DS')
st.markdown('2013')
