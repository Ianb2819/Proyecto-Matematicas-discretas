import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import textwrap
# --- Configuración de la Página ---
st.set_page_config(
    page_title="Optimizador de Horarios (Grafos)",
    page_icon="🎨",
    layout="wide"
)


st.title("👨‍💻 Optimizador de Horarios con Grafos")
st.write("""
Esta app demuestra cómo el **coloreo de grafos** puede resolver un problema de asignación de horarios.
1.  Añade las **materias** (vértices).
2.  Define los **conflictos** (aristas).
3.  ¡Calcula las **franjas horarias** (colores) necesarias!
""")

# --- Inicializar el estado de la sesión 
if 'materias' not in st.session_state:
    st.session_state.materias = []
if 'conflictos' not in st.session_state:
    st.session_state.conflictos = []

# --- Columnas para la Interfaz 
col1, col2 = st.columns([1, 1.5])  

# === COLUMNA 1: INPUTS DEL USUARIO ===
with col1:
    st.header("1. Añadir Materias (Vértices)")
    
    # Formulario para añadir materia
    with st.form("form_materia", clear_on_submit=True):
        nueva_materia = st.text_input("Nombre de la materia:", placeholder="Ej: Cálculo")
        submitted = st.form_submit_button("Añadir Materia")
        
        if submitted and nueva_materia:
            if nueva_materia not in st.session_state.materias:
                st.session_state.materias.append(nueva_materia)
                st.success(f"¡Se añadió '{nueva_materia}'!")
            else:
                st.warning(f"'{nueva_materia}' ya está en la lista.")
    
    # Mostrar materias actuales y botón para limpiar
    if st.session_state.materias:
        st.write("**Materias Actuales:**")
        st.write(f"_{', '.join(st.session_state.materias)}_")
        if st.button("Limpiar todas las materias"):
            st.session_state.materias = []
            st.session_state.conflictos = []
            st.rerun()

    st.divider()

    st.header("2. Definir Conflictos (Aristas)")
    
    # Solo mostrar si hay al menos 2 materias
    if len(st.session_state.materias) >= 2:
        
        # Usamos un formulario para que el usuario elija AMBOS y luego envíe
        with st.form("form_conflicto_v2", clear_on_submit=True):
            
            # Lista de opciones es la misma para ambos
            lista_opciones = st.session_state.materias
            
            materia_1 = st.selectbox(
                "Materia 1:",
                options=lista_opciones,
                index=None, # Para que muestre el placeholder
                placeholder="Selecciona la primera materia"
            )
            
            materia_2 = st.selectbox(
                "Materia 2:",
                options=lista_opciones,
                index=None, # Para que muestre el placeholder
                placeholder="Selecciona la segunda materia"
            )
            
            submitted_conflicto = st.form_submit_button("Añadir Conflicto")
            
            # --- Lógica de Validación ---
            if submitted_conflicto:
                # 1. Validar que se seleccionaron dos materias
                if not materia_1 or not materia_2:
                    st.error("Por favor, selecciona 2 materias para crear un conflicto.")
                
                # 2. Validar que no son la misma materia
                elif materia_1 == materia_2:
                    st.error("Una materia no puede tener conflicto consigo misma. Selecciona dos materias diferentes.")
                
                # 3. Si todo está bien, crear el conflicto
                else:
                    conflicto = tuple(sorted([materia_1, materia_2]))
                    
                    if conflicto not in st.session_state.conflictos:
                        st.session_state.conflictos.append(conflicto)
                        st.success(f"Conflicto añadido: {conflicto[0]} ↔ {conflicto[1]}")
                    else:
                        st.warning("Ese conflicto ya existe.")

    else:
        st.info("Añade al menos 2 materias para poder crear conflictos.")
        
    # Mostrar conflictos actuales 
    if st.session_state.conflictos:
        st.write("**Conflictos Actuales:**")
        st.write(st.session_state.conflictos)
        if st.button("Limpiar todos los conflictos"):
            st.session_state.conflictos = []
            st.rerun()

# === COLUMNA 2: RESULTADOS Y VISUALIZACIÓN ===
with col2:
    st.header("3. Resultados del Horario")

    # Botón principal para calcular
    if st.button("¡Generar Horario!", type="primary", use_container_width=True):
        
        if not st.session_state.materias:
            st.error("No hay materias para procesar.")
        
        else:
            # --- Lógica de Grafos ---
            G = nx.Graph()
            G.add_nodes_from(st.session_state.materias)
            G.add_edges_from(st.session_state.conflictos)
            
            if not G.edges:
                st.warning("No se definieron conflictos. Todas las clases pueden ir en la misma franja.")
            
            # Colorear el grafo
            try:
                coloring_dict = nx.greedy_color(G, strategy="largest_first")
                
                # --- Procesar Resultados ---
                num_colores = len(set(coloring_dict.values()))
                st.success(f"¡Hecho! Se necesita un mínimo de **{num_colores}** franjas horarias.")
                
                # --- (INICIO) CÓDIGO DE LA TABLA QUE FALTABA ---
                schedule = {}
                for materia, color in coloring_dict.items():
                    franja = f"Franja Horaria {color + 1}"
                    if franja not in schedule:
                        schedule[franja] = []
                    schedule[franja].append(materia)
                
                # Mostrar el horario en un DataFrame bonito
                st.subheader("Propuesta de Horario:")
                df = pd.DataFrame.from_dict(schedule, orient='index').T
                df = df.reindex(sorted(df.columns), axis=1) # Ordenar Franja 1, Franja 2...
                st.dataframe(df.fillna(""), use_container_width=True)
                # --- (FIN) CÓDIGO DE LA TABLA QUE FALTABA ---


                # --- Visualización del Grafo (VERSIÓN 3.0 "ESTÉTICA CON MÁRGENES") ---
                st.subheader("Grafo de Conflictos Coloreado:")
                
                # 1. Etiquetas envueltas (para que quepa el texto largo)
                wrapped_labels = {
                    node: "\n".join(textwrap.wrap(node, 
                                                width=11,  # Un poco más ancho (11 caracteres)
                                                break_long_words=False, 
                                                replace_whitespace=False)) 
                    for node in G.nodes()
                }
                
                # 2. Colores del dict
                node_colors = [coloring_dict[node] for node in G.nodes()]
                
                # 3. Lienzo un poco más grande
                fig, ax = plt.subplots(figsize=(12, 9)) 
                
                # 4. Layout orgánico
                pos = nx.kamada_kawai_layout(G) 
                
                # 5. Paleta de colores pastel
                cmap = plt.cm.get_cmap('Set2') 
                
                nx.draw(
                    G,
                    pos,
                    labels=wrapped_labels,
                    with_labels=True,
                    node_color=node_colors,     
                    cmap=cmap,                  
                    node_size=4000,             
                    edgecolors='black',         
                    linewidths=0.5,             
                    font_size=10,               
                    font_weight="bold",
                    font_color="black",         
                    edge_color="#AAAAAA",       
                    style="dashed",             
                    ax=ax
                )
                
                # 6. Limpiar el fondo
                fig.patch.set_facecolor('#FFFFFF') # Fondo de la app
                ax.set_facecolor('#FFFFFF') # Fondo del gráfico
                ax.set_title("Grafo de Materias y Conflictos", pad=20, fontsize=16) 
                
                # 7. Añadir márgenes
                ax.margins(0.20) 
                
                st.pyplot(fig)

            except Exception as e:
                st.error(f"Error al procesar el grafo: {e}")