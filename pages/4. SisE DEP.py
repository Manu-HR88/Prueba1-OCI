import streamlit as st
import pandas as pd
#import matplotlib.pyplot as plt
#import seaborn as sns
import numpy as np

'''
Esta página del tablero, tiene como finalidad ser el control para el exámen OCI en la etapa 2 donde el examen sería el mismo para las 
4 DEP's y fuera elaborado por los supervisores del equipo base.
Las características de este tablero serían el arranque para después adaptar el que pudiera servirles a la Zona y posteriormente a la Escuela.
'''

st.markdown("<h1 style='text-align: center; color: orange;'>¡Sistema de Evaluación OCI 2024!</h1>", unsafe_allow_html=True)
#---------------------------------------------EN ESTE SEGMENTO SE DEFINEN LOS BOTONES PARA CARGAR LOS ARCHIVOS EN EXCEL--------------------------------------
#Para cargar archivos de reactivos
reactivos = st.file_uploader("Cargue su archivo en excel con los reactivos") #Con esta línea insertamos un botón para cargar el archivo con los reactivos
df_reactivos = pd.read_excel(reactivos) #para pasar el archivo excel de reactivos a un DataFrame
#df_reactivos = pd.read_excel("C:/Users/Usuario/Documents/OCI/2024/Tablero/Tabla de respuestas OCI.xlsx") #De manera temporal para usar sin estar cargando el archivo
st.write("Muestra del arhivo de reactivos")
st.write(df_reactivos) # mostramos el archivo cargado. (para control)

#Para cargar archivos de resultados
resultados = st.file_uploader("Cargue su archivo con los resultados de sus alumnos")
df_resultados =pd.read_excel(resultados)
#df_resultados = pd.read_excel("C:/Users/Usuario/Documents/OCI/2024/Tablero/Tabla de resultados.xlsx") #De manera temporal para usar sin estar cargando el archivo
st.write("Muestra del archivo de resultados subido")
st.write(df_resultados)

#Para cargar archivos de resultados (Este apartado sería sólo para la zona y la DEP ya que la escuela probablemente no lo requiera)
directorio = st.file_uploader("Cargue el directorio")
df_directorio = pd.read_excel(directorio)
#df_directorio = pd.read_excel("C:/Users/Usuario/Documents/OCI/2024/Tablero/Directorio_CSEP.xlsx")



# Using object notation
add_selectbox = st.sidebar.selectbox(
    "Filtro de resultados",
    ("Por Alcaldía ", "Por Zona", "Por Escuela", "Por grupo")
)





#-------------------------------------------------FIN DEL SEGMENTO PARA CCARGAR ARCHIVOS EN EXCEL ---------------------------------------------------------





#---------------------------------SEGMENTO PARA CALIFICAR EL ARCHIVO DE RESULTADOS CON LA BASE DE LOS REACTIVOS----------------------------------------------------

# Crear un DataFrame vacío para almacenar los resultados
df_calificado = pd.DataFrame(columns=["CCT","Nombre Escuela","Turno","Sostenimiento","DEP","Zona Escolar","Alcaldía",'Alumno', 'P1', 'P2', 'P3','P4','P5','P6','P7','P8','P9','P10'])

# Iterar sobre cada fila del DataFrame de respuestas
for index, row in df_resultados.iterrows():
    # Combina las columnas de nombre del alumno en una sola columna 'Alumno'
    alumno = f"{row['APELLIDO PATERNO']} {row['APELLIDO MATERNO']} {row['NOMBRE(S)']}"
    cct = row["CCT"]

# Obtener información de la escuela utilizando merge
    fila_escuela = df_directorio[df_directorio['CCT'] == cct]

