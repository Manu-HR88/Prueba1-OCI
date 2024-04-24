import streamlit as st
import pandas as pd
import base64
import io
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# En esta página se pretende analizar los resultados del concurso Olimpiada de Conocimiento Infantil 2024. 
# Aquí se analizarán no solo los ganadores sino que la Zona Escolar podrá ingresar los archivos de los resultados de sus escuelas 
# y con ello analizar y proponer un plan de intervención para estos alumnos de sexto.

# Agrega un texto semi-transparente como marca de agua
st.markdown(
    """
    <style>
        .watermark {
            position: fixed;
            top: 50%;
            left: 40%;
            transform: translate(-50%, -50%);
            color: #E4E4E4;
            font-size: 80px;
            transform: rotate(-45deg);
        }
    </style>
    <div class="watermark">Versión de Prueba</div>
    """,
    unsafe_allow_html=True
)


st.image('Logo_SATC_fondo.png', use_column_width=True)

#-------------------------------------- Inicio segmento para cargar los archivos ------------------------------------------------


# Permitir al usuario elegir la cantidad de archivos a subir
numero_archivos = st.number_input("¿Cuántos archivos desea cargar? (Máximo 20)", min_value=1, max_value=20, step=1)

# Lista para almacenar los datos y reactivos de cada archivo
# datos_list = []
# reactivos_list = []

# # Subir archivos y extraer las hojas "Datos" y "Reactivos" de cada archivo
# for i in range(numero_archivos):
#     archivo_excel = st.file_uploader(f"Subir archivo {i+1}", type=["xlsm", "xlsx"])
#     if archivo_excel is not None:
#         # Leer el archivo Excel y extraer la hoja "Datos"
#         datos_df = pd.read_excel(archivo_excel, sheet_name="Datos", header=2)
#         datos_list.append(datos_df)

#         # Leer el archivo Excel y extraer la hoja "Reactivos"
#         reactivos_df = pd.read_excel(archivo_excel, sheet_name="Reactivos", header=1, usecols="A:B")
#         reactivos_list.append(reactivos_df)

# st.write(datos_list) #Control para mostrar que se cargó la información
# st.write(reactivos_list) #Control para mostrar que se cargó la información

#---------------------------------------- Fin segmento para cargar los archivos ------------------------------------------------
        

#---------------------------------------Inicio prueba para calificar todo de una vez --------------------------------------------    

# Esta prueba tiene la intención de probar si se puede caificr el DF y obtener los datos de múltiples archivos, esto permitirá
# que la ZOna o la DEP analice los archivos de sus escuelas completos, no sólo de los ganadores.
# Se utilizaría la misma manera de carga inicial a través de barra para seleccionar el número de archivos a subir o cargar.
@st.cache_data
def calificar_respuesta(respuesta_alumno, respuesta_correcta):
    if respuesta_alumno == respuesta_correcta:
        return 1
    else:
        return 0

df_resultados_total = pd.DataFrame()        

for i in range(numero_archivos):
    archivo_excel = st.file_uploader(f"Subir archivo {i+1}", type=["xlsm", "xlsx"])
    if archivo_excel is not None:
        df_alumnos = pd.read_excel(archivo_excel, sheet_name="Datos", header=2)
        df_respuestas = pd.read_excel(archivo_excel, sheet_name="Reactivos", header=1, usecols="A:E")
        df_alumnos["Nombre del Alumno"] =  df_alumnos["Apellido Paterno del Alumno"] + " " + df_alumnos["Apellido Materno del Alumno"] + " " +  df_alumnos["Nombre (s) del Alumno"]
        df_alumnos.drop(columns=["Nombre (s) del Alumno", "Apellido Paterno del Alumno", "Apellido Materno del Alumno"], inplace=True)
        column_order = ["Folio", "Nombre del Alumno", "CCT"]
        # Reordenar las columnas manteniendo todas las columnas restantes
        column_order = ["Folio", "Nombre del Alumno", "CCT"] + [col for col in df_alumnos.columns if col not in ["Folio", "Nombre del Alumno", "CCT"]]
        df_alumnos = df_alumnos[column_order]
        df_calificaciones = df_alumnos.copy()  # Creamos una copia del DataFrame de alumnos para conservarlo intacto
        for pregunta in df_respuestas['Reactivo']:
            df_temp = pd.merge(df_alumnos[['Nombre del Alumno', pregunta]], df_respuestas[df_respuestas['Reactivo'] == pregunta], left_on=pregunta, right_on='Correcta', how='left')
            df_temp['P' + str(pregunta)] = df_temp.apply(lambda row: calificar_respuesta(row[pregunta], row['Correcta']), axis=1)
            df_calificaciones = pd.merge(df_calificaciones, df_temp[['Nombre del Alumno', 'P' + str(pregunta)]], on='Nombre del Alumno')
        df_resultados = df_calificaciones.copy()
        df_resultados = df_resultados.drop(range(1,61), axis = 1)
        cols_aciertos_totales = ['P' + str(i) for i in range(1, 61)]
        cols_aciertos_lenguajes = ['P' + str(i) for i in range(1, 21)]
        cols_aciertos_saberes = ['P' + str(i) for i in range(21, 41)]
        cols_aciertos_etica = ['P' + str(i) for i in range(41, 56)]
        cols_aciertos_humano = ['P' + str(i) for i in range(56, 61)]
        df_resultados['Total Aciertos'] = df_resultados[cols_aciertos_totales].sum(axis=1)
        df_resultados['Aciertos Lenguajes'] = df_resultados[cols_aciertos_lenguajes].sum(axis=1)
        df_resultados['Aciertos Saberes y P. Científico'] = df_resultados[cols_aciertos_saberes].sum(axis=1)
        df_resultados['Aciertos Ética, Nat y Sociedades'] = df_resultados[cols_aciertos_etica].sum(axis=1)
        df_resultados['Aciertos De lo Humano y lo Comunitario'] = df_resultados[cols_aciertos_humano].sum(axis=1)
        df_resultados_total = pd.concat([df_resultados_total, df_resultados])

