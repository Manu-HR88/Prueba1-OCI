import streamlit as st
import pandas as pd
import base64
import io

# Esta parte del tablero tiene como objetivo principal mostrar los resultados del concurso para obtener los ganadores y mostrar las tables de puntuación, de acuerdo a los
# parámetros definidos en la convocatoria. Con esto se podrá verificar cada resultado.

st.image('Logo_SATC_fondo.png', use_column_width=True)



#---------------------------------------------------------- Inicio Segmento para la carga de archivos ----------------------------------------------------------------------------

# Extraemos las respuestas de los alumnos (aquí hay que considerar configurar que el usuario ingrese un archivo a través de un botón)
#df_alumnos = pd.read_excel("OCI2024_Escuela.xlsm", sheet_name="Datos", header=2)

# Extraemos las respuestas asignadas como correctas del examen (aquí hay que buscar la manera de configurar que de la mimsa carga se extraigan ambas hojas)
#df_respuestas = pd.read_excel("OCI2024_Escuela.xlsm", sheet_name="Reactivos", header=1, usecols="A:B")



# Utilizamos el botón para cargar datos.
st.markdown("<h1 style='text-align: center; font-size: 20px; '>Cargue su archivo Excel capturado</h1>", unsafe_allow_html=True)
archivo_excel = st.file_uploader("", type=["xlsm", "xlsx"])