# Crear un diccionario para almacenar los resultados de cada pregunta
    resultado_preguntas = {'CCT': cct,
                            'Nombre Escuela': fila_escuela['ESCUELA'].iloc[0] if not fila_escuela.empty else '',
                            'Turno':fila_escuela['NOM TUR'].iloc[0] if not fila_escuela.empty else '',
                            'Sostenimiento': fila_escuela['SOSTENIMIENTO'].iloc[0] if not fila_escuela.empty else '',
                            'DEP':fila_escuela['DEP'].iloc[0] if not fila_escuela.empty else '',
                            'Zona Escolar':fila_escuela['ZONA'].iloc[0] if not fila_escuela.empty else '',
                            'Alcaldía': fila_escuela['ALCALDIA'].iloc[0] if not fila_escuela.empty else '',
                            'Alumno': alumno}
    
    # Iterar sobre cada pregunta y comparar la respuesta del alumno con la respuesta correcta
    for pregunta in df_reactivos['Reactivo']:
        respuesta_alumno = row[pregunta]
        respuesta_correcta = df_reactivos.loc[df_reactivos['Reactivo'] == pregunta, 'Respuesta correcta'].values[0]
        
        # Asignar 1 si coincide, 0 si no coincide, y NaN si la respuesta del alumno es NaN
        if pd.isna(respuesta_alumno):
            resultado_preguntas[pregunta] = np.nan
        else:
            resultado_preguntas[pregunta] = 1 if respuesta_alumno == respuesta_correcta else 0
    
    # Agregar el diccionario al DataFrame de resultados
    df_calificado = pd.concat([df_calificado, pd.DataFrame([resultado_preguntas])], ignore_index=True)

# Mostrar el DataFrame resultante

st.write(df_calificado)

#Para armar el cuadro, incluyendo el total de aciertos por campo formativo.
df_calificado["Total Aciertos"] = df_calificado.iloc[:, 8:19].sum(axis=1)
df_calificado["Aciertos Lenguaje"] = df_calificado.iloc[:, 8:12].sum(axis=1)
df_calificado["Aciertos Saberes y P. Científico"] = df_calificado.iloc[:, 12:16].sum(axis=1)
df_calificado["Aciertos Ética, Nat. y Sociedad"] = df_calificado.iloc[:, 16:18].sum(axis=1)

#--------------------------------------------------------FIN DE SEGMENTO PARA CALIFICAR RESULTADOS-------------------------------------------------------------------




#-----------------------------------------------------------SEGMENTO PARA MOSTRAR LOS GANADORES------------------------------------------------------------------------

#--------Aquí hay que hacer la división para que muestre el ganador para escuelas públicas y privadas
#Creamos filtro para que cada variable tenga un DF público y privado
df_calificado_publico = df_calificado[df_calificado["Sostenimiento"] == "PÚBLICO"]
df_calificado_privado = df_calificado[df_calificado["Sostenimiento"] == "PRIVADO"]

# Convertir la columna "Total Aciertos" a tipo numérico tanto de público como privado
df_calificado_publico=df_calificado_publico.copy()
df_calificado_publico["Total Aciertos"] = pd.to_numeric(df_calificado_publico["Total Aciertos"], errors='coerce')
df_calificado_privado=df_calificado_privado.copy()
df_calificado_privado["Total Aciertos"] = pd.to_numeric(df_calificado_privado["Total Aciertos"], errors='coerce')


# Encontrar el índice del alumno con el mayor número de aciertos
indice_max_aciertos_publico = df_calificado_publico["Total Aciertos"].idxmax()
indice_max_aciertos_privado = df_calificado_privado["Total Aciertos"].idxmax()

# Obtener el número máximo de aciertos
max_aciertos_publico = df_calificado_publico.loc[indice_max_aciertos_publico, "Total Aciertos"]
max_aciertos_privado = df_calificado_privado.loc[indice_max_aciertos_privado, "Total Aciertos"]

# Obtener los nombres de los alumnos con el máximo número de aciertos
alumnos_max_aciertos_publico = df_calificado_publico[df_calificado_publico["Total Aciertos"] == max_aciertos_publico]["Alumno"].tolist()
alumnos_max_aciertos_privado = df_calificado_privado[df_calificado_privado["Total Aciertos"] == max_aciertos_privado]["Alumno"].tolist()

# Obtener información adicional para el alumno con el mayor número de aciertos en escuelas privadas
info_alumno_publico = df_calificado_publico.loc[indice_max_aciertos_publico, ["CCT", "Nombre Escuela", "Turno"]]

# Imprimir mensaje condicional para escuelas públicas
if len(alumnos_max_aciertos_publico) == 1:
    st.write(f"El alumno con el mayor número de aciertos de escuelas públicas es \n{alumnos_max_aciertos_publico[0]} con {max_aciertos_publico} aciertos.")
    st.write(f"CCT: {info_alumno_publico['CCT']} \nEscuela: {info_alumno_publico['Nombre Escuela']} \nTurno: {info_alumno_publico['Turno']}")
