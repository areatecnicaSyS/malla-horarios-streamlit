import streamlit as st
import pandas as pd
import numpy as np
import datetime
import io

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Gestión de Malla de Horarios",
    page_icon="📅",
    layout="wide"
)

# ---------------------------------------------------------
# SISTEMA DE AUTENTICACIÓN (CONTRASEÑA)
# ---------------------------------------------------------
# Puedes cambiar la contraseña aquí abajo por la que prefieras
PASSWORD_CORRECTA = "1234" 

def verificar_password():
    """Función para validar la contraseña de acceso"""
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        # Contenedor centrado para el login
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("## 🔐 Acceso Restringido")
            st.markdown("Por favor, ingresa la contraseña para acceder al generador de horarios.")
            
            password_input = st.text_input("Contraseña", type="password", placeholder="Ingresa tu clave...")
            
            if st.button("Ingresar", type="primary", use_container_width=True):
                if password_input == PASSWORD_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta. Inténtalo de nuevo.")
        return False
    return True

# Si no está autenticado, detener la ejecución aquí
if not verificar_password():
    st.stop()

# ---------------------------------------------------------
# LOGOTIPO Y ENCABEZADO (Una vez superado el login)
# ---------------------------------------------------------
# O puedes usar una URL pública de imagen, ej: "https://tu-sitio.com/logo.png"
# Si prefieres subirlo localmente, asegúrate de colocar el archivo de tu logo en la misma carpeta.
LOGO_PATH = "logo.png"  # Cambia esto por la ruta de tu logo (ej. "logo.png" o "logo.jpg")

col_logo, col_titulo = st.columns([1, 5])

with col_logo:
    try:
        # Intenta mostrar la imagen si existe en la carpeta del proyecto
        st.image(LOGO_PATH, width=120)
    except:
        # Si no encuentra la imagen, muestra un icono por defecto
        st.markdown("### 🏢 [Logo]")

with col_titulo:
    st.title("Generador Automático de Malla de Horarios")
    st.markdown("Área Técnica Servicios y Soluciones Tecnológicas — Gestión de Personal y Turnos")

st.divider()

# ---------------------------------------------------------
# INICIALIZACIÓN DEL SESSION STATE
# ---------------------------------------------------------
if "personal" not in st.session_state:
    st.session_state.personal = ["Juan Pérez", "María Rodríguez", "Carlos Gómez", "Ana Martínez"]

if "malla_semanal" not in st.session_state:
    st.session_state.malla_semanal = {}

# ---------------------------------------------------------
# BARRA LATERAL (SIDEBAR): CONFIGURACIÓN
# ---------------------------------------------------------
st.sidebar.header("⚙️ 1. Gestión de Personal")

# Opción para cerrar sesión en la barra lateral
if st.sidebar.button("🔒 Cerrar Sesión", use_container_width=True):
    st.session_state.autenticado = False
    st.rerun()

st.sidebar.divider()

# Agregar nueva persona
col_input, col_btn = st.sidebar.columns([3, 1])
nuevo_nombre = col_input.text_input("Nombre de colaborador", placeholder="Ej. Luisa Ríos", label_visibility="collapsed")
if col_btn.button("➕", help="Agregar colaborador"):
    if nuevo_nombre.strip():
        if nuevo_nombre.strip() not in st.session_state.personal:
            st.session_state.personal.append(nuevo_nombre.strip())
            st.sidebar.success(f"Agregado: {nuevo_nombre.strip()}")
            st.rerun()
        else:
            st.sidebar.warning("Esa persona ya está en la lista.")

# Lista de personal actual con opción de eliminar
st.sidebar.markdown("**Lista de Colaboradores:**")
for index, p in enumerate(st.session_state.personal):
    col_p_name, col_p_del = st.sidebar.columns([4, 1])
    col_p_name.caption(f"• {p}")
    if col_p_del.button("❌", key=f"del_{index}"):
        st.session_state.personal.pop(index)
        st.rerun()

st.sidebar.divider()

st.sidebar.header("📆 2. Lapso de Tiempo")
fecha_hoy = datetime.date.today()
fecha_inicio = st.sidebar.date_input("Fecha de Inicio", fecha_hoy)
fecha_fin = st.sidebar.date_input("Fecha de Fin", fecha_hoy + datetime.timedelta(days=27))

if fecha_fin < fecha_inicio:
    st.sidebar.error("Error: La fecha de fin debe ser posterior a la fecha de inicio.")

st.sidebar.divider()

