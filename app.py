
# =====================================================
# DASHBOARD DE USUARIOS, PUBLICACIONES Y COMENTARIOS
# Proyecto del Diplomado de Python
# =====================================================

# 1. IMPORTAR LAS LIBRERÍAS
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
# CONFIGURACIÓN VISUAL DEL DASHBOARD

st.set_page_config(
    page_title="Dashboard de Usuarios",
    page_icon="📊",
    layout="wide"
)

# Estilos personalizados
st.markdown("""
    <style>
    .stApp {
        background-color: #F0F5FA;
    }

    h1 {
        color: #075985;
        text-align: center;
    }

    h2, h3 {
        color: #0878B8;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #D6E6F2;
    }
    </style>
""", unsafe_allow_html=True)

# 2. CONFIGURAR LA PÁGINA
st.set_page_config(
    page_title="Dashboard de Usuarios",
    page_icon="📊",
    layout="wide"
)

# 3. DIRECCIONES DE LAS TRES API
API_USUARIOS = "https://jsonplaceholder.typicode.com/users"
API_PUBLICACIONES = "https://jsonplaceholder.typicode.com/posts"
API_COMENTARIOS = "https://jsonplaceholder.typicode.com/comments"

# 4. FUNCIÓN PARA DESCARGAR Y PROCESAR LOS DATOS
@st.cache_data(ttl=600)
def cargar_datos():

    # Descargar usuarios
    respuesta_usuarios = requests.get(API_USUARIOS, timeout=20)
    respuesta_usuarios.raise_for_status()
    usuarios = pd.DataFrame(respuesta_usuarios.json())

    # Descargar publicaciones
    respuesta_publicaciones = requests.get(API_PUBLICACIONES, timeout=20)
    respuesta_publicaciones.raise_for_status()
    publicaciones = pd.DataFrame(respuesta_publicaciones.json())

    # Descargar comentarios
    respuesta_comentarios = requests.get(API_COMENTARIOS, timeout=20)
    respuesta_comentarios.raise_for_status()
    comentarios = pd.DataFrame(respuesta_comentarios.json())

    # Seleccionar y limpiar las columnas de usuarios
    usuarios = usuarios[
        ["id", "name", "username", "email", "address", "company"]
    ].copy()

    # Extraer ciudad y empresa
    usuarios["ciudad"] = usuarios["address"].apply(
        lambda x: x["city"]
    )

    usuarios["empresa"] = usuarios["company"].apply(
        lambda x: x["name"]
    )

    # Eliminar las columnas anidadas que ya no necesitamos
    usuarios = usuarios.drop(columns=["address", "company"])

    # Relacionar publicaciones con usuarios mediante userId
    publicaciones_usuarios = publicaciones.merge(
        usuarios,
        left_on="userId",
        right_on="id",
        how="left"
    )

    # Relacionar comentarios con publicaciones mediante postId
    datos_completos = comentarios.merge(
        publicaciones_usuarios,
        left_on="postId",
        right_on="id_x",
        how="left"
    )

    return usuarios, publicaciones, comentarios, datos_completos

# 5. TÍTULO DEL DASHBOARD
st.title("📊 Dashboard de Usuarios, Publicaciones y Comentarios")

st.write(
    "Sistema de análisis de información utilizando "
    "las API públicas de JSONPlaceholder."
)

