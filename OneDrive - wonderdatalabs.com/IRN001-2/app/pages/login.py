"""
Página de login do sistema Coleta Seletiva Conectada

Este módulo contém a implementação da página de login unificada para todos os tipos
de usuários (moradores, catadores e administradores).
"""

import streamlit as st
import os
from app.utils.auth import login

class LoginPage:
    """
    Classe responsável pela página de login do sistema.
    Implementa a separação entre lógica e layout.
    """
    def __init__(self):
        """Inicializa a página de login e carrega o CSS específico"""
        self.load_css()
        # Esconder a barra lateral na página de login
        self.hide_sidebar()
    
    def load_css(self):
        """Carrega o CSS específico da página de login"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            css_path = os.path.join(base_dir, "app", "css", "login.css")
            with open(css_path, "r", encoding="utf-8") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Erro ao carregar CSS de login: {e}")
    
    def hide_sidebar(self):
        """Esconde a barra lateral na página de login"""
        hide_streamlit_style = """
            <style>
                div[data-testid="stSidebar"] {display: none !important;}
                div[data-testid="collapsedControl"] {display: none !important;}
                .main .block-container {max-width: 100% !important; padding: 1rem !important;}
                section[data-testid="stSidebarUserContent"] {display: none !important;}
                button[kind="header"] {display: none !important;}
            </style>
        """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    def show_logo(self):
        """Renderiza o logo centralizado"""
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                "app", "assets", "logo.jpg")
        
        if os.path.exists(logo_path):
            st.markdown(f"""<div class="logo-container">
                           <img src="data:image/jpeg;base64,{self.get_base64_image(logo_path)}" 
                                class="logo-img" 
                                style="max-width: 200px; height: auto; margin-bottom: 0;"
                                alt="Logo Coleta Seletiva Conectada"/>
                           </div>""", unsafe_allow_html=True)
        else:
            # Fallback para um ícone simples caso a imagem não seja encontrada
            st.markdown("""
            <div class="logo-container">
                <span style="font-size: 0.8rem; color: #2e8b57; margin-bottom: 0;">♻️</span>
            </div>
            """, unsafe_allow_html=True)
    
    def get_base64_image(self, image_path):
        """Converte uma imagem para base64 para exibição inline no HTML"""
        import base64
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    
    def show_login_form(self):
        """Renderiza o formulário de login centralizado"""

        st.markdown("<h3 class='login-header'>Acesso ao Sistema</h3>", unsafe_allow_html=True)
        
        # Formulário de login
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email", placeholder="seu.email@exemplo.com")
            password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            
            # Melhorando a apresentação do tipo de usuário
            user_types = {
                "morador": "🏠 Morador",
                "catador": "♻️ Catador",
                "admin": "🔧 Administrador"
            }
            
            user_type = st.selectbox(
                "Tipo de Usuário", 
                options=list(user_types.keys()), 
                format_func=lambda x: user_types[x]
            )
            
            submitted = st.form_submit_button("Entrar", use_container_width=True)
            
            if submitted:
                self.process_login(email, password, user_type)
        
        # Informações adicionais
        st.markdown("""
        <p class="login-info-text">Não possui uma conta? Entre em contato com a administração.</p>
        <p class="login-contact-text"><small>Em caso de dificuldades, contate a Secretaria de Meio Ambiente: (35) 3629-1234.</small></p>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    def process_login(self, email, password, user_type):
        """
        Processa a tentativa de login
        
        Args:
            email (str): Email do usuário
            password (str): Senha do usuário
            user_type (str): Tipo de usuário (morador, catador ou admin)
        """
        if not email or not password:
            st.error("Por favor, preencha todos os campos.")
        else:
            # Tenta fazer login
            if login(email, password, user_type):
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Credenciais inválidas. Verifique seu email, senha e tipo de usuário.")
    
    def show_footer(self):
        """Renderiza o rodapé da página"""
        st.markdown("""
        <div class="login-footer">
            <p>© 2025 - Prefeitura Municipal de Itajubá - Secretaria de Meio Ambiente</p>
            <p><small>Desenvolvido com ❤️ para um futuro mais sustentável</small></p>
        </div>
        """, unsafe_allow_html=True)
    
    def render(self):
        """Renderiza a página completa de login com layout compacto"""
        # Esconde a barra lateral
        self.hide_sidebar()
        
        # Adiciona CSS personalizado para ajustar o layout
        st.markdown("""
        <style>
        div.block-container {
            padding-top: 0.2rem;
            padding-bottom: 0.2rem;
        }
        section[data-testid="stVerticalBlock"] {
            gap: 0 !important;
        }
        div[data-testid="stVerticalBlock"] > div {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
            padding-top: 0 !important;
        }
        div[data-testid="stExpander"] {
            display: none !important;
        }
        footer {
            display: none !important;
        }
        /* Garantir espaçamento mínimo entre logo e título */
        .logo-container + * {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Cria uma grade de 3 colunas para centralizar o conteúdo
        col1, col2, col3 = st.columns([1, 3, 1])
        
        # Todo o conteúdo vai na coluna central (col2)
        with col2:
            # Cria o container centralizado
            st.markdown("<div class='login-centered'>", unsafe_allow_html=True)
            
            # Logo centralizado
            self.show_logo()
            
            # Título e subtítulo - sem margem superior
            st.markdown("<h1 class='main-header' style='margin-top: 0; padding: 0;'>Coleta Seletiva Conectada</h1>", unsafe_allow_html=True)
            
            # Formulário de login centralizado
            self.show_login_form()
            
            # Rodapé
            self.show_footer()
            
            st.markdown("</div>", unsafe_allow_html=True)


def render_login_page():
    """
    Função para renderizar a página de login.
    Mantida para compatibilidade com o restante do sistema.
    """
    login_page = LoginPage()
    login_page.render()