st.sidebar.header("🕒 3. Bloques Horarios / Turnos")
turnos_input = st.sidebar.text_area(
    "Turnos disponibles (uno por línea)",
    value="Mañana (07:00 - 15:00)\nTarde (15:00 - 23:00)\nNoche (23:00 - 07:00)",
    height=100
)
turnos_lista = [t.strip() for t in turnos_input.split("\n") if t.strip()]

# ---------------------------------------------------------
# LÓGICA DE GENERACIÓN DE HORARIOS
# ---------------------------------------------------------
st.sidebar.divider()
if st.sidebar.button("⚡ Generar Malla Automática", type="primary", use_container_width=True):
    if not st.session_state.personal:
        st.error("Por favor agrega al menos una persona en el personal.")
    elif not turnos_lista:
        st.error("Por favor ingresa al menos un turno disponible.")
    elif fecha_fin < fecha_inicio:
        st.error("Rango de fechas inválido.")
    else:
        rango_dias = pd.date_range(start=fecha_inicio, end=fecha_fin)
        
        semanas_dict = {}
        for dia in rango_dias:
            num_semana = dia.isocalendar()[1]
            anio = dia.year
            clave_semana = f"Semana {num_semana} ({anio})"
            
            if clave_semana not in semanas_dict:
                semanas_dict[clave_semana] = []
            semanas_dict[clave_semana].append(dia)
            
        malla_generada = {}
        
        personal_list = list(st.session_state.personal)
        idx_rotacion = 0
        opciones_asignacion = turnos_lista + ["Descanso"]

        for semana, lista_dias in semanas_dict.items():
            dias_headers = [d.strftime("%A %d/%m").capitalize() for d in lista_dias]
            
            matriz = []
            for i, p in enumerate(personal_list):
                fila_persona = []
                for d_idx, dia_obj in enumerate(lista_dias):
                    turno_asignado = opciones_asignacion[(idx_rotacion + i + d_idx) % len(opciones_asignacion)]
                    fila_persona.append(turno_asignado)
                matriz.append(fila_persona)
                
            idx_rotacion += 1
            df_semana = pd.DataFrame(matriz, index=personal_list, columns=dias_headers)
            malla_generada[semana] = df_semana

        st.session_state.malla_semanal = malla_generada
        st.success("¡Malla de horarios generada exitosamente!")

# ---------------------------------------------------------
# VISUALIZACIÓN Y EDICIÓN DE RESULTADOS
# ---------------------------------------------------------
if st.session_state.malla_semanal:
    st.subheader("🗓️ Malla de Horarios por Semanas")
    
    tabs = st.tabs(list(st.session_state.malla_semanal.keys()))
    
    for i, (semana_nombre, df_sem) in enumerate(st.session_state.malla_semanal.items()):
        with tabs[i]:
            st.markdown(f"#### 📌 Horarios de la **{semana_nombre}**")
            st.caption("Puedes editar directamente cualquier celda si necesitas hacer un cambio puntual.")
            
            df_editado = st.data_editor(
                df_sem,
                use_container_width=True,
                key=f"editor_{semana_nombre}"
            )
            st.session_state.malla_semanal[semana_nombre] = df_editado

    st.divider()
    
    # ---------------------------------------------------------
    # DESCARGA DE RESULTADOS (EXCEL Y CSV)
    # ---------------------------------------------------------
    st.subheader("📥 Exportar Malla Completa")
    col_dl1, col_dl2 = st.columns(2)
    
    output_excel = io.BytesIO()
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        for sem_name, df_data in st.session_state.malla_semanal.items():
            sheet_title = sem_name.replace(" (", "_").replace(")", "")
            df_data.to_excel(writer, sheet_name=sheet_title)
            
    excel_data = output_excel.getvalue()
    
    col_dl1.download_button(
        label="📊 Descargar en Excel (.xlsx)",
        data=excel_data,
        file_name=f"malla_horarios_{fecha_inicio}_a_{fecha_fin}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    lista_dfs = []
    for sem_name, df_data in st.session_state.malla_semanal.items():
        df_temp = df_data.copy()
        df_temp.insert(0, "Semana", sem_name)
        lista_dfs.append(df_temp)
        
    df_consolidado = pd.concat(lista_dfs)
    csv_data = df_consolidado.to_csv().encode('utf-8')
    
    col_dl2.download_button(
        label="📄 Descargar Consolidado CSV",
        data=csv_data,
        file_name=f"malla_horarios_{fecha_inicio}_a_{fecha_fin}.csv",
        mime="text/csv",
        use_container_width=True
    )

else:
    st.info("👈 Configura el personal, el lapso de tiempo y presiona **'⚡ Generar Malla Automática'** en la barra lateral para empezar.")