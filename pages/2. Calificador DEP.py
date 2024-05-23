import streamlit as st
import pandas as pd
import numpy as np
import base64
import io

# Esta parte del tablero tiene como objetivo principal mostrar los resultados del concurso para obtener los ganadores y mostrar las tables de puntuación, de acuerdo a los
# parámetros definidos en la convocatoria. Con esto se podrá verificar cada resultado.

# Agrega un texto semi-transparente como marca de agua
#st.markdown(
#    """
#    <style>
#        .watermark {
#            position: fixed;
#            top: 37%;
#            left: 40%;
#            transform: translate(-50%, -50%);
#            color: #E4E4E4;
#            font-size: 80px;
#            transform: rotate(-45deg);
#        }
#    </style>
#    <div class="watermark">Versión de Prueba</div>
#    """,
#    unsafe_allow_html=True
#)

# Agregar logotipo de la AEFCM
st.image('Logo_SATC_fondo.png', use_column_width=True)

#---------------------------------------------------------- Inicio Segmento para la carga de archivos ----------------------------------------------------------------------------

# Permitir al usuario elegir la cantidad de archivos a subir
numero_archivos = st.number_input("¿Cuántos archivos desea cargar? (Máximo 20)", min_value=1, max_value=20, step=1)


#Generamos un DF vacío para guardar los acumulados.
df_resultados_total = pd.DataFrame()        
df_alumnos_np = pd.DataFrame()
df_calificado = pd.DataFrame()


for i in range(numero_archivos):
    archivo_excel = st.file_uploader(f"Subir archivo {i+1}", type=["xlsm", "xlsx"])
    if archivo_excel is not None:
        df_alumnos = pd.read_excel(archivo_excel, sheet_name="Datos", header=2)
        df_respuestas = pd.read_excel(archivo_excel, sheet_name="Reactivos", header=1, usecols="A:E")
        # Juntamos los datos del nombre en una sóla celda y eliminamos las separadas
        df_alumnos["Nombre del Alumno"] =  df_alumnos["Apellido Paterno del Alumno"] + " " + df_alumnos["Apellido Materno del Alumno"] + " " +  df_alumnos["Nombre (s) del Alumno"]
        df_alumnos.drop(columns=["Nombre (s) del Alumno", "Apellido Paterno del Alumno", "Apellido Materno del Alumno"], inplace=True)
        # Reordenamos las columnas
        column_order = ["Folio", "Nombre del Alumno", "CCT"] + [col for col in df_alumnos.columns if col not in ["Folio", "Nombre del Alumno", "CCT"]]
        df_alumnos = df_alumnos[column_order]
        # Lista de columnas de respuestas
        columnas_respuestas = df_alumnos.columns[9:69]
        # Verificar si todas las respuestas de un alumno son "NP"
        alumnos_con_todas_np = df_alumnos[(df_alumnos[columnas_respuestas] == "NP").all(axis=1)]
        # Esta línea permite identificar los alumnos que no presentaron examen ("NP")
        datos_alumnos_np = alumnos_con_todas_np.iloc[:, :9]        
        df_alumnos_np = pd.concat([df_alumnos_np, datos_alumnos_np])
        # Ahora para calificar también habrá que generar un df con los resultados calificados y otro con las sumas de los campos formativos.
        # Empezamos limpiando el DF de los que tienen NP en todas las respuestas.
        # Obtener los índices de los alumnos con todas las respuestas "NP"
        indices_alumnos_np = alumnos_con_todas_np.index
        # Eliminar los alumnos con todas las respuestas "NP" del DataFrame original
        df_sin_np = df_alumnos.drop(indices_alumnos_np)
        #Creamos una copia para trabajar la calificación y no afectar el DF original
        df_para_calificar = df_sin_np.copy()
        # Calificar automáticamente las respuestas de los alumnos
        for index, row in df_respuestas.iterrows():
            numero_reactivo = row['Reactivo']
            respuesta_correcta = row['Correcta']
            # Obtener la respuesta del alumno para el reactivo actual
            respuesta_alumno = df_para_calificar[numero_reactivo]            
            # Comparar la respuesta del alumno con la respuesta correcta
            df_para_calificar[numero_reactivo] = respuesta_alumno.apply(
                lambda x: 1 if x == respuesta_correcta else (0 if pd.notnull(x) else pd.NA)
            )
        df_calificado = pd.concat([df_calificado, df_para_calificar])