#Elimiamos columnas de calificació para quedarnos con los resultados.
cols_eliminar = df_resultados_total.filter(regex='^P[1-9]|[1-5][0-9]|60$', axis=1) #columnas que coinciden con el patrón 'P' seguido de un número del 1 al 60 para la eliminación
if not df_resultados_total.empty:
    df_resultados_total_cf = df_resultados_total[["Folio", "Nombre del Alumno", "Grupo", "Nombre del Docente", "CCT", 
                                            "Nombre de la Escuela","Turno", "Sostenimiento","Total Aciertos", 
                                            'Aciertos Lenguajes','Aciertos Saberes y P. Científico', 
                                            'Aciertos Ética, Nat y Sociedades', 'Aciertos De lo Humano y lo Comunitario'
                                            ]]
#df_resultados_total = df_resultados_total.drop(cols_eliminar.columns, axis=1) #eliminamos columnas
#st.write(df_resultados_total) #Control para ver el DF final con el acumulado.
#st.write(df_resultados_total["Nombre del Alumno"])
# ------------------------------------- Fin del segmento para cargar y calificar -------------------------------------------


# ---------------------------------------Inicia segmento para armar los filtros -----------------------------------------------------
if not df_resultados_total.empty:
    # Obtener los valores únicos de cada columna
    alumnos_unicos = df_resultados_total_cf['Nombre del Alumno'].unique()
    grupos_unicos = df_resultados_total_cf['Grupo'].unique()
    docentes_unicos = df_resultados_total_cf['Nombre del Docente'].unique()
    escuelas_unicas = df_resultados_total_cf['Nombre de la Escuela'].unique()
    turnos_unicos = df_resultados_total_cf['Turno'].unique()
    sostenimientos_unicos = df_resultados_total_cf['Sostenimiento'].unique()

    # Crear filtros en la barra lateral de Streamlit
    filtro_sostenimiento = st.sidebar.selectbox("Filtrar por Sostenimiento", ["Todos"] + list(sostenimientos_unicos))
    filtro_turno = st.sidebar.selectbox("Filtrar por Turno", ["Todos"] + list(turnos_unicos))
    filtro_escuela = st.sidebar.selectbox("Filtrar por Nombre de la Escuela", ["Todos"] + list(escuelas_unicas))
    #filtro_docente = st.sidebar.selectbox("Filtrar por Nombre del Docente", ["Todos"] + list(docentes_unicos))
    filtro_grupo = st.sidebar.selectbox("Filtrar por Grupo", ["Todos"] + list(grupos_unicos))
    filtro_alumno = st.sidebar.selectbox("Filtrar por Nombre del Alumno", ["Todos"] + list(alumnos_unicos))

    # Aplicar los filtros al DataFrame
    if filtro_sostenimiento != "Todos":
        df_resultados_total_cf = df_resultados_total_cf[df_resultados_total_cf['Sostenimiento'] == filtro_sostenimiento]
        df_resultados_total = df_resultados_total[df_resultados_total['Sostenimiento'] == filtro_sostenimiento]
    if filtro_turno != "Todos":
        df_resultados_total_cf = df_resultados_total_cf[df_resultados_total_cf['Turno'] == filtro_turno]
        df_resultados_total = df_resultados_total[df_resultados_total['Turno'] == filtro_turno]
    if filtro_escuela != "Todos":
        df_resultados_total_cf = df_resultados_total_cf[df_resultados_total_cf['Nombre de la Escuela'] == filtro_escuela]
        df_resultados_total = df_resultados_total[df_resultados_total['Nombre de la Escuela'] == filtro_escuela]
    # if filtro_docente != "Todos":
    #     df_resultados_total_cf = df_resultados_total_cf[df_resultados_total_cf['Nombre del Docente'] == filtro_docente]
    #     df_resultados_total = df_resultados_total[df_resultados_total['Nombre del Docente'] == filtro_docente]
    if filtro_grupo != "Todos":
        df_resultados_total_cf = df_resultados_total_cf[df_resultados_total_cf['Grupo'] == filtro_grupo]
        df_resultados_total = df_resultados_total[df_resultados_total['Grupo'] == filtro_grupo]
    if filtro_alumno != "Todos":
        df_resultados_total_cf = df_resultados_total_cf[df_resultados_total_cf['Nombre del Alumno'] == filtro_alumno]
        df_resultados_total = df_resultados_total[df_resultados_total['Nombre del Alumno'] == filtro_alumno]
    # Mostrar el DataFrame filtrado
    st.write(df_resultados_total_cf) #línea de control para ver los cambios que se van produciendo al aplicar los filtros.

    st.write(df_resultados_total)


    # ------------Inicio creación de DF de PDAS ------------
    # Lista de nombres de las columnas
    columnas_pda = ['Reactivo', 'Contenido', 'PDA', 'Campo Formativo']

    # Lista de números del 1 al 60 para la columna 'Reactivo'
    reactivos = list(range(1, 61))

    # Crear un DataFrame vacío
    df_pdas = pd.DataFrame(columns=columnas_pda)

    # Llenar el DataFrame con los valores predeterminados
    df_pdas['Reactivo'] = df_respuestas["Reactivo"]
    df_pdas['Contenido'] = df_respuestas["Contenido"]
    df_pdas['PDA'] = df_respuestas["PDA"]

    # Asignar los valores de "Campo Formativo" de acuerdo con las categorías especificadas
    for i in reactivos:
        if i <= 20:
            df_pdas.at[i - 1, 'Campo Formativo'] = 'Lenguajes'
        elif i <= 40:
            df_pdas.at[i - 1, 'Campo Formativo'] = 'Saberes y Pensamiento Científico'
        elif i <= 53:
            df_pdas.at[i - 1, 'Campo Formativo'] = 'Ética, Naturaleza y Sociedades'
        else:
            df_pdas.at[i - 1, 'Campo Formativo'] = 'De lo Humano y lo Comunitario'

    #st.write(df_pdas) #Control para ver los pdas

    # ------------Fin creación de DF de PDAS ------------

    # Calcular el porcentaje de error por reactivo
    porcentaje_error = []
    for reactivo in range(1, 61):
        # Calcular el total de alumnos que contestaron correctamente el reactivo
        aciertos = df_resultados_total[f'P{reactivo}'].sum()
        # Calcular el total de alumnos
        total_alumnos = len(df_resultados_total)
        # Calcular el porcentaje de error
        porcentaje = ((total_alumnos - aciertos) / total_alumnos) * 100
        # Agregar el porcentaje de error a la lista
        porcentaje_error.append(porcentaje)

    # Crear el DataFrame con las columnas "Reactivo", "PDA" y "Porcentaje de Error"
    df_analisis = pd.DataFrame({
        "Reactivo": list(range(1, 61)),
        #"PDA": df_pda['PDA'].values,  # Asignar los valores de la columna "PDA" del DataFrame df_pda
        "Porcentaje de Error": porcentaje_error
    })

   
    # Fusionar los DataFrames utilizando la columna común "Reactivo"
    df_analisis_completo = pd.merge(df_analisis, df_pdas, on="Reactivo", how="inner")


    # Mostrar el DataFrame en Streamlit
    # Definir los estilos condicionales
    def highlight_error(val):
        if val > 50:
            return 'background-color: red; color: white'
        elif val > 30:
            return 'background-color: yellow'
        else:
            return 'background-color: green'

    
    #st.write(df_analisis)
    #st.write(df_resultados_total[["P10","P27","P29"]])


    tab1,tab2,tab3,tab4 = st.tabs(["Lenguajes", "Saberes y Pensamiento Científico","Ética, Naturaleza y Sociedades", "Delo Humano y lo Comunitario"])
    with tab1:
        st.header("Lenguajes")
        df_analisis_lenguajes = df_analisis_completo.loc[df_analisis_completo['Campo Formativo'] == "Lenguajes"]
        st.write(df_analisis_lenguajes.style.applymap(highlight_error, subset=['Porcentaje de Error']))
    with tab2:
        st.header("Saberes y Pensamiento Científico")
        df_analisis_sypc = df_analisis_completo.loc[df_analisis_completo['Campo Formativo'] == "Saberes y Pensamiento Científico"]
        st.write(df_analisis_sypc.style.applymap(highlight_error, subset=['Porcentaje de Error']))
    with tab3:
        st.header("Etica, Naturaleza y Sociedades")
        df_analisis_ens = df_analisis_completo.loc[df_analisis_completo['Campo Formativo'] == "Ética, Naturaleza y Sociedades"]
        st.write(df_analisis_ens.style.applymap(highlight_error, subset=['Porcentaje de Error']))
    with tab4:
        st.header("De lo Humano y lo Comunitario")
        df_analisis_hyc = df_analisis_completo.loc[df_analisis_completo['Campo Formativo'] == "De lo Humano y lo Comunitario"]
        st.write(df_analisis_hyc.style.applymap(highlight_error, subset=['Porcentaje de Error']))
