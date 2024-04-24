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

st.markdown("<h1 style='text-align: center; color: #800226; '>¡P R E S E N T A C I Ó N!</h1>", unsafe_allow_html=True)

# st.header("¡B i e n v e n i d o!")

st.subheader("Bienvenido")

st.markdown("<p style='text-align: justify;'>El Sistema Calificador y de Evaluación (SISE) es un sistema que tiene la funcionalidad de calificar las respuestas de las y los estudiantes participantes; mostrar los resultados por alumno, grupo, escuela; identificar los posibles casos de empate y categorizar los Contenidos Curriculares y Proceso de Desarrollo (PDA), del Plan de estudio 2022, evaluados de acuerdo a una prioridad baja, media y alta a través de un mapeo de aprendizajes. Lo anterior con la finalidad de generar un Programa de Reforzamiento del Aprendizaje a corto, mediano y largo plazo que contribuya a una educación de excelencia, priorizando el máximo logro de aprendizajes de niñas, niños y adolescentes (NNA).",unsafe_allow_html=True)

st.markdown("<p style='text-align: justify;'>Para conocer todas sus funcionalidades y beneficios te invitamos a consultar en el menú del lado izquierdo la opción “Guía de usuario”",unsafe_allow_html=True)

st.markdown("<p style='text-align: justify;'><strong><em>¡Esperamos que esta herramienta te sea de gran utilidad!.</em></strong></p>", unsafe_allow_html=True)