if archivo_excel is not None:
    # Leer la hoja de reactivos
    df_alumnos = pd.read_excel(archivo_excel, sheet_name="Datos", header=2)
    # Leer la hoja de respuestas
    df_respuestas = pd.read_excel(archivo_excel, sheet_name="Reactivos", header=1, usecols="A:B")
    #st.write("control para ver cómo cargo la hoja de alumnos")
    #st.write(df_alumnos)
    #st.write("control para ver cómo cargo la hoja de respuestas correctas")
    #st.write(df_respuestas)

    # ----------------------------------------------------------------- Fin carga de archivos -----------------------------------------------------------------------------------


    # -------------------------------------------------------------- Inicio calificación de examenes ----------------------------------------------------------------------------
    # Definimos la función para comparar la respuesta del alumno con la correcta y calificarla
    @st.cache_data
    def calificar_respuesta(respuesta_alumno, respuesta_correcta):
        if respuesta_alumno == respuesta_correcta:
            return 1
        else:
            return 0
        
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
        
    # Combinar los DataFrames utilizando merge
    df_calificaciones = df_alumnos.copy()  # Creamos una copia del DataFrame de alumnos para conservarlo intacto
    for pregunta in df_respuestas['Reactivo']:
        # Merge los DataFrames con base en la pregunta actual 
        df_temp = pd.merge(df_alumnos[['Nombre del Alumno', pregunta]], df_respuestas[df_respuestas['Reactivo'] == pregunta], left_on=pregunta, right_on='Correcta', how='left')
        # Aplicar la función de calificación
        df_temp['P' + str(pregunta)] = df_temp.apply(lambda row: calificar_respuesta(row[pregunta], row['Correcta']), axis=1)
        # Concatenar los resultados al DataFrame de calificaciones
        df_calificaciones = pd.merge(df_calificaciones, df_temp[['Nombre del Alumno', 'P' + str(pregunta)]], on='Nombre del Alumno')

    #st.write(df_calificaciones) #control para ver el resultado de la calificación

    # Creamos una copia para trabajar los resultados por campo formativo
    df_resultados = df_calificaciones.copy()

    # Eliminamos las columnas de las respuestas, para dejar solo las calificadas
    df_resultados = df_resultados.drop(range(1,61), axis = 1)

    # Vamos a generar las columnas de resultados
    # Lista de nombres de las columnas que contienen las respuestas calificadas por campo formativo
    cols_aciertos_totales = ['P' + str(i) for i in range(1, 61)]
    cols_aciertos_lenguajes = ['P' + str(i) for i in range(1, 21)]
    cols_aciertos_saberes = ['P' + str(i) for i in range(21, 41)]
    cols_aciertos_etica = ['P' + str(i) for i in range(41, 56)]
    cols_aciertos_humano = ['P' + str(i) for i in range(56, 61)]

    # Calcular la cantidad de aciertos en cada campo formativo sumando las respuestas calificadas correspondientes
    df_resultados['Total Aciertos'] = df_resultados[cols_aciertos_totales].sum(axis=1)
    df_resultados['Aciertos Lenguajes'] = df_resultados[cols_aciertos_lenguajes].sum(axis=1)
    df_resultados['Aciertos Saberes y P. Científico'] = df_resultados[cols_aciertos_saberes].sum(axis=1)
    df_resultados['Aciertos Ética, Nat y Sociedades'] = df_resultados[cols_aciertos_etica].sum(axis=1)
    df_resultados['Aciertos De lo Humano y lo Comunitario'] = df_resultados[cols_aciertos_humano].sum(axis=1)

    # Revisamos los resultados de los campos formativos
    #Control para ver los resultados por Campo Formativo
    #st.write(df_resultados.iloc[:,68:73]) # control para visualizar los resultados por campo formativo

    # --------------------------------------------------------------- Fin calificación de exámenes ----------------------------------------------------------------------------


    # ----------------------------------------------------------- Inicio mostrar resultados al usuario ------------------------------------------------------------------------

    # Creamos filtro para que cada variable tenga un DF público y privado
    # Si se está analizando a una escuela, seguramente tendrá solo uno.
    # Habrá que ver cómo filtrarlo en el tablero para que no aparezca vacío.
    df_calificado_publico = df_resultados[df_resultados["Sostenimiento"] == "PÚBLICO"]
    df_calificado_privado = df_resultados[df_resultados["Sostenimiento"] == "PARTICULAR"]
    #Definimos el total de columnas posibles
    cols_globales = ["Folio","Grupo","Nombre del Docente","CCT","Nombre de la Escuela","Turno","Sostenimiento","Zona Escolar","Alcaldia","DEP"]
    cols_especificas =[] #Generamos una lista vacía para almacenar las que traiga el archivo original
    cols_eliminar = df_resultados.filter(regex='^P[1-9]|[1-5][0-9]|60$', axis=1) #columnas que coinciden con el patrón 'P' seguido de un número del 1 al 60 para la eliminación
    # Creamos un ciclo que recorra el total de columnas 
    for col in cols_globales:
        if col in df_calificado_publico.columns:
            cols_especificas.append(col)


    # Vamos a crear un condicional "if" para que sólo se muestre la información de los DF de escuelas públicas y privadas.
    if not df_calificado_publico.empty:
        #Convertimos en texto las columnas Folio, Zona Escolar y DEP
        df_calificado_publico["Folio"] = df_calificado_publico["Folio"].astype(str)
        if "Zona Escolar" in df_calificado_publico.columns:
            df_calificado_publico["Zona Escolar"] = df_calificado_publico["Zona Escolar"].astype(str)
        if "DEP" in df_calificado_publico.columns:
            df_calificado_publico["DEP"] = df_calificado_publico["DEP"].astype(str)
        # Encontrar el índice del alumno con el mayor número de aciertos
        indice_max_aciertos_publico = df_calificado_publico["Total Aciertos"].idxmax()
        # Obtener el número máximo de aciertos
        max_aciertos_publico = df_calificado_publico.loc[indice_max_aciertos_publico, "Total Aciertos"]
        # Obtener los nombres de los alumnos con el máximo número de aciertos
        alumnos_max_aciertos_publico = df_calificado_publico[df_calificado_publico["Total Aciertos"] == max_aciertos_publico]["Nombre del Alumno"].tolist()
        # Obtener información adicional para el alumno con el mayor número de aciertos en escuelas públicas
        info_alumno_publico = df_calificado_publico.loc[indice_max_aciertos_publico, cols_especificas]  #["CCT", "Nombre de la Escuela", "Turno"] esta es otra opción para poner solamente las columnas que se quieran
  
        if len(alumnos_max_aciertos_publico) > 1:
            texto_publico_empate = f"<div style='text-align: center; font-size: 20px;'>Empate entre los siguientes participantes con {max_aciertos_publico} aciertos:</div>"
            st.write(texto_publico_empate, unsafe_allow_html=True)
            for alumno in alumnos_max_aciertos_publico:
                st.write(f"<div style='text-align: center; font-size: 20px;'>{alumno}</div>", unsafe_allow_html=True)
                info_alumno_empate = df_calificado_publico[df_calificado_publico["Nombre del Alumno"] == alumno][cols_especificas].iloc[0]
                for i in range(len(info_alumno_empate)):
                    st.write(cols_especificas[i], ":", info_alumno_empate.iloc[i])
        else:
            texto_publico = f"<div style='text-align: center; font-size: 20px;'>Participante con mayor número de aciertos de escuelas públicas: <br><span style='font-size: 30px; font-weight: bold;'>{alumnos_max_aciertos_publico[0]}</span> <br> con {max_aciertos_publico} aciertos.</div>"
            st.write(texto_publico, unsafe_allow_html=True)
            for i in range(len(info_alumno_publico)):
                st.write(cols_especificas[i], ":", info_alumno_publico.iloc[i])

        # Para armar el DF que se pueda mostrar con los resultados para consulta del usuario.
        df_resumen_publico= df_calificado_publico.copy() # se crea una copia para no afectar el DF original, si se llega a ocupar.
        df_resumen_publico = df_resumen_publico.drop(cols_eliminar.columns, axis=1) #eliminamos columnas
        #Creamos un botón para ver los resultados completos
        if st.button("Ver resultados de escuelas públicas"):
            st.write(df_resumen_publico.sort_values(by=["Total Aciertos","Aciertos Lenguajes","Aciertos Saberes y P. Científico","Aciertos Ética, Nat y Sociedades","Aciertos De lo Humano y lo Comunitario"], ascending=False)) # Control para revisar resultado
        
