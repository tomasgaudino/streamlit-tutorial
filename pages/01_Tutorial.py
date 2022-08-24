import streamlit as st

st.title('Caso práctico: Inflación y dólar')

st.write('En este ejercicio vamos a aprender a combinar las herramientas de visualización que nos ofrece Plotly con el poderoso motor de renderización web Streamlit. El primer paso es importar las librerías que vamos a utilizar:')

st.code("""# Primero lo primero: importar streamlit y graph objects de plotly
import streamlit as st
from plotly import graph_objects as go
# Requests es una librería que sirve para traer información de APIs
import requests
# Pandas es tu mejor amigo a la hora de manipular datos, ¿ya lo conocías?
import pandas as pd
# Make_subplots nos permite ubicar en el mismo gráfico varios trazos y diferentes ejes
from plotly.subplots import make_subplots""")

st.info('Con todos los elementos necesarios importados, ya podemos empezar a codear!')
st.write('Primero, seteamos una variable global que ajusta el ancho de los objetos al de la pantalla.')
st.code("""# Una configuración básica de estética
st.set_page_config(layout='wide')
""")

st.write('El siguiente paso es armar una función genérica que nos permita interactuar con la API del BCRA.')
st.code("""def get_bcra_info(token, url):
    headers = {'Authorization': f'BEARER {token}'}
    # Realizamos consulta vía API al BCRA
    response = requests.get(url, headers=headers).json()
    df = pd.DataFrame(response)
    return df
""")

st.write('Es importante que nuestro dashboard tenga un título y una breve descripción para orientar a la audiencia. Para esto utilizamos las funciones st.title, st.subheader y st.info')
st.code("""# Agregamos un título y un subheader a la página
st.title('¿Inflación vs. USD?')
st.write("El siguiente gráfico muestra la inflación interanual, el valor del dólar oficial y del dólar blue en función del tiempo para Argentina desde el año 1995.")
st.info('Todos los datos fueron extraídos de https://estadisticasbcra.com/api/documentacion')
""")

st.write('Como los datos dependen de la API del BCRA y el mismo exige un token, para no difundir el mío los invito a que generen su propio token y obtengan la información ustedes mismos.')
st.code("""# Agrego una entrada de texto para ingresar el token generado y lo almaceno en una variable
token = st.text_input('Token de BCRA')
# Ayuda complementaria al usuario
st.info('Para conseguir un token, registrate con tu mail en https://estadisticasbcra.com/api/registracion')
# Una vez ingresado el token, el usuario debe presionar este botón
calculate = st.button('Empezar')""")

st.write('Ahora viene la parte interesante. Vamos a generar tres tablas a partir de la API del BCRA: inflación interanual argentina, cotización del dólar oficial y cotización del dólar blue. Se aplican dos transformaciones muy básicas, 1) se renombran las columnas para mejorar la legibilidad, y 2) se filtra para un período posterior a 1995.')
st.code("""if calculate:
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
""")

st.write('Vamos a graficar. En primer lugar, instanciamos una figura de plotly. Existen varios métodos, el que se muestra a continuación es make_subplots, una clase que nos permite ubicar un eje Y a la izquierda y a la derecha.')
st.code("""# Instanciamos una figura de plotly para empezar a graficar
fig = make_subplots(specs=[[{"secondary_y": True}]])
""")

st.write('Ya con el objeto de figura definido podemos empezar a añadir trazos de interés a nuestro gráfico. Nuestro objetivo es mostrar la inflación interanual porcentual en el eje Y izquierdo (que va de 0 a 100) y la cotización del dólar oficial y blue en el eje Y derecho. Se utilizan dos ejes diferentes para evitar problemas de escala')
st.code("""# Añadimos el primer trazo: inflación mensual en función del tiempo
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
)""")

st.write('Ya con los trazos definidos, restan algunas configuraciones protocolares como definir los títulos de los ejes:')
st.code("""# Definimos el título del eje X
fig.update_xaxes(title_text="Período")

# Definimos los títulos de los ejes Y
fig.update_yaxes(title_text="Inflación interanual (%)", secondary_y=False)
fig.update_yaxes(title_text="USD Oficial vs Blue ($)", secondary_y=True)
""")

st.write('Por último, tenemos que decirle a streamlit que acabamos de armar un hermoso gráfico de plotly y que queremos mostrarlo al usuario. En este ejemplo, la función st.plotly_chart() tiene definidos dos parámetros: la figura objeto que acabamos de definir y use_container_width, que ajusta el ancho de la figura al del container.')
st.code("st.plotly_chart(fig, use_container_width=True)")

st.subheader('¿Esto es todo?')
st.write("""¡No! Hubo muchísimas cosas que no pudimos ver por cuestiones de tiempo. Entre ellas:

- Métricas y columnas
- Filtros
    - Text inputs
    - Date pickers
    - Dropdowns
    - Radios
- Drag and drop
- Embedding
- Logins""")