#
# 6. CARGAR LOS DATOS Y CONTROLAR POSIBLES ERRORES
try:

    # Descargar y organizar los datos de las tres API
    usuarios, publicaciones, comentarios, datos = cargar_datos()

    st.success("¡Los datos se descargaron correctamente!")

    # Mostrar el resumen de los datos
    st.subheader("Resumen de los datos")

    # Crear cuatro columnas para los indicadores
    col1, col2, col3, col4 = st.columns(4)

    # Calcular el promedio de comentarios por publicación
    promedio = len(comentarios) / len(publicaciones)

    # Mostrar los cuatro indicadores
    col1.metric("Total de usuarios", len(usuarios))
    col2.metric("Total de publicaciones", len(publicaciones))
    col3.metric("Total de comentarios", len(comentarios))
    col4.metric("Promedio de comentarios", round(promedio, 2))

    # Mostrar una vista previa de los usuarios
    st.subheader("Listado de usuarios")
    st.dataframe(usuarios, width="stretch")

    # Mostrar una vista previa de las publicaciones
    st.subheader("Listado de publicaciones")
    st.dataframe(publicaciones.head(10), width="stretch")

    # Mostrar una vista previa de los comentarios
    st.subheader("Listado de comentarios")
    st.dataframe(comentarios.head(10), width="stretch")
    
        # 7. GRÁFICO DE PUBLICACIONES POR USUARIO

    st.subheader("📊 Publicaciones por usuario")

    # Agrupar las publicaciones según el ID del usuario
    publicaciones_usuario = publicaciones.groupby("userId").size()

    # Crear el gráfico de barras
    st.bar_chart(publicaciones_usuario)
        # 8. GRÁFICO DE COMENTARIOS POR PUBLICACIÓN

    st.subheader("💬 Comentarios por publicación")

    # Agrupar los comentarios por el ID de la publicación
    comentarios_publicacion = comentarios.groupby("postId").size()

    # Mostrar el gráfico de barras
    st.bar_chart(comentarios_publicacion)

    # 9. RELACIONAR USUARIOS, PUBLICACIONES Y COMENTARIOS

    st.subheader("🔗 Relación de usuarios, publicaciones y comentarios")

    # Seleccionar los datos necesarios de los usuarios
    usuarios_seleccionados = usuarios[["id", "name"]].rename(
        columns={
            "id": "userId",
            "name": "nombre_usuario"
        }
    )

    # Contar cuántos comentarios tiene cada publicación
    total_comentarios = comentarios.groupby("postId").size().reset_index(
        name="cantidad_comentarios"
    )

    # Unir las publicaciones con los usuarios
    datos_relacionados = publicaciones.merge(
        usuarios_seleccionados,
        on="userId",
        how="left"
    )

    # Unir el resultado con el total de comentarios
    datos_relacionados = datos_relacionados.merge(
        total_comentarios,
        left_on="id",
        right_on="postId",
        how="left"
    )

    # Mostrar la tabla relacionada
    st.write("Información unificada de las tres API")

    st.dataframe(datos_relacionados, width="stretch")


    # 10. FILTRO INTERACTIVO POR USUARIO

    st.subheader("🔎 Filtrar publicaciones por usuario")

    # Crear una lista desplegable con los nombres de los usuarios
    usuario_seleccionado = st.selectbox(
        "Selecciona un usuario:",
        datos_relacionados["nombre_usuario"].dropna().unique()
    )

    # Filtrar las publicaciones del usuario seleccionado
    datos_filtrados = datos_relacionados[
        datos_relacionados["nombre_usuario"] == usuario_seleccionado
    ]

    # Mostrar solamente las publicaciones seleccionadas
    st.write(f"Publicaciones de: {usuario_seleccionado}")

    st.dataframe(
        datos_filtrados[
            ["nombre_usuario", "title", "cantidad_comentarios"]
        ],
        width="stretch"
    )
    
    # 11. RANKING DE USUARIOS POR COMENTARIOS

    st.subheader("🏆 Usuarios con más comentarios")

    # Agrupar los comentarios recibidos por cada usuario
    ranking_usuarios = datos_relacionados.groupby(
        "nombre_usuario"
    )["cantidad_comentarios"].sum()

    # Ordenar de mayor a menor
    ranking_usuarios = ranking_usuarios.sort_values(
        ascending=False
    )

    # Mostrar los 10 usuarios principales
    st.bar_chart(ranking_usuarios.head(10))
    
    # 12. GRÁFICO CIRCULAR DE PUBLICACIONES POR USUARIO

    st.subheader("🥧 Distribución de publicaciones por usuario")

    # Contar las publicaciones de cada usuario
    publicaciones_por_usuario = publicaciones.groupby("userId").size()

    # Crear el gráfico circular
    import plotly.express as px

    grafico_pastel = px.pie(
        values=publicaciones_por_usuario.values,
        names=publicaciones_por_usuario.index,
        title="Porcentaje de publicaciones por usuario"
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(grafico_pastel, width="stretch")

        # 10.1. FILTROS POR CIUDAD Y EMPRESA

    st.subheader("🌎 Filtrar usuarios por ciudad y empresa")

    # Crear una lista de ciudades disponibles
    ciudades = ["Todas"] + sorted(usuarios["ciudad"].unique())

    # Crear una lista de empresas disponibles
    empresas = ["Todas"] + sorted(usuarios["empresa"].unique())

    # Crear dos columnas para los filtros
    col1, col2 = st.columns(2)

    # Filtro por ciudad
    with col1:
        ciudad_seleccionada = st.selectbox(
            "Selecciona una ciudad:",
            ciudades
        )

    # Filtro por empresa
    with col2:
        empresa_seleccionada = st.selectbox(
            "Selecciona una empresa:",
            empresas
        )

    # Aplicar los filtros seleccionados
    usuarios_filtrados = usuarios.copy()

    if ciudad_seleccionada != "Todas":
        usuarios_filtrados = usuarios_filtrados[
            usuarios_filtrados["ciudad"] == ciudad_seleccionada
        ]

    if empresa_seleccionada != "Todas":
        usuarios_filtrados = usuarios_filtrados[
            usuarios_filtrados["empresa"] == empresa_seleccionada
        ]

    # Mostrar los resultados
    st.write("Usuarios encontrados:", len(usuarios_filtrados))
    st.dataframe(usuarios_filtrados, width="stretch")


    # 10.1. FILTROS POR CIUDAD Y EMPRESA

    st.subheader("🌎 Filtrar usuarios por ciudad y empresa")

    # Obtener las ciudades disponibles
    ciudades = ["Todas"] + sorted(usuarios["ciudad"].unique())

    # Obtener las empresas disponibles
    empresas = ["Todas"] + sorted(usuarios["empresa"].unique())

    # Crear dos columnas para los filtros
    col1, col2 = st.columns(2)

    # Filtro por ciudad
    with col1:
        ciudad_seleccionada = st.selectbox(
            "Selecciona una ciudad:",
            ciudades,
            key="filtro_ciudad"
        )

    # Filtro por empresa
    with col2:
        empresa_seleccionada = st.selectbox(
            "Selecciona una empresa:",
            empresas,
            key="filtro_empresa"
        )

    # Copiar la tabla original de usuarios
    usuarios_filtrados = usuarios.copy()

    # Aplicar el filtro de ciudad
    if ciudad_seleccionada != "Todas":
        usuarios_filtrados = usuarios_filtrados[
            usuarios_filtrados["ciudad"] == ciudad_seleccionada
        ]

    # Aplicar el filtro de empresa
    if empresa_seleccionada != "Todas":
        usuarios_filtrados = usuarios_filtrados[
            usuarios_filtrados["empresa"] == empresa_seleccionada
        ]

    # Mostrar los resultados
    st.write("Usuarios encontrados:", len(usuarios_filtrados))
    st.dataframe(usuarios_filtrados, width="stretch")


        
        
    # 13. GRÁFICO DE DISPERSIÓN


    st.subheader("📈 Relación entre publicaciones y comentarios")

    # Contar publicaciones por usuario
    publicaciones_usuario = publicaciones.groupby("userId").size()

    # Contar comentarios por usuario
    comentarios_usuario = datos_relacionados.groupby(
        "userId"
    )["cantidad_comentarios"].sum()

    # Crear una tabla con ambas cantidades
    datos_dispersion = publicaciones_usuario.to_frame(
        name="total_publicaciones"
    )

    datos_dispersion["total_comentarios"] = comentarios_usuario

    # Crear el gráfico de dispersión
    grafico_dispersion = px.scatter(
        datos_dispersion,
        x="total_publicaciones",
        y="total_comentarios",
        title="Publicaciones y comentarios por usuario",
        labels={
            "total_publicaciones": "Total de publicaciones",
            "total_comentarios": "Total de comentarios"
        }
    )

    # Mostrar el gráfico
    st.plotly_chart(
        grafico_dispersion,
        width="stretch",
        key="grafico_dispersion_usuarios"
    )
    
        # 14. TABLA DINÁMICA POR USUARIO

    st.subheader("📋 Resumen dinámico por usuario")

    # Agrupar publicaciones y comentarios por usuario
    tabla_dinamica = datos_relacionados.pivot_table(
        index="nombre_usuario",
        values="cantidad_comentarios",
        aggfunc="sum"
    )

    # Mostrar la tabla dinámica
    st.dataframe(tabla_dinamica, width="stretch")

        # 15. EXPORTAR DATOS A EXCEL Y CSV

    st.subheader("📥 Descargar información")

    # Crear el archivo CSV
    archivo_csv = datos_relacionados.to_csv(
        index=False
    ).encode("utf-8-sig")

    # Crear el archivo Excel en memoria
    import io

    archivo_excel = io.BytesIO()

    with pd.ExcelWriter(archivo_excel, engine="openpyxl") as writer:
        datos_relacionados.to_excel(
            writer,
            index=False,
            sheet_name="Datos"
        )

    # Crear dos columnas para las descargas
    col1, col2 = st.columns(2)

    # Botón para descargar CSV
    with col1:
        st.download_button(
            label="📄 Descargar CSV",
            data=archivo_csv,
            file_name="datos_usuarios.csv",
            mime="text/csv",
            key="descargar_csv"
        )

    # Botón para descargar Excel
    with col2:
        st.download_button(
            label="📊 Descargar Excel",
            data=archivo_excel.getvalue(),
            file_name="datos_usuarios.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="descargar_excel"
        )
    
except requests.exceptions.RequestException as error:

    # Mostrar errores de conexión con las API
    st.error(f"Error al conectar con las API: {error}")

    

except Exception as error:

    # Mostrar cualquier otro error del programa
    st.error(f"Se produjo un error al procesar los datos: {error}")
