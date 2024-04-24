import streamlit as st

# Agrega un texto semi-transparente como marca de agua
st.markdown(
    """
    <style>
        .watermark {
            position: fixed;
            top: 37%;
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

st.markdown("<h1 style='text-align: center; color: #800226; '>GUÍA DE USUARIO</h1>", unsafe_allow_html=True)


"""
*Captura de respuestas por estudiante, por grupo y por escuela.*

Ponemos a tu disposición un archivo electrónico en excel, denominado "OCI2024_Escuela.xlsm", en el cual capturarás las respuestas correctas de tu instrumento, los datos de la escuela, del grupo y del estudiante de sexto grado participante; así como cada una de las respuestas dadas por cada uno de ellos. 

*Para calificar las respuestas*

En la pestaña “Calificador”, ubicada en el menú de la izquierda, deberás adjuntar el archivo electrónico en excel, con la captura de datos y de las respuestas de cada alumno por grupo y escuela. 

Una vez que se haya adjuntado, SISE te mostrará la siguiente información: 

 1)	El nombre del participante con mayor número de aciertos; así como los datos de identificación con los cuales iniciaste la captura. 
 2)	Un botón denominado “Ver resultados de escuelas públicas o particulares”. Al pusarlo, se despliega una tabla con los datos de la escuela, del grupo, del docente, del estudiante, el número de aciertos totales en la prueba y el desglose de aciertos por Campo formativo. Estos resultados se organizan de mayor a menor número de aciertos. Si hubiese empate en esta pantalla se mostrarán dichos resultados.

Es importante señalar que, los resultados no se guardan en el sistema por razones de confidencialidad. Por ello, los resultados se despliegan en pantalla y permanecen visibles siempre y cuando no se actualice la página. 

Considerando lo anterior, se pone a tu disposición el botón *“Descargar archivo de escuelas públicas o privadas”*. Al pulsarlo, se muestra la liga con el nombre *“Haz clic para descargar los resultados en Excel”*. Una vez realizada esta acción, el archivo solicitado se aloja en la carpeta *“Descargas”* de tu equipo de cómputo. 

"""