#-------------prueba descarga excel
  
        # Mostrar un botón de descarga utilizando st.download_button()
        if st.button('Descargar archivo de escuelas públicas'):
            # Convertir el DataFrame a un archivo Excel en formato base64
            excel_base64 = convertir_a_excel(df_resumen_publico.sort_values(by=["Total Aciertos","Aciertos Lenguajes","Aciertos Saberes y P. Científico","Aciertos Ética, Nat y Sociedades","Aciertos De lo Humano y lo Comunitario"], ascending=False))
            # Generar un enlace de descarga para el archivo Excel
            href = f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_base64}'
            # Mostrar el botón de descarga
            st.markdown(f'<a href="{href}" download="dataframe.xlsx">Haz clic aquí para descargar lo resultados en Excel</a>', unsafe_allow_html=True)

#----------------fin prueba descarga excel
    
    # Se repite el mismo proceso anterior pero ahora con el df de escuelas privadas
    if not df_calificado_privado.empty:
        #Convertimos en texto las columnas Folio, Zona Escolar y DEP
        df_calificado_privado["Folio"] = df_calificado_privado["Folio"].astype(str)
        if "Zona Escolar" in df_calificado_privado.columns:
            df_calificado_privado["Zona Escolar"] = df_calificado_privado["Zona Escolar"].astype(str)
        if "DEP" in df_calificado_privado.columns:
            df_calificado_privado["DEP"] = df_calificado_privado["DEP"].astype(str)
        indice_max_aciertos_privado = df_calificado_privado["Total Aciertos"].idxmax()
        max_aciertos_privado = df_calificado_privado.loc[indice_max_aciertos_privado, "Total Aciertos"]
        alumnos_max_aciertos_privado = df_calificado_privado[df_calificado_privado["Total Aciertos"] == max_aciertos_privado]["Nombre del Alumno"].tolist()
        info_alumno_privado = df_calificado_privado.loc[indice_max_aciertos_privado, cols_especificas]  #["CCT", "Nombre de la Escuela", "Turno"] esta es otra opción para poner solamente las columnas que se quieran

        if len(alumnos_max_aciertos_privado) > 1:
            texto_privado_empate = f"<div style='text-align: center; font-size: 20px;'>Empate entre los siguientes participantes con {max_aciertos_privado} aciertos:</div>"
            st.write(texto_privado_empate, unsafe_allow_html=True)
            for alumno in alumnos_max_aciertos_privado:
                st.write(f"<div style='text-align: center; font-size: 20px;'>{alumno}</div>", unsafe_allow_html=True)
                info_alumno_empate = df_calificado_privado[df_calificado_privado["Nombre del Alumno"] == alumno][cols_especificas].iloc[0]
                for i in range(len(info_alumno_empate)):
                    st.write(cols_especificas[i], ":", info_alumno_empate.iloc[i])
        else:
            texto_privado = f"<div style='text-align: center; font-size: 20px;'>Participante con mayor número de aciertos de escuelas públicas: <br><span style='font-size: 30px; font-weight: bold;'>{alumnos_max_aciertos_publico[0]}</span> <br> con {max_aciertos_publico} aciertos.</div>"
            st.write(texto_privado, unsafe_allow_html=True)
            for i in range(len(info_alumno_privado)):
                st.write(cols_especificas[i], ":", info_alumno_privado.iloc[i])

        # Para armar el DF que se pueda mostrar con los resultados para consulta del usuario.
        df_resumen_privado= df_calificado_privado.copy() # se crea una copia para no afectar el DF original, si se llega a ocupar.
        df_resumen_privado = df_resumen_privado.drop(cols_eliminar.columns, axis=1) #eliminamos columnas

        if st.button("Ver resultados de escuelas particulares"):
            st.write(df_resumen_privado.sort_values(by=["Total Aciertos","Aciertos Lenguajes","Aciertos Saberes y P. Científico","Aciertos Ética, Nat y Sociedades","Aciertos De lo Humano y lo Comunitario"], ascending=False)) # Control para revisar resultados

        if st.button('Descargar archivo de escuelas particulares'):
            # Convertir el DataFrame a un archivo Excel en formato base64
            excel_base64 = convertir_a_excel(df_resumen_privado.sort_values(by=["Total Aciertos","Aciertos Lenguajes","Aciertos Saberes y P. Científico","Aciertos Ética, Nat y Sociedades","Aciertos De lo Humano y lo Comunitario"], ascending=False))
            # Generar un enlace de descarga para el archivo Excel
            href = f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_base64}'
            # Mostrar el botón de descarga
            st.markdown(f'<a href="{href}" download="dataframe.xlsx">Haz clic aquí para descargar el DataFrame como Excel</a>', unsafe_allow_html=True)