#Control para ver el DF_Respuestas
# st.write(df_respuestas)

#Este DF tiene los registros de los alumnos que No Presentaron (NP)
#st.write(df_alumnos_np)
#Este DF tiene los registros de las calificaciones de cada reactivo quitando a los que No Presentaron
#st.write (df_calificado)

if archivo_excel is not None:

    #Generamos un nuevo DF con las columnas que utilizaremos para         
    df_resultados_total = df_calificado.iloc[:, 0:9]
    # Sumar los valores de las columnas de los reactivos del 1 al 60
    df_resultados_total['Total Aciertos'] = df_calificado.iloc[:, 9:69].sum(axis=1)
    # Sumar los valores de las columnas de los reactivos del 1 al 20
    df_resultados_total['Aciertos Lenguajes'] = df_calificado.iloc[:, 9:29].sum(axis=1)
    # Sumar los valores de las columnas de los reactivos del 21 al 40
    df_resultados_total['Aciertos Saberes y P. Científico'] = df_calificado.iloc[:, 29:49].sum(axis=1)
    # Sumar los valores de las columnas de los reactivos del 41 al 53
    df_resultados_total["Aciertos Ética, Nat. y Sociedades"] = df_calificado.iloc[:, 49:62].sum(axis=1)
    # Sumar los valores de las columnas de los reactivos del 54 al 60
    df_resultados_total['Aciertos De lo Humano y lo Comunitario'] = df_calificado.iloc[:, 62:69].sum(axis=1)



    # Forzamos que las columnas de datos numéricos se convierta a texto
    df_resultados_total["DEP"] = df_resultados_total["DEP"].astype(str)
    df_resultados_total["Zona Escolar"] = df_resultados_total["Zona Escolar"].astype(str)
    df_resultados_total["Folio"] = df_resultados_total["Folio"].astype(str)


    df_calificado["DEP"] = df_calificado["DEP"].astype(str)
    df_calificado["Zona Escolar"] = df_calificado["Zona Escolar"].astype(str)
    df_calificado["Folio"] = df_calificado["Folio"].astype(str)

    #Este DF tiene la sumatoria de las respuestas por Campo Formativo.
    #st.write(df_resultados_total)

    #--------------------------------------------------- Fin del segmento para calificar y armar los DF que se van a utilizar ---------------------------------------------------




    #-------------------------------------------------------------- Inicia segmento para definir los filtros ---------------------------------------------------------------------

    # Definimos las funciones para el fltrado en cada campo o criterio para filtrar
    @st.cache_data
    def filtro_dep(data, direccion):
        if direccion != "Todos":
            data = data[data['DEP'] == direccion]
        return data

    @st.cache_data
    def filtro_alcaldia(data, delegacion):
        if delegacion != "Todos":
            data = data[data['Alcaldía'] == delegacion]
        return data

    @st.cache_data
    def filtro_zona(data, zona):
        if zona != "Todos":
            data = data[data['Zona Escolar'] == zona]
        return data

    @st.cache_data
    def filtro_sostenimiento(data, sostenim):
        if sostenim != "Todos":
            data = data[data['Sostenimiento'] == sostenim]
        return data

    @st.cache_data
    def filtro_turno(data, jornada):
        if jornada != "Todos":
            data = data[data['Turno'] == jornada]
        return data

    @st.cache_data
    def filtro_escuela(data, school):
        if school != "Todos":
            data = data[data['Nombre de la Escuela'] == school]
        return data

    @st.cache_data
    def filtro_folio(data, number):
        if number != "Todos":
            data = data[data['Folio'] == number]
        return data


    # Función para convertir el DataFrame a un archivo Excel en formato base64
    @st.cache_data
    def convertir_a_excel(df):
        # Crear un objeto de BytesIO para almacenar el archivo Excel
        buffer = io.BytesIO()
        # Exportar el DataFrame a un archivo Excel en el buffer
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        # Reiniciar la posición del puntero del buffer al principio
        buffer.seek(0)
        # Convertir el contenido del buffer a base64
        excel_base64 = base64.b64encode(buffer.read()).decode()
        return excel_base64


    #Una vez que están definidos los filtros debemos aplicar la barra de filtros y utilizar un DF nuevo para que se vaya actuaizando el filtro


    #Con esta línea extraemos los valores únicos del campo "DEP"
    dep = np.concatenate((["Todos"], df_resultados_total["DEP"].unique())) 
    #Generamos la barra de filtro, un mensaje y los valores únicos del DF original
    slide_dep = st.sidebar.selectbox("Seleccione la Dirección de Educación Primaria", dep)
    # Generamos el DF con el filtro seleccionado
    df_resultados_total_f_dep = filtro_dep(df_resultados_total,slide_dep)

    alcaldia = np.concatenate((["Todos"], df_resultados_total_f_dep["Alcaldía"].unique()))
    slide_alcaldia = st.sidebar.selectbox("Seleccione la Alcaldía", alcaldia)
    df_resultados_total_f_alcaldia = filtro_alcaldia(df_resultados_total_f_dep, slide_alcaldia)

    zona_escolar = np.concatenate((["Todos"], df_resultados_total_f_alcaldia["Zona Escolar"].unique()))
    slide_zona = st.sidebar.selectbox("Seleccione la Zona Escolar", zona_escolar)
    df_resultados_total_f_zona = filtro_zona(df_resultados_total_f_alcaldia, slide_zona)

    sostenimiento = np.concatenate((["Todos"], df_resultados_total_f_zona["Sostenimiento"].unique()))
    slide_sostenimiento = st.sidebar.selectbox("Seleccione el tipo de Sostenimiento", sostenimiento)
    df_resultados_total_f_sost = filtro_sostenimiento(df_resultados_total_f_zona, slide_sostenimiento)

    turno = np.concatenate ((["Todos"], df_resultados_total_f_sost["Turno"].unique()))
    slide_turno = st.sidebar.selectbox("Seleccione el turno", turno)
    df_resultados_total_f_turno = filtro_turno(df_resultados_total_f_sost, slide_turno)

    escuela = np.concatenate((["Todos"], df_resultados_total_f_turno["Nombre de la Escuela"].unique()))
    slide_escuela = st.sidebar.selectbox("Seleccione la Escuela", escuela)
    df_resultados_total_f_escuela = filtro_escuela(df_resultados_total_f_turno, slide_escuela)

    folio = np.concatenate((["Todos"], df_resultados_total_f_escuela["Folio"].unique()))
    slide_folio = st.sidebar.selectbox("Seleccione el Folio", folio)
    df_resultados_total_f_folio = filtro_folio(df_resultados_total_f_escuela, slide_folio)

    df_resultados_filtrado = df_resultados_total_f_folio.copy()
    #st.write("Este es el DF df_resultados_filtrado")
    #st.write(df_resultados_filtrado)    
    #st.write("Este es el DF df_resultados_total")
    #st.write(df_resultados_total)    

    df_resultados_ordenado = df_resultados_filtrado.sort_values(by=["Total Aciertos","Aciertos Lenguajes","Aciertos Saberes y P. Científico","Aciertos Ética, Nat. y Sociedades","Aciertos De lo Humano y lo Comunitario"], ascending=False)
    #línea de control para ver los resultados del DF fitrado
    #st.write("Control para ver el DF ordenado")
    #st.write(df_resultados_ordenado)    

    #------------------------------------------------ Fin segmento para aplicar filtros ------------------------------------------------



    #---------------------------------------Inicio segmento para mostrar los resultados por Alcaldía--------------------------------------


    # Obtener el número de ganadores por alcaldía (supongamos que está en un diccionario llamado ganadores_por_alcaldia)
    ganadores_por_alcaldia = {
        'ÁLVARO OBREGÓN': {'PÚBLICO': 10, 'PARTICULAR': 7},
        'AZCAPOTZALCO': {'PÚBLICO': 6, 'PARTICULAR': 3},
        'BENITO JUÁREZ': {'PÚBLICO': 3, 'PARTICULAR': 7},
        'COYOACÁN': {'PÚBLICO': 8, 'PARTICULAR': 6},
        'CUAJIMALPA DE MORELOS': {'PÚBLICO': 4, 'PARTICULAR': 5},
        'CUAUHTÉMOC': {'PÚBLICO': 7, 'PARTICULAR': 4},
        'GUSTAVO A. MADERO': {'PÚBLICO': 21, 'PARTICULAR': 9},
        'IZTACALCO': {'PÚBLICO': 6, 'PARTICULAR': 2},
        'Región Centro': {'PÚBLICO': 17, 'PARTICULAR': 6},
        'Región Juárez': {'PÚBLICO': 17, 'PARTICULAR': 3},
        'MAGDALENA CONTRERAS': {'PÚBLICO': 4, 'PARTICULAR': 1},
        'MIGUEL HIDALGO': {'PÚBLICO': 4, 'PARTICULAR': 4},
        'MILPA ALTA': {'PÚBLICO': 3, 'PARTICULAR': 1},
        'TLÁHUAC': {'PÚBLICO': 8, 'PARTICULAR': 2},
        'TLALPAN': {'PÚBLICO': 11, 'PARTICULAR': 7},
        'VENUSTIANO CARRANZA': {'PÚBLICO': 7, 'PARTICULAR': 2},
        'XOCHIMILCO': {'PÚBLICO': 8, 'PARTICULAR': 2}
        }

    st.markdown("<h3 style='text-align: center;'>Resultados por Alcaldía</h3>", unsafe_allow_html=True)
    st.write("A continuación se muestran los resultados de escuelas públicas y particulares divididos por Alcaldía y de acuerdo a lo señalado en la Guía Operativa 2024.")

    for alcaldia in df_resultados_ordenado["Alcaldía"].unique():
        st.markdown(f"<h3 style='text-align: center;'>{alcaldia}</h3>", unsafe_allow_html=True)
        #if alcaldia != "IZTAPALAPA":
        tab1,tab2 = st.tabs(["Resultados de escuelas públicas", "Resultados de escuelas particulares"])
        with tab1:
            # Obtener el número de ganadores para el sostenimiento seleccionado
            ganadores_publicas = ganadores_por_alcaldia[alcaldia]["PÚBLICO"]
            # imprimir ganadores_publicas
            st.write(f"Para la Alcaldía {alcaldia} se deben seleccionar {ganadores_publicas} estudiantes de escuelas públicas")
            # Creamos un filtro de sostenimiento temporal:
            primeros_ganadores_publicas = df_resultados_ordenado[(df_resultados_ordenado['Sostenimiento'] == "PÚBLICO") & (df_resultados_ordenado['Alcaldía'] == alcaldia)]
            primeros_ganadores_publicas["Total Aciertos"] = primeros_ganadores_publicas["Total Aciertos"].astype(int)
            primeros_ganadores_publicas["Aciertos Lenguajes"] = primeros_ganadores_publicas["Aciertos Lenguajes"].astype(int)
            primeros_ganadores_publicas["Aciertos Saberes y P. Científico"] = primeros_ganadores_publicas["Aciertos Saberes y P. Científico"].astype(int)
            primeros_ganadores_publicas["Aciertos Ética, Nat. y Sociedades"] = primeros_ganadores_publicas["Aciertos Ética, Nat. y Sociedades"].astype(int)
            primeros_ganadores_publicas["Aciertos De lo Humano y lo Comunitario"] = primeros_ganadores_publicas["Aciertos De lo Humano y lo Comunitario"].astype(int)
            primeros_ganadores_publicas.reset_index(drop=True, inplace=True)
            primeros_ganadores_publicas.index += 1
            st.write(primeros_ganadores_publicas)

            if st.button(f'Descargar resultados de escuelas públicas ({alcaldia})'):
                # Convertir el DataFrame a un archivo Excel en formato base64
                excel_base64_gan_pub = convertir_a_excel(primeros_ganadores_publicas)
                # Generar un enlace de descarga para el archivo Excel
                href = f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_base64_gan_pub}'
                # Mostrar el botón de descarga
                st.markdown(f'<a href="{href}" download="dataframe.xlsx">Haz clic aquí para descargar los resultados en Excel</a>', unsafe_allow_html=True)

        with tab2:
            # Obtener el número de ganadores para el sostenimiento seleccionado
            ganadores_particulares = ganadores_por_alcaldia[alcaldia]["PARTICULAR"]
            # imprimir ganadores_publicas
            st.write(f"Para la Alcaldía {alcaldia} se deben seleccionar {ganadores_particulares} estudiantes de escuelas particulares")
            # Creamos un filtro de sostenimiento temporal:
            primeros_ganadores_particulares = df_resultados_ordenado[(df_resultados_ordenado['Sostenimiento'] == "PARTICULAR")&(df_resultados_ordenado["Alcaldía"]==alcaldia)]
            primeros_ganadores_particulares["Total Aciertos"] = primeros_ganadores_particulares["Total Aciertos"].astype(int)
            primeros_ganadores_particulares["Aciertos Lenguajes"] = primeros_ganadores_particulares["Aciertos Lenguajes"].astype(int)
            primeros_ganadores_particulares["Aciertos Saberes y P. Científico"] = primeros_ganadores_particulares["Aciertos Saberes y P. Científico"].astype(int)
            primeros_ganadores_particulares["Aciertos Ética, Nat. y Sociedades"] = primeros_ganadores_particulares["Aciertos Ética, Nat. y Sociedades"].astype(int)
            primeros_ganadores_particulares["Aciertos De lo Humano y lo Comunitario"] = primeros_ganadores_particulares["Aciertos De lo Humano y lo Comunitario"].astype(int)
            primeros_ganadores_particulares.reset_index(drop=True, inplace=True)
            primeros_ganadores_particulares.index += 1
            st.write(primeros_ganadores_particulares)
            if st.button(f'Descargar resultados de escuelas particulares ({alcaldia})'):
                # Convertir el DataFrame a un archivo Excel en formato base64
                excel_base64_gan_part = convertir_a_excel(primeros_ganadores_particulares)
                # Generar un enlace de descarga para el archivo Excel
                href = f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_base64_gan_part}'
                # Mostrar el botón de descarga
                st.markdown(f'<a href="{href}" download="dataframe.xlsx">Haz clic aquí para descargar los resultados en Excel</a>', unsafe_allow_html=True)        
        
    #---------------------------------------Fin segmento para mostrar los resultados por Alcaldía--------------------------------------



    #--------------------------------------------------- Inicio segmento de descargas ----------------------------------------------------------

    st.markdown("<h3 style='text-align: center;'>Otros documentos de interés</h3>", unsafe_allow_html=True)
    st.write("Aquí podras encontrar otros documentos que pudieras utilizar si lo consideras necesario")

    #-- Descargar DF con los alumnos que NO PRESENTARON
    st.markdown("<p style='text-align: justify;'><em>1.Registro de los alumnos que 'No Presentaron'.</em></p>", unsafe_allow_html=True)
    # Mostrar un botón de descarga utilizando st.download_button()
    if st.button('Descargar archivo con NP'):
        # Convertir el DataFrame a un archivo Excel en formato base64
        excel_base64_np = convertir_a_excel(df_alumnos_np)
        # Generar un enlace de descarga para el archivo Excel
        href = f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_base64_np}'
        # Mostrar el botón de descarga
        st.markdown(f'<a href="{href}" download="dataframe.xlsx">Haz clic aquí para descargar lo resultados en Excel</a>', unsafe_allow_html=True)

    #-- Descargar DF calificado con los filtros
    st.markdown("<p style='text-align: justify;'><em>2.Registro de calificación de cada reactivo.</em></p>", unsafe_allow_html=True)
    # Mostrar un botón de descarga utilizando st.download_button()
    if st.button('Descargar archivo calificado'):
        # Convertir el DataFrame a un archivo Excel en formato base64
        excel_base64_calif = convertir_a_excel(df_calificado)
        # Generar un enlace de descarga para el archivo Excel
        href = f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_base64_calif}'
        # Mostrar el botón de descarga
        st.markdown(f'<a href="{href}" download="dataframe.xlsx">Haz clic aquí para descargar los resultados en Excel</a>', unsafe_allow_html=True)

    #-- Descargar el DF con los resultados por campo formativo y por filtros
    st.markdown("<p style='text-align: justify;'><em>3.Registro de resultados por cada campo formativo y total de aciertos.</em></p>", unsafe_allow_html=True)
    # Mostrar un botón de descarga utilizando st.download_button()
    if st.button('Descargar archivo con resultados'):
        # Convertir el DataFrame a un archivo Excel en formato base64
        excel_base64_resultados = convertir_a_excel(df_resultados_ordenado)
        # Generar un enlace de descarga para el archivo Excel
        href = f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_base64_resultados}'
        # Mostrar el botón de descarga
        st.markdown(f'<a href="{href}" download="dataframe.xlsx">Haz clic aquí para descargar los resultados en Excel</a>', unsafe_allow_html=True)

    # ------------------------------------------------- Fin Segmento para descargar archivos ----------------------------------------------------------




    # ----------------------------------------------Inicia Segmento para ver porcentaje de aciertos ---------------------------------------------------

    st.markdown("<h3 style='text-align: center;'>Revisión del porcentaje de error por Reactivo</h3>", unsafe_allow_html=True)

    #prueba para ver cómo queda el df ordenado, para ver si podemos trabajar con ese
    #st.write(df_resultados_ordenado)

    df_pdas = pd.DataFrame()
    df_pdas['Reactivo'] = df_respuestas["Reactivo"]
    df_pdas['Contenido'] = df_respuestas["Contenido"]
    df_pdas['PDA'] = df_respuestas["PDA"]
    df_pdas['Campo Formativo'] = df_respuestas["Campo Formativo"]

    #control para ver df_pdas
    #st.write("ver df_pdas")
    #st.write(df_pdas)

    #Filtrar el df_calificado para que coincida con los filtros anteriores

    df_calificado_f_dep = filtro_dep(df_calificado,slide_dep)
    df_calificado_f_alcaldia = filtro_alcaldia(df_calificado_f_dep, slide_alcaldia)
    df_calificado_f_zona = filtro_zona(df_calificado_f_alcaldia, slide_zona)
    df_calificado_f_sost = filtro_sostenimiento(df_calificado_f_zona, slide_sostenimiento)
    df_calificado_f_turno = filtro_turno(df_calificado_f_sost, slide_turno)
    df_calificado_f_escuela = filtro_escuela(df_calificado_f_turno, slide_escuela)
    df_calificado_f_folio = filtro_folio(df_calificado_f_escuela, slide_folio)
    df_calificado_filtrado = df_calificado_f_folio.copy()

    #Ver f_filtrado
    #st.write("Ver el df_calificado_filtrado")
    #st.write(df_calificado_filtrado)

    # Calcular el porcentaje de error por reactivo
    porcentaje_error = []
    for reactivo in range(1, 61):
        # Calcular el total de alumnos que contestaron correctamente el reactivo
        aciertos = df_calificado_filtrado[reactivo].sum()
        # Calcular el total de alumnos
        total_alumnos = len(df_calificado_filtrado)
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

    #control ver df_analisis
    #st.write("Ver df_analisis")
    #st.write(df_analisis)

    # Fusionar los DataFrames utilizando la columna común "Reactivo"
    df_analisis_completo = pd.merge(df_analisis, df_pdas, on="Reactivo", how="inner")

    #Control ver df_analisis completo, ya con ambos fusionados
    #st.write("vere ambos df fusionados")
    #st.write(df_analisis_completo)

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


    tab1,tab2,tab3,tab4 = st.tabs(["Lenguajes", "Saberes y Pensamiento Científico","Ética, Naturaleza y Sociedades", "De lo Humano y lo Comunitario"])
    with tab1:
        #st.header("Lenguajes")
        df_analisis_lenguajes = df_analisis_completo.loc[df_analisis_completo['Campo Formativo'] == "Lenguajes"]
        df_analisis_lenguajes['Reactivo'] = df_analisis_lenguajes['Reactivo'].rank(method='dense').astype(int)
        st.write(df_analisis_lenguajes.loc[:, ['Reactivo', 'Porcentaje de Error', 'Contenido', 'PDA']].style.hide_index().applymap(highlight_error, subset=['Porcentaje de Error']))
    with tab2:
        #st.header("Saberes y Pensamiento Científico")
        df_analisis_sypc = df_analisis_completo.loc[df_analisis_completo['Campo Formativo'] == "Saberes y Pensamiento Científico"]
        df_analisis_sypc['Reactivo'] = df_analisis_sypc['Reactivo'].rank(method='dense').astype(int)
        st.write(df_analisis_sypc.loc[:, ['Reactivo', 'Porcentaje de Error', 'Contenido', 'PDA']].style.hide_index().applymap(highlight_error, subset=['Porcentaje de Error']))
    with tab3:
        #st.header("Etica, Naturaleza y Sociedades")
        df_analisis_ens = df_analisis_completo.loc[df_analisis_completo['Campo Formativo'] == "Ética, Naturaleza y Sociedades"]
        df_analisis_ens['Reactivo'] = df_analisis_ens['Reactivo'].rank(method='dense').astype(int)
        st.write(df_analisis_ens.loc[:, ['Reactivo', 'Porcentaje de Error', 'Contenido', 'PDA']].style.hide_index().applymap(highlight_error, subset=['Porcentaje de Error']))
    with tab4:
        #st.header("De lo Humano y lo Comunitario")
        df_analisis_hyc = df_analisis_completo.loc[df_analisis_completo['Campo Formativo'] == "De lo Humano y lo Comunitario"]
        df_analisis_hyc['Reactivo'] = df_analisis_hyc['Reactivo'].rank(method='dense').astype(int)
        st.write(df_analisis_hyc.loc[:, ['Reactivo', 'Porcentaje de Error', 'Contenido', 'PDA']].style.hide_index().applymap(highlight_error, subset=['Porcentaje de Error']))


    #Para conjuntar los originales con los cambios del ranking en el Reactivo:

    df_porcentaje_error = pd.DataFrame()
    df_porcentaje_error = pd.concat([df_analisis_lenguajes,df_analisis_sypc,df_analisis_ens,df_analisis_hyc])

    #mostrar el df concatenado
    #st.write("Mostrar el resultado concatenado pdas/grado de error")
    #st.write(df_porcentaje_error)


    #Para descargar resultado de reactivos:

    if st.button('Descargar archivo con grado de error'):
        # Convertir el DataFrame a un archivo Excel en formato base64
        excel_base64_resultados = convertir_a_excel(df_porcentaje_error)
        # Generar un enlace de descarga para el archivo Excel
        href = f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_base64_resultados}'
        # Mostrar el botón de descarga
        st.markdown(f'<a href="{href}" download="dataframe.xlsx">Haz clic aquí para descargar lo resultados en Excel</a>', unsafe_allow_html=True)
