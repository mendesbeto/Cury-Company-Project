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

st.set_page_config(page_title='Visão Empresa', page_icon='', layout='wide')
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

def order_metric_by_day(df1):
                    #Selecionar colunas
                    cols = ['ID','Order_Date']
                    #Selecionar linhas
                    grafico = df1.loc[:,cols].groupby('Order_Date').count().reset_index()

                    #Desenhhar grafico de bara com plotly
                    fig = px.bar( grafico, x='Order_Date', y='ID')
                    return fig

def traffic_order_share(df1):
                        pizza = (df1
                                 .loc[:,['Road_traffic_density','ID']]
                                 .groupby('Road_traffic_density')
                                 .count().reset_index())
                        pizza['id_percent'] = pizza['ID']/pizza['ID'].sum()
                        fig = px.pie(pizza, values='id_percent', names='Road_traffic_density')
                        return fig

def traffic_order_city(df1):
                        bolha = (df1
                                 .loc[:,['City','Road_traffic_density','ID']]
                                 .groupby(['City','Road_traffic_density'])
                                 .count().reset_index())
                        fig = px.scatter(bolha,
                                         x='City',
                                         y='Road_traffic_density',
                                         size='ID',
                                         color='City')
                        return fig

def pedido_por_semana(df1):
                        df1['weak_of_year'] = df1['Order_Date'].dt.strftime('%U') # ou ('%W')
                        cols = ['ID','weak_of_year']

                        grafico = df1.loc[:,cols].groupby('weak_of_year').count().reset_index()

                        fig = px.line(grafico, x='weak_of_year', y='ID')

                        return fig

def distrib_por_trafigo(df1):
                        df2 = df1.loc[:,['weak_of_year','ID']].groupby('weak_of_year').count().reset_index()
                        df3 = df1.loc[:,['weak_of_year','Delivery_person_ID']].groupby('weak_of_year').nunique().reset_index()
                        
                        dfu = pd.merge(df2,df3, how='inner', on='weak_of_year')
                        dfu['order_by_delivery'] = dfu['ID'] / dfu['Delivery_person_ID']
                        fig = px.line(dfu, x='weak_of_year', y='order_by_delivery')
                        return fig

def entrega_por_regiao(df1):
        mapa = df1.loc[:, ['City', 'Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
        map = folium.Map()
        for index, location_info in mapa.iterrows():
            Marker([location_info['Delivery_location_latitude'],
                            location_info['Delivery_location_longitude']],
                            popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
            folium_static(map, width=1024, height=600)
        

# =========================== Inicio da estrutura dos codigos logicos ===========================

# Importação de arquivo
df = pd.read_csv('train.csv')

# Limpando arquivo
df1 = clean_code(df)


#==============================================
# Barra Lateral 
#==============================================
st.header('Marketplace - Visão da Empresa')

#image_path = 'Alvo.webp'
image = Image.open( 'Alvo.webp' )
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Faster Dejivery in Town')
st.sidebar.markdown('''___''')

st.sidebar.markdown('## Selecione uma das data limite')
data_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.to_datetime (2022, 4, 13),
    min_value=pd.to_datetime (2022, 2, 11),
    max_value=pd.to_datetime (2022, 4, 6),
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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográica'])

with tab1:
        with st.container():
                st.markdown('# Order Metric by Day')
                fig = order_metric_by_day(df1)
                st.plotly_chart(fig, use_container_width=True)
        
        with st.container():
              cols1, cols2 = st.columns(2)
              with cols1:
                    st.header('Traffic Order Share')
                    fig = traffic_order_share(df1)                        
                    st.plotly_chart(fig, use_container_width=True)
                    
              with cols2:
                    st.header('Trafic Order City')
                    fig = traffic_order_city(df1)
                    st.plotly_chart(fig, use_container_width=True)
             

with tab2:
    with st.container():
          # Criar coluna de senmans
            st.markdown('# Pedidos por Semana')
            fig=pedido_por_semana(df1)
            st.plotly_chart(fig, use_container_width=True)


    with st.container():
            st.markdown('# Distribuição por tipo de tráfego')
            fig = distrib_por_trafigo(df1)
            st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown('# Entregas por Regiões')
    entrega_por_regiao(df1)
    

st.markdown('''---''')