else:
    st.write("Hay un empate entre los siguientes alumnos de escuelas públicas:")
    for i, alumno_publico in enumerate(alumnos_max_aciertos_publico):
        cct_publico = info_alumno_publico['CCT'].split(',')[i].strip() if i < len(info_alumno_publico['CCT'].split(',')) else info_alumno_publico['CCT']
        nombre_escuela_publico = info_alumno_publico['Nombre Escuela'].split(',')[i].strip() if i < len(info_alumno_publico['Nombre Escuela'].split(',')) else info_alumno_publico['Nombre Escuela']
        turno_publico = info_alumno_publico['Turno'].split(',')[i].strip() if i < len(info_alumno_publico['Turno'].split(',')) else info_alumno_publico['Turno']
        st.write(f"{i + 1}. {alumno_publico} con {max_aciertos_publico} aciertos.")
        st.write(f"CCT: {cct_publico}, \nEscuela: {nombre_escuela_publico}, \nTurno: {turno_publico}")
        
# Obtener información adicional para el alumno con el mayor número de aciertos en escuelas privadas
info_alumno_privado = df_calificado_privado.loc[indice_max_aciertos_privado, ["CCT", "Nombre Escuela", "Turno"]]

# Imprimir mensaje condicional para escuelas privadas
if len(alumnos_max_aciertos_privado) == 1:
    st.write(f"El alumno con el mayor número de aciertos de escuelas privadas es {alumnos_max_aciertos_privado[0]} con {max_aciertos_privado} aciertos.")
    st.write(f"CCT: {info_alumno_privado['CCT']}, \nEscuela: {info_alumno_privado['Nombre Escuela']}, \nTurno: {info_alumno_privado['Turno']}")
else:
    st.write("Hay un empate entre los siguientes alumnos de escuelas privadas:")
    for i, alumno_privado in enumerate(alumnos_max_aciertos_privado):
        cct_privado = info_alumno_privado['CCT'].split(',')[i].strip() if i < len(info_alumno_privado['CCT'].split(',')) else info_alumno_privado['CCT']
        nombre_escuela_privado = info_alumno_privado['Nombre Escuela'].split(',')[i].strip() if i < len(info_alumno_privado['Nombre Escuela'].split(',')) else info_alumno_privado['Nombre Escuela']
        turno_privado = info_alumno_privado['Turno'].split(',')[i].strip() if i < len(info_alumno_privado['Turno'].split(',')) else info_alumno_privado['Turno']
        st.write(f"{i + 1}. {alumno_privado} con {max_aciertos_privado} aciertos.")
        st.write(f"CCT: {cct_privado} \nEscuela: {nombre_escuela_privado} \nTurno: {turno_privado}")

#Prueba para ordenar el DF calificado resultados de escuelas públicas
df_calif_ord_publico = df_calificado_publico.sort_values(by=["Total Aciertos","Aciertos Lenguaje","Aciertos Saberes y P. Científico","Aciertos Ética, Nat. y Sociedad"], ascending=False)


#Prueba para ordenar el DF calificado resultados de escuelas privadas
df_calif_ord_privado = df_calificado_privado.sort_values(by=["Total Aciertos","Aciertos Lenguaje","Aciertos Saberes y P. Científico","Aciertos Ética, Nat. y Sociedad"], ascending=False)
#Prueba para dejar del DF filtrado por tipo de escuela los mejores, en caso de empate
total_reg_privado = df_calif_ord_privado[df_calif_ord_privado["Total Aciertos"] == df_calif_ord_privado["Total Aciertos"].max()].shape[0]
df_calif_ord_privado= df_calif_ord_privado[:total_reg_privado].drop(columns=["P1","P2","P3","P4","P5","P6","P7","P8","P9","P10"])
st.write ("control 1")
st.button("Mostrar resultados", type="primary")
if st.button("Escuelas Privadas"):
    st.write(df_calif_ord_privado)


#st.write(df_calif_ord_privado)

