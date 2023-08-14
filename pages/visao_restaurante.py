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

# ============================================================
# Finções
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

def distance(df1):
                cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

                #haversine(('Restaurant_latitude', 'Restaurant_longitude'), ('Delivery_location_latitude', 'Delivery_location_longitude'))
                df1['distance'] = df1.loc[:,cols].apply( lambda x:
                                                haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),axis=1)
                distans = np.round(df1['distance'].mean(),2)
                return distans

def mean_time_std_time_delivery(df1, fetival, op):

                        '''
                                Esta funçaõa calcula o tempo medio e o desvio padrão de entrega
                                Parâmetros:
                                        Input:
                                                - df: Dataframe com os dados necessários para o calculo
                                                - po: Tipo de operação que precisa ser calculado
                                                        'std_time': calculo de desvio de padrão
                                                        'mean_time': calculo do tempo medio
                                        Output:
                                                - df: Dataframe com 2 colunas e 1 linha
                        '''
                        df1_temp = (df1.loc[:,['Festival','Time_taken(min)']]
                                .groupby('Festival')
                                .agg({'Time_taken(min)':['mean','std']}))
                        
                        df1_temp.columns = ['mean_time', 'std_time']
                        df1_temp = df1_temp.reset_index()

                        df1_temp = np.round(df1_temp.loc[df1_temp['Festival'] == fetival, op],2)
                        return df1_temp

def mean_time_std_time_graph(df1):
                        cols = ['City','Time_taken(min)']
                        df1_temp = df1.loc[:,cols].groupby('City').agg({'Time_taken(min)':['mean','std']})
                        df1_temp.columns = ['mean_time', 'std_time']                
                        df1_temp = df1_temp.reset_index()
                
                        fig = go.Figure()
                        fig.add_trace( go.Bar(name = 'Control',
                        x=df1_temp['City'],
                        y=df1_temp['mean_time'],
                        error_y=dict(type='data',
                                        array=df1_temp['std_time'])))
                        fig.update_layout( barmode='group')
                        return fig

def mean_time_std_time_distance(df1):
                        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
                        #haversine(('Restaurant_latitude', 'Restaurant_longitude'), ('Delivery_location_latitude', 'Delivery_location_longitude'))
                        df1['distance'] = df1.loc[:,cols].apply( lambda x:
                        haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                        (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),axis=1)
                
                        dist_media = df1.loc[:,['City','distance']].groupby('City').mean().reset_index()
                        fig = go.Figure(data=[go.Pie(labels=dist_media['City'],values=dist_media['distance'],pull=[0.01, 0.1, 0])])
                        fig.update_layout( barmode='group')
                        return fig

def mean_time_std_time_trafic(df1):
                cols = ['City','Road_traffic_density','Time_taken(min)']
                df1_temp = df1.loc[:,cols].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean','std']})
                df1_temp.columns = ['mean_time', 'std_time']
                df1_temp = df1_temp.reset_index()
                
                fig = px.sunburst(df1_temp, path=['City','Road_traffic_density'], values='mean_time',
                        color='std_time', color_continuous_scale='RdBu',
                        color_continuous_midpoint=np.average(df1_temp['std_time']))
                fig.update_layout( barmode='group')
                return fig



# =========================== Inicio da estrutura dos codigos logicos ===========================

# Importação de arquivo
df = pd.read_csv('train.csv')

# Limpando arquivo
df1 = clean_code(df)


#==============================================
# Barra Lateral 
#==============================================
st.header('Marketplace - Visão Restaurantes')

#image_path = 'alvo.webp'
image=Image.open('alvo.webp')
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
                st.title('Overal Matrics')
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                with col1:
                        entregadores = len(df1.loc[:,'Delivery_person_ID'].unique())
                        col1.metric('Entregadores únicos ', entregadores)

                with col2:
                        # Calcular distancia dos pedidos
                        distans = distance(df1)
                        col2.metric('distancia media dos campo ', distans)
            
                with col3:
                        df1_temp = mean_time_std_time_delivery(df1, fetival='Yes', op='mean_time')
                        col3.metric('Tempo medio c/festival', df1_temp)
                

                with col4:

                        df1_temp = mean_time_std_time_delivery(df1, fetival='Yes', op='std_time')
                        col4.metric('Tempo medio c/festival',df1_temp)
        
                with col5:
                        df1_temp = mean_time_std_time_delivery(df1, fetival='No', op='mean_time')
                        col5.metric('tmp medio s/festival',df1_temp)
            
                with col6:
                        df1_temp = mean_time_std_time_delivery(df1, fetival='No', op='std_time')
                        col6.metric('tmp d.padrao s/festival',df1_temp)
    
        with st.container():
                st.markdown('''---''')
                col1, col2 = st.columns(2)
                with col1:
                        st.markdown('Contener')
                        cols = ['City','Type_of_order','Time_taken(min)']
                        df1_temp = df1.loc[:,cols].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std']})
                        df1_temp.columns = ['mean_tima', 'std_time']
                        df1_temp = df1_temp.reset_index()
                        st.dataframe(df1_temp)

                with col2:
                        st.markdown('Tempo media das entregas por cidade')
                        fig = mean_time_std_time_graph(df1)
                        st.plotly_chart(fig)
        with st.container():
                st.markdown('''---''')
                col1, col2 = st.columns(2)
                with col1:
                        st.markdown('Tempo de entregas por Distância')
                        fig = fig=mean_time_std_time_distance(df1)
                        st.plotly_chart(fig)
                        
                with col2:
                        
                        st.markdown('Tempo de entregas por trfigo')
                        fig = mean_time_std_time_trafic(df1)
                        st.plotly_chart(fig)
                        
               

with tab2:
    st.markdown('')

with tab3:
    st.markdown('')

st.markdown('''---''')