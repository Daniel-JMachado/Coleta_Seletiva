"""
Coleta Seletiva Conectada - Aplicativo Principal
POC para Prefeitura de Itajubá

Este é o ponto de entrada do aplicativo que conecta catadores de materiais 
recicláveis e moradores, facilitando o processo de coleta seletiva.
"""

import streamlit as st
import os
import sys
import base64

# Adiciona o diretório app ao path do Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Imports das páginas
from pages.login import render_login_page
from pages.morador import render_morador_page
from pages.catador import render_catador_page
from pages.admin import render_admin_page
from utils.auth import check_authentication, logout, load_session

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
        css_path = os.path.join(os.path.dirname(__file__), "app", "css", "style.css")
        if os.path.exists(css_path):
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
        try:
            load_session()
        except:
            pass
    
    # Não exibe a sidebar na tela de login
    if not st.session_state.authenticated:
        render_login_page()
    else:
        # Barra lateral com opções
        with st.sidebar:
            # Verifica se o arquivo JPG existe e exibe-o
            logo_path = os.path.join(os.path.dirname(__file__), "app", "assets", "logo.jpg")
            
            if os.path.exists(logo_path):
                # Função para converter imagem para base64
                def get_base64_image(image_path):
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
        try:
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
        except Exception as e:
            st.error(f"Erro ao carregar página: {e}")
            st.info("Tente fazer login novamente.")
            logout()
            st.rerun()

if __name__ == "__main__":
    main() 