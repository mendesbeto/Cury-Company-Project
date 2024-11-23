!pip install streamlit
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon=''
)

#image_path = "/Users/Windows10/Documents/repos/ftc_programacao_python/,"
image = Image.open('Alvo.webp')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Faster Dejivery in Town')
st.sidebar.markdown('''___''')

st.write('# Cury Company Growth Dashboard')

st.markdown(
    '''
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Time de Data Science no Discord
        - @bemfamily
    '''
)
