import streamlit as st
from plotly import graph_objects as go
import requests
import pandas as pd
from plotly.subplots import make_subplots

# Una configuración básica de estética
st.set_page_config(layout='wide')


# Defino una función que me traiga los datos directamente desde la API del BCRA
def get_bcra_info(token, url):
    headers = {'Authorization': f'BEARER {token}'}
    # Realizamos consulta vía API al BCRA
    response = requests.get(url, headers=headers).json()
    df = pd.DataFrame(response)
    return df


# Agregamos un título y un subheader a la página
st.title('¿Inflación vs. USD?')
st.write("El siguiente gráfico muestra la inflación interanual, el valor del dólar oficial y del dólar blue en función del tiempo para Argentina desde el año 1995.")


# Agrego una entrada de texto para ingresar el token generado y lo almaceno en una variable
token = st.text_input('Token de BCRA')
# Ayuda complementaria al usuario
st.info('Para conseguir un token, registrate con tu mail en https://estadisticasbcra.com/api/registracion')
# Una vez ingresado el token, el usuario debe presionar este botón
calculate = st.button('Empezar')

if calculate:
    # Inflación interanual argentina
    yearly_inflation = get_bcra_info(token, 'https://api.estadisticasbcra.com/inflacion_interanual_oficial')
    yearly_inflation = yearly_inflation.rename(columns={'d': 'Período', 'v': 'Inflación interanual oficial'})
    yearly_inflation = yearly_inflation[yearly_inflation['Período'] >= '1995-01-01']

    # Cotización de dólar blue en función del tiempo
    usd_value = get_bcra_info(token, 'https://api.estadisticasbcra.com/usd')
    usd_value = usd_value.rename(columns={'d': 'Período', 'v': 'USD(t)'})
    usd_value = usd_value[usd_value['Período'] >= '1995-01-01']

    # Cotización de dólar oficial en función del tiempo
    usd_of_value = get_bcra_info(token, 'https://api.estadisticasbcra.com/usd_of')
    usd_of_value = usd_of_value.rename(columns={'d': 'Período', 'v': 'USD Oficial(t)'})
    usd_of_value = usd_of_value[usd_of_value['Período'] >= '1995-01-01']

    # Instanciamos una figura de plotly para empezar a graficar
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Añadimos el primer trazo: inflación mensual en función del tiempo
    fig.add_trace(
        go.Scatter(
            x=yearly_inflation['Período'],
            y=yearly_inflation['Inflación interanual oficial'],
            mode='lines',
            name='Inflación interanual oficial (%)'
        ),
        secondary_y=False
    )

    # Añadimos el segundo trazo: dólar oficial en función del tiempo
    fig.add_trace(
        go.Scatter(
            x=usd_of_value['Período'],
            y=usd_of_value['USD Oficial(t)'],
            mode='lines',
            name='USD Oficial ($)'
        ),
        secondary_y=True
    )

    # Añadimos el tercer trazo: dolar en función del tiempo
    fig.add_trace(
        go.Scatter(
            x=usd_value['Período'],
            y=usd_value['USD(t)'],
            mode='lines',
            name='USD ($)'
        ),
        secondary_y=True
    )

    # Definimos el título del eje X
    fig.update_xaxes(title_text="Período")

    # Definimos los títulos de los ejes Y
    fig.update_yaxes(title_text="Inflación interanual (%)", secondary_y=False)
    fig.update_yaxes(title_text="USD Oficial vs Blue ($)", secondary_y=True)


    st.plotly_chart(fig, use_container_width=True)

    st.info('Todos los datos fueron extraídos de https://estadisticasbcra.com/api/documentacion')