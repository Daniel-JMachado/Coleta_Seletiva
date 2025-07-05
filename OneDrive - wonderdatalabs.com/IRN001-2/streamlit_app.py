"""
Coleta Seletiva Conectada - Aplicativo Principal
POC para Prefeitura de Itajubá

Este é o ponto de entrada do aplicativo que conecta catadores de materiais 
recicláveis e moradores, facilitando o processo de coleta seletiva.
"""

import streamlit as st
import os
import sys
import importlib.util

# Função para importar um módulo a partir do caminho completo
def import_py_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível importar o módulo {module_name} do arquivo {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Caminhos dos módulos - ajustados para a estrutura do projeto
base_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(base_dir, "OneDrive - wonderdatalabs.com", "IRN001-2", "app")

login_module = import_py_file("login", os.path.join(app_dir, "pages", "login.py"))
morador_module = import_py_file("morador", os.path.join(app_dir, "pages", "morador.py"))
catador_module = import_py_file("catador", os.path.join(app_dir, "pages", "catador.py"))
admin_module = import_py_file("admin", os.path.join(app_dir, "pages", "admin.py"))
auth_module = import_py_file("auth", os.path.join(app_dir, "utils", "auth.py"))

# Atribui as funções necessárias
render_login_page = login_module.render_login_page
render_morador_page = morador_module.render_morador_page
render_catador_page = catador_module.render_catador_page
render_admin_page = admin_module.render_admin_page
check_authentication = getattr(auth_module, "check_authentication", None)
logout = auth_module.logout
load_session = getattr(auth_module, "load_session", None)

# Configuração da página
st.set_page_config(
    page_title="Coleta Seletiva Conectada - Itajubá",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carrega CSS
def load_css():
    try:
        css_path = os.path.join(app_dir, "css", "style.css")
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Erro ao carregar CSS: {e}. A estilização padrão será usada.")

def main():
    """Função principal que controla o fluxo da aplicação."""
    try:
        load_css()
    except:
        st.warning("Arquivo CSS não encontrado. A estilização padrão será usada.")
    
    # Inicializa o estado da sessão se não existir
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_type = None
        st.session_state.user_data = None
        
        # Tenta carregar uma sessão persistente anterior
        if load_session:
            load_session()
    
    # Não exibe a sidebar na tela de login
    if not st.session_state.authenticated:
        render_login_page()
    else:
        # Barra lateral com opções
        with st.sidebar:
            # Verifica se o arquivo JPG existe e exibe-o
            logo_path = os.path.join(app_dir, "assets", "logo.jpg")
            
            if os.path.exists(logo_path):
                # Função para converter imagem para base64
                def get_base64_image(image_path):
                    import base64
                    with open(image_path, "rb") as img_file:
                        return base64.b64encode(img_file.read()).decode('utf-8')
                
                # Exibe a imagem JPG como base64
                st.markdown(f"""<div style="text-align: center; margin-bottom: 1.5rem;">
                            <img src="data:image/jpeg;base64,{get_base64_image(logo_path)}" 
                                 style="max-width: 100px; height: auto; border-radius: 6px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);">
                            </div>""", unsafe_allow_html=True)
            else:
                # Fallback para o emoji de reciclagem
                st.markdown("""
                <div style="text-align: center; margin-bottom: 1.5rem;">
                    <span style="font-size: 4rem; color: #2e8b57;">♻️</span>
                </div>
                """, unsafe_allow_html=True)
                
            st.title("Coleta Seletiva Conectada")
            
            # Mostra informação do usuário logado
            user_icons = {
                "morador": "🏠",
                "catador": "♻️",
                "admin": "🔧"
            }
            icon = user_icons.get(st.session_state.user_type or "unknown", "👤")
            
            user_name = st.session_state.user_data.get('nome', 'Usuário') if st.session_state.user_data else 'Usuário'
            st.success(f"{icon} Olá, {user_name}!")
        
        # Renderiza a página de acordo com o tipo de usuário
        if st.session_state.user_type == "morador":
            render_morador_page(st.session_state.user_data)
        elif st.session_state.user_type == "catador":
            render_catador_page(st.session_state.user_data)
        elif st.session_state.user_type == "admin":
            render_admin_page(st.session_state.user_data)
        else:
            st.error("Tipo de usuário não reconhecido!")
            logout()
            st.rerun()

if __name__ == "__main__":
    main()