df_calif_ord_publico = df_calificado_publico.sort_values(by=["Total Aciertos","Aciertos Lenguaje","Aciertos Saberes y P. Científico","Aciertos Ética, Nat. y Sociedad"], ascending=False)
#Prueba para dejar del DF filtrado por tipo de escuela los mejores, en caso de empate
total_reg_publico = df_calif_ord_publico[df_calif_ord_publico["Total Aciertos"] == df_calif_ord_publico["Total Aciertos"].max()].shape[0]
df_calif_ord_publico = df_calif_ord_publico[:total_reg_publico].drop(columns=["P1","P2","P3","P4","P5","P6","P7","P8","P9","P10"])
st.button("Mostrar resultados Públicas")
if st.button("Escuelas Públicas"):
    st.write(df_calif_ord_publico)


#st.write(df_calif_ord_publico)
#----------------------------------------------------------FIN DEL SEGMENTO PARA MOSTRAR LOS GANADORES----------------------------------------------------------------------
        



#-------------------------------------------------------------SEGMENTO PARA GRAFICAR LOS RESULTADOS--------------------------------------------------------------------------


df_preguntas= df_calificado[["P1","P2","P3","P4","P5","P6","P7","P8","P9","P10"]]
resultados_por_pregunta = {
    'Aciertos': df_preguntas.eq(1).sum(),
    'Errores': df_preguntas.eq(0).sum(),
    'No Contestadas': df_preguntas.isna().sum()
}

df_prueba = pd.DataFrame(resultados_por_pregunta)

df_prueba["Total Contestadas"] = df_prueba["Aciertos"] + df_prueba["Errores"]
df_prueba["No Contestadas"] = 14 - df_prueba["Total Contestadas"]


tab1, tab2, tab3 = st.tabs(["Lenguajes", "Saberes y P. Científico", "Ética, Nat. y Sociedades"])
with tab1:
   st.header("Lenguajes")
   st.write(df_prueba)

with tab2:
   st.header("Saberes y P. Científico")
   st.write(df_prueba)

with tab3:
   st.header("Ética, Nat. y Sociedades")
   st.write(df_prueba)



#st.write(df_prueba)


#Creamos una copia del DF calificado completo, sin ningún filtro. Si se quisiera agregar filtros aquí podría ser la oportunidad
df_calificado_analisis = df_calificado.copy()

#Creamos un DF vacío para guardar los puros datos numéricos que vamos a requerir
df_grafica_1 = pd.DataFrame()

#Establecemos la división del número de reactivos por campo formativo para sacar el promedio por registro.
df_grafica_1['Porcentaje Aciertos Lenguaje'] = (df_calificado_analisis['Aciertos Lenguaje'] / 4) * 100
df_grafica_1['Porcentaje Aciertos Saberes y P. Científico'] = (df_calificado_analisis['Aciertos Saberes y P. Científico'] / 4) * 100
df_grafica_1['Porcentaje Aciertos Ética, Nat. y Sociedad'] = (df_calificado_analisis['Aciertos Ética, Nat. y Sociedad'] / 2) * 100

# Graficar los porcentajes de aciertos
#fig, ax = plt.subplots(figsize=(10, 6))
#sns.barplot(x=['Lenguaje', 'Saberes y P. Científico', 'Ética, Nat. y Sociedad'],
           # y=[df_grafica_1['Porcentaje Aciertos Lenguaje'].mean(), 
              # df_grafica_1['Porcentaje Aciertos Saberes y P. Científico'].mean(), 
               #df_grafica_1['Porcentaje Aciertos Ética, Nat. y Sociedad'].mean()],
           # ax=ax)
#ax.set_title('Porcentaje de Aciertos por Campo Formativo')
#ax.set_xlabel('Campos Formativos')
#ax.set_ylabel('Porcentaje de Aciertos (%)')

# Agregar etiquetas de datos a las barras
#for i in range(len(ax.patches)):
    #ax.text(ax.patches[i].get_x() + ax.patches[i].get_width()/2., ax.patches[i].get_height(),
            #f"{ax.patches[i].get_height():.2f}%", ha='center', va='bottom')

# Mostrar la gráfica en Streamlit
#st.pyplot(fig)


tab4, tab5, tab6 = st.tabs(["Aciertos", "Errores", "No contestadas"])
with tab4:
   st.header("Aciertos")
   #st.pyplot(fig)

with tab5:
   st.header("Errores")
   #st.pyplot(fig)

with tab6:
   st.header("No contestadas")
   #st.pyplot(fig)
