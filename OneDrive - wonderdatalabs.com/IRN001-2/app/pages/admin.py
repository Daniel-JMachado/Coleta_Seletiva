"""
Página do Administrador do sistema Coleta Seletiva Conectada

Este módulo contém a implementação da página do administrador (prefeitura), com funcionalidades para
cadastrar novos usuários, visualizar estatísticas, gerenciar usuários e adicionar conteúdo educativo.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import json
from PIL import Image
import io
# Importações do Plotly com tratamento de erro
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    print("Plotly não está disponível. Gráficos serão desabilitados.")
    px = None
    go = None
    PLOTLY_AVAILABLE = False
import hashlib

from app.utils.database import (
    load_users, load_coletas, save_user, update_user, delete_user,
    load_conteudo_educativo, save_conteudo_educativo,
    add_artigo, add_dica, save_notificacao, save_profile_photo
)
from app.utils.auth import register_user

class AdminPage:
    """
    Classe responsável pela página do administrador do sistema.
    Implementa a separação entre lógica e layout.
    """
    
    def __init__(self, user_data):
        """
        Inicializa a página do administrador
        
        Args:
            user_data (dict): Dados do usuário administrador logado
        """
        self.user_data = user_data
        self.load_css()
        
    def load_css(self):
        """Carrega o CSS específico da página do administrador"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # CSS do administrador
            css_path = os.path.join(base_dir, "app", "css", "admin.css")
            with open(css_path, 'r', encoding='utf-8') as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
                
            # CSS do perfil (para upload de foto)
            perfil_css_path = os.path.join(base_dir, "app", "css", "perfil.css")
            with open(perfil_css_path, 'r', encoding='utf-8') as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Erro ao carregar CSS do administrador: {e}")
            # Estilo fallback
            st.markdown("""
                <style>
                .admin-container { padding: 1rem; }
                .admin-card { background-color: #f8f9fa; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                .admin-stats { display: flex; flex-wrap: wrap; gap: 10px; }
                </style>
            """, unsafe_allow_html=True)
    
    def render(self):
        """Renderiza a página principal do administrador"""
        st.title("Painel do Administrador")
        
        # Menu de navegação lateral
        with st.sidebar:
            selected_option = st.radio(
                "Menu",
                ["Dashboard", "Cadastrar Usuário", "Gerenciar Usuários", "Estatísticas", "Conteúdo Educativo"]
            )
            
            # Separador e botão de logout
            st.markdown("---")
            if st.button("🚪 Sair do Sistema", type="primary", use_container_width=True):
                from app.utils.auth import logout
                logout()
                st.rerun()
        
        # Mostra o conteúdo de acordo com a opção selecionada
        if selected_option == "Dashboard":
            self.show_dashboard()
        elif selected_option == "Cadastrar Usuário":
            self.show_user_registration()
        elif selected_option == "Gerenciar Usuários":
            self.show_user_management()
        elif selected_option == "Estatísticas":
            self.show_statistics()
        elif selected_option == "Conteúdo Educativo":
            self.show_educational_content()
    
    def show_dashboard(self):
        """Exibe o dashboard principal com estatísticas e informações gerais"""
        st.header("Dashboard")
        
        # Carrega dados necessários
        users = load_users()
        coletas = load_coletas()
        
        # Estatísticas principais
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Uso de value_counts() para contagem mais eficiente
            tipo_counts = users['tipo'].value_counts()
            total_users = len(users)
            moradores = tipo_counts.get('morador', 0)
            catadores = tipo_counts.get('catador', 0)
            admins = tipo_counts.get('admin', 0)
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 25px; border-radius: 15px; color: white; 
                        box-shadow: 0 8px 32px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <h3 style="margin: 0 0 20px 0; font-size: 1.3rem; display: flex; align-items: center;">
                    👥 Usuários Cadastrados
                </h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; backdrop-filter: blur(10px);">
                        <div style="font-size: 2rem; font-weight: bold; margin-bottom: 5px;">{total_users}</div>
                        <div style="opacity: 0.9; font-size: 0.9rem;">Total de Usuários</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; backdrop-filter: blur(10px);">
                        <div style="font-size: 2rem; font-weight: bold; margin-bottom: 5px;">{moradores}</div>
                        <div style="opacity: 0.9; font-size: 0.9rem;">Moradores</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; backdrop-filter: blur(10px);">
                        <div style="font-size: 2rem; font-weight: bold; margin-bottom: 5px;">{catadores}</div>
                        <div style="opacity: 0.9; font-size: 0.9rem;">Catadores</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; backdrop-filter: blur(10px);">
                        <div style="font-size: 2rem; font-weight: bold; margin-bottom: 5px;">{admins}</div>
                        <div style="opacity: 0.9; font-size: 0.9rem;">Administradores</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_coletas = len(coletas)
            
            # Uso de value_counts() para contagem mais eficiente e tratamento de NaN
            if not coletas.empty and 'status' in coletas.columns:
                status_counts = coletas['status'].value_counts()
                agendadas = status_counts.get('agendada', 0)
                em_andamento = status_counts.get('em_andamento', 0) + status_counts.get('pendente', 0)  # Considerar pendente também
                concluidas = status_counts.get('realizada', 0) + status_counts.get('concluida', 0)  # Considerar os dois termos
            else:
                agendadas = 0
                em_andamento = 0
                concluidas = 0
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        padding: 25px; border-radius: 15px; color: white; 
                        box-shadow: 0 8px 32px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <h3 style="margin: 0 0 20px 0; font-size: 1.3rem; display: flex; align-items: center;">
                    📋 Coletas
                </h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; backdrop-filter: blur(10px);">
                        <div style="font-size: 2rem; font-weight: bold; margin-bottom: 5px;">{total_coletas}</div>
                        <div style="opacity: 0.9; font-size: 0.9rem;">Total de Coletas</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; backdrop-filter: blur(10px);">
                        <div style="font-size: 2rem; font-weight: bold; margin-bottom: 5px;">{agendadas}</div>
                        <div style="opacity: 0.9; font-size: 0.9rem;">Agendadas</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; backdrop-filter: blur(10px);">
                        <div style="font-size: 2rem; font-weight: bold; margin-bottom: 5px;">{em_andamento}</div>
                        <div style="opacity: 0.9; font-size: 0.9rem;">Em Andamento</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; backdrop-filter: blur(10px);">
                        <div style="font-size: 2rem; font-weight: bold; margin-bottom: 5px;">{concluidas}</div>
                        <div style="opacity: 0.9; font-size: 0.9rem;">Concluídas</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Cálculo de métricas de performance com tratamento de erros
            coletas_ultimos_7_dias = 0
            
            try:
                if not coletas.empty and 'data_solicitacao' in coletas.columns:
                    # Converter para datetime com tratamento de erros
                    coletas['data_solicitacao_dt'] = pd.to_datetime(coletas['data_solicitacao'], errors='coerce')
                    data_limite = pd.Timestamp(datetime.now() - timedelta(days=7))
                    coletas_ultimos_7_dias = len(coletas[coletas['data_solicitacao_dt'] > data_limite])
            except Exception as e:
                st.warning(f"Erro ao calcular coletas recentes: {e}")
                
            # Cálculo seguro de taxa de conclusão com tratamento para divisão por zero
            taxa_conclusao = 0
            if total_coletas > 0:
                taxa_conclusao = round((concluidas / total_coletas) * 100, 2)
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        padding: 25px; border-radius: 15px; color: white; 
                        box-shadow: 0 8px 32px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <h3 style="margin: 0 0 20px 0; font-size: 1.3rem; display: flex; align-items: center;">
                    📊 Performance
                </h3>
                <div style="display: grid; grid-template-columns: 1fr; gap: 15px;">
                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; backdrop-filter: blur(10px);">
                        <div style="font-size: 2rem; font-weight: bold; margin-bottom: 5px;">{coletas_ultimos_7_dias}</div>
                        <div style="opacity: 0.9; font-size: 0.9rem;">Coletas (7 dias)</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; backdrop-filter: blur(10px);">
                        <div style="font-size: 2rem; font-weight: bold; margin-bottom: 5px;">{taxa_conclusao}%</div>
                        <div style="opacity: 0.9; font-size: 0.9rem;">Taxa de Conclusão</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Gráficos
        st.subheader("Análise de Dados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de status das coletas com tratamento para dados vazios
            if not coletas.empty and 'status' in coletas.columns:
                try:
                    # Verificar se o módulo plotly está disponível
                    if not PLOTLY_AVAILABLE or px is None:
                        st.info("Gráficos não disponíveis. Biblioteca Plotly não instalada.")
                        # Mostrar dados em tabela como alternativa
                        status_counts = coletas['status'].value_counts().reset_index()
                        status_counts.columns = ['Status', 'Quantidade']
                        st.dataframe(status_counts, use_container_width=True)
                    else:
                        status_counts = coletas['status'].value_counts().reset_index()
                        status_counts.columns = ['Status', 'Quantidade']
                        
                        # Usar cores padrão se houver problemas com o esquema de cores
                        try:
                            fig = px.pie(
                                status_counts, 
                                values='Quantidade', 
                                names='Status', 
                                title='Status das Coletas',
                                color_discrete_sequence=px.colors.sequential.Viridis
                            )
                        except Exception:
                            # Fallback sem esquema de cores personalizado
                            fig = px.pie(
                                status_counts, 
                                values='Quantidade', 
                                names='Status', 
                                title='Status das Coletas'
                            )
                        
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Erro ao criar gráfico de status: {e}")
                    st.info("Não foi possível gerar o gráfico de status das coletas.")
            else:
                st.info("Não há dados de coletas para exibir no gráfico.")
        
        with col2:
            # Gráfico de usuários por tipo com tratamento de exceções
            try:
                # Verificar se o módulo plotly está disponível
                if not PLOTLY_AVAILABLE or px is None:
                    st.info("Gráficos não disponíveis. Biblioteca Plotly não instalada.")
                    # Mostrar dados em tabela como alternativa
                    user_types = users['tipo'].value_counts().reset_index()
                    user_types.columns = ['Tipo', 'Quantidade']
                    st.dataframe(user_types, use_container_width=True)
                else:
                    user_types = users['tipo'].value_counts().reset_index()
                    user_types.columns = ['Tipo', 'Quantidade']
                    
                    # Usar cores padrão se houver problemas com o esquema de cores
                    try:
                        fig = px.bar(
                            user_types,
                            x='Tipo',
                            y='Quantidade',
                            title='Usuários por Tipo',
                            color='Tipo',
                            color_discrete_sequence=px.colors.sequential.Plasma
                        )
                    except Exception:
                        # Fallback sem esquema de cores personalizado
                        fig = px.bar(
                            user_types,
                            x='Tipo',
                            y='Quantidade',
                            title='Usuários por Tipo',
                            color='Tipo'
                        )
                    
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao criar gráfico de usuários: {e}")
                st.info("Não foi possível gerar o gráfico de usuários por tipo.")
    
    def show_user_registration(self):
        """Exibe o formulário para cadastro de novos usuários"""
        st.header("Cadastrar Novo Usuário")
        
        with st.form("cadastro_usuario"):
            nome = st.text_input("Nome*", placeholder="Nome completo")
            email = st.text_input("Email*", placeholder="email@exemplo.com")
            
            col1, col2 = st.columns(2)
            with col1:
                tipo = st.selectbox("Tipo de Usuário*", options=["morador", "catador", "admin"])
            with col2:
                telefone = st.text_input("Telefone*", placeholder="(XX) XXXXX-XXXX")
            
            col3, col4 = st.columns(2)
            with col3:
                bairro = st.text_input("Bairro", placeholder="Nome do bairro")
            with col4:
                endereco = st.text_input("Endereço", placeholder="Rua, número")
            
            if tipo == "catador":
                areas_atuacao = st.text_input("Áreas de Atuação", 
                                             placeholder="Bairros onde atua, separados por vírgula")
            else:
                areas_atuacao = ""
            
            # Upload de foto de perfil
            st.markdown("<p>Foto de Perfil (JPG, PNG ou GIF)</p>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Foto de Perfil", type=["jpg", "jpeg", "png", "gif"], 
                                           label_visibility="collapsed")
            
            # Preview da imagem se foi carregada
            if uploaded_file is not None:
                try:
                    st.markdown("<div style='border-radius: 10px; overflow: hidden; width: 150px; margin-top: 10px;'>", unsafe_allow_html=True)
                    image = Image.open(uploaded_file)
                    
                    # Redimensionar a imagem para um tamanho razoável para preview
                    img_width, img_height = image.size
                    if img_width > img_height:
                        new_width = 150
                        new_height = int(img_height * (new_width / img_width))
                    else:
                        new_height = 150
                        new_width = int(img_width * (new_height / img_height))
                    
                    img_preview_resized = image.resize((new_width, new_height))
                    st.image(img_preview_resized, caption="Preview da foto", width=new_width)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Reset do buffer de leitura para uso posterior
                    uploaded_file.seek(0)
                except Exception as e:
                    st.error(f"Erro ao carregar preview: {str(e)}")
            
            senha = "123"  # Senha padrão conforme solicitado
            
            submit = st.form_submit_button("Cadastrar Usuário")
            
            if submit:
                if nome and email and tipo and telefone:
                    # Validação básica de email
                    if '@' not in email or '.' not in email:
                        st.error("Por favor, insira um email válido.")
                        return
                        
                    # Chamada para função de registro
                    try:
                        success, message = register_user(nome, email, senha, tipo, bairro, telefone, endereco)
                        if success:
                            # Se o usuário foi criado com sucesso e tem foto, salvar a foto
                            if uploaded_file is not None:
                                # Obter o ID do usuário recém-criado
                                users_df = load_users()
                                user_id = users_df[users_df['email'] == email]['id'].iloc[0]
                                success_photo, photo_path = save_profile_photo(user_id, uploaded_file)
                                if not success_photo:
                                    st.warning(f"Usuário cadastrado, mas houve um erro ao salvar a foto: {photo_path}")
                            
                            st.success("Usuário cadastrado com sucesso!")
                            
                            # Cria notificação para o novo usuário
                            try:
                                # Obter o ID do usuário recém-criado
                                users_df = load_users()
                                user_id = users_df[users_df['email'] == email]['id'].iloc[0]
                                notificacao = {
                                    'usuario_id': user_id,
                                    'tipo_usuario': tipo,  # Adiciona o tipo_usuario
                                    'titulo': 'Bem-vindo ao Sistema de Coleta Seletiva Conectada',
                                    'mensagem': f'Olá {nome}, seu cadastro foi realizado com sucesso. Sua senha padrão é "123". Recomendamos que altere sua senha no primeiro acesso.',
                                    'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'lida': False
                                }
                                save_notificacao(notificacao)
                            except Exception as e:
                                st.warning(f"Usuário cadastrado, mas houve um erro ao criar notificação: {str(e)}")
                        else:
                            st.error(f"Erro no cadastro: {message}")
                    except Exception as e:
                        st.error(f"Erro ao processar o cadastro: {str(e)}")
                else:
                    st.error("Por favor, preencha todos os campos obrigatórios.")
    
    def show_user_management(self):
        """Exibe a página de gerenciamento de usuários"""
        st.header("Gerenciar Usuários")
        
        # Carregar usuários
        users = load_users()
        
        if users is None or users.empty:
            st.warning("Nenhum usuário encontrado.")
            return
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            tipo_filtro = st.selectbox("Filtrar por tipo", ["Todos", "morador", "catador", "admin"])
        
        with col2:
            status_filtro = st.selectbox("Filtrar por status", ["Todos", "ativo", "inativo"])
        
        # Aplicar filtros
        filtered_users = users.copy()
        if tipo_filtro != "Todos":
            filtered_users = filtered_users[filtered_users['tipo'] == tipo_filtro]
        
        if status_filtro != "Todos":
            filtered_users = filtered_users[filtered_users['status'] == status_filtro]
        
        # Exibir usuários em formato de cards
        for idx, user in filtered_users.iterrows():
            with st.expander(f"{user['nome']} ({user['tipo']})"):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    # Verificar se o usuário tem foto de perfil
                    foto_perfil = user.get('foto_perfil', '')
                    # Converter para string para evitar problemas com tipos não string
                    if foto_perfil is None or not isinstance(foto_perfil, str):
                        foto_perfil = str(foto_perfil) if foto_perfil else ''
                    
                    # Normalizar o caminho (converter barras invertidas para barras normais)
                    foto_perfil = foto_perfil.strip().replace('\\', '/')
                    
                    # Verificar se a foto existe
                    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    full_img_path = os.path.join(base_path, foto_perfil) if foto_perfil else ""
                    
                    if foto_perfil and os.path.exists(full_img_path):
                        # Mostra a foto atual
                        img = Image.open(full_img_path)
                        st.image(img, caption="Foto atual", width=150)
                    else:
                        # Mostrar placeholder se não tiver foto
                        st.markdown("<div class='profile-photo-placeholder' style='width:150px;height:150px;border-radius:50%;display:flex;justify-content:center;align-items:center;font-size:2rem;color:#adb5bd;background-color:#f8f9fa;'>👤</div>", unsafe_allow_html=True)
                
                with col2:
                    # Exibir informações do usuário
                    st.write(f"**Email:** {user['email']}")
                    st.write(f"**Telefone:** {user['telefone']}")
                    st.write(f"**Endereço:** {user.get('endereco', 'N/A')}")
                    st.write(f"**Bairro:** {user.get('bairro', 'N/A')}")
                    st.write(f"**Tipo:** {user['tipo']}")
                    st.write(f"**Status:** {user['status']}")
                    
                    # Ações
                    if user['status'] == "ativo":
                        if st.button("Desativar Usuário", key=f"desativar_{user['id']}"):
                            try:
                                update_user(user['id'], {"status": "inativo"})
                                st.success("Usuário desativado com sucesso.")
                            except Exception as e:
                                st.error(f"Erro ao desativar usuário: {e}")
                    else:
                        if st.button("Ativar Usuário", key=f"ativar_{user['id']}"):
                            try:
                                update_user(user['id'], {"status": "ativo"})
                                st.success("Usuário ativado com sucesso.")
                            except Exception as e:
                                st.error(f"Erro ao ativar usuário: {e}")
        
        # Edição de usuário selecionado
        if not filtered_users.empty:
            st.subheader("Editar Usuário")
            user_to_edit = st.selectbox("Selecione o usuário", 
                                       options=filtered_users['id'].tolist(), 
                                       format_func=lambda x: f"{filtered_users.loc[filtered_users['id'] == x, 'nome'].values[0]} ({filtered_users.loc[filtered_users['id'] == x, 'tipo'].values[0]})")
            
            if user_to_edit:
                user_data = filtered_users.loc[filtered_users['id'] == user_to_edit].iloc[0]
                
                with st.form("edicao_usuario"):
                    nome = st.text_input("Nome*", value=user_data['nome'], placeholder="Nome completo")
                    email = st.text_input("Email*", value=user_data['email'], placeholder="email@exemplo.com")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        tipo = st.selectbox("Tipo de Usuário*", options=["morador", "catador", "admin"], index=["morador", "catador", "admin"].index(user_data['tipo']))
                    with col2:
                        telefone = st.text_input("Telefone*", value=user_data['telefone'], placeholder="(XX) XXXXX-XXXX")
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        bairro = st.text_input("Bairro", value=user_data.get('bairro', ''), placeholder="Nome do bairro")
                    with col4:
                        endereco = st.text_input("Endereço", value=user_data.get('endereco', ''), placeholder="Rua, número")
                        
                    if st.form_submit_button("Salvar Alterações"):
                        if nome and email and tipo and telefone:
                            try:
                                update_user(user_to_edit, {
                                    'nome': nome,
                                    'email': email,
                                    'tipo': tipo,
                                    'telefone': telefone,
                                    'bairro': bairro,
                                    'endereco': endereco
                                })
                                st.success("Usuário atualizado com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao atualizar usuário: {e}")
                        else:
                            st.error("Preencha todos os campos obrigatórios.")
                    
    def show_statistics(self):
        """Exibe estatísticas detalhadas do sistema com layout profissional"""
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 20px; color: white; 
                    box-shadow: 0 12px 40px rgba(0,0,0,0.15); margin-bottom: 30px;">
            <h1 style="margin: 0; font-size: 2.5rem; text-align: center; font-weight: 700;">
                📊 Dashboard de Estatísticas
            </h1>
            <p style="text-align: center; margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.9;">
                Visão completa do sistema de coleta seletiva
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Carrega dados
        users = load_users()
        coletas = load_coletas()
        
        # Métricas principais em cards estilizados
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_users = len(users) if not users.empty else 0
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 30px; border-radius: 20px; color: white; text-align: center; 
                        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3); margin-bottom: 20px;
                        border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px);">
                <div style="font-size: 3rem; font-weight: 800; margin-bottom: 10px;">{total_users}</div>
                <div style="font-size: 1.1rem; opacity: 0.9; font-weight: 500;">👥 Usuários Cadastrados</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            moradores = len(users[users['tipo'] == 'morador']) if not users.empty else 0
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        padding: 30px; border-radius: 20px; color: white; text-align: center; 
                        box-shadow: 0 8px 32px rgba(240, 147, 251, 0.3); margin-bottom: 20px;
                        border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px);">
                <div style="font-size: 3rem; font-weight: 800; margin-bottom: 10px;">{moradores}</div>
                <div style="font-size: 1.1rem; opacity: 0.9; font-weight: 500;">🏠 Moradores</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            catadores = len(users[users['tipo'] == 'catador']) if not users.empty else 0
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        padding: 30px; border-radius: 20px; color: white; text-align: center; 
                        box-shadow: 0 8px 32px rgba(79, 172, 254, 0.3); margin-bottom: 20px;
                        border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px);">
                <div style="font-size: 3rem; font-weight: 800; margin-bottom: 10px;">{catadores}</div>
                <div style="font-size: 1.1rem; opacity: 0.9; font-weight: 500;">♻️ Catadores</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_coletas = len(coletas) if not coletas.empty else 0
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                        padding: 30px; border-radius: 20px; color: white; text-align: center; 
                        box-shadow: 0 8px 32px rgba(250, 112, 154, 0.3); margin-bottom: 20px;
                        border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px);">
                <div style="font-size: 3rem; font-weight: 800; margin-bottom: 10px;">{total_coletas}</div>
                <div style="font-size: 1.1rem; opacity: 0.9; font-weight: 500;">📋 Total de Coletas</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Métricas adicionais de coletas
        if not coletas.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                pendentes = len(coletas[coletas['status'] == 'pendente'])
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); 
                            padding: 25px; border-radius: 15px; color: white; text-align: center; 
                            box-shadow: 0 6px 25px rgba(255, 154, 158, 0.3); margin-bottom: 20px;">
                    <div style="font-size: 2.5rem; font-weight: 700; margin-bottom: 8px;">{pendentes}</div>
                    <div style="font-size: 1rem; opacity: 0.9; font-weight: 500;">⏳ Pendentes</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                concluidas = len(coletas[coletas['status'] == 'concluida'])
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                            padding: 25px; border-radius: 15px; color: #2d3748; text-align: center; 
                            box-shadow: 0 6px 25px rgba(168, 237, 234, 0.3); margin-bottom: 20px;">
                    <div style="font-size: 2.5rem; font-weight: 700; margin-bottom: 8px;">{concluidas}</div>
                    <div style="font-size: 1rem; opacity: 0.8; font-weight: 500;">✅ Concluídas</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                taxa_conclusao = (concluidas / total_coletas) * 100 if total_coletas > 0 else 0
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                            padding: 25px; border-radius: 15px; color: #2d3748; text-align: center; 
                            box-shadow: 0 6px 25px rgba(255, 236, 210, 0.3); margin-bottom: 20px;">
                    <div style="font-size: 2.5rem; font-weight: 700; margin-bottom: 8px;">{taxa_conclusao:.1f}%</div>
                    <div style="font-size: 1rem; opacity: 0.8; font-weight: 500;">📈 Taxa de Conclusão</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                # Peso total coletado - usar tanto peso_kg quanto quantidade_estimada
                peso_total = 0.0
                if not coletas.empty:
                    # Primeiro, tentar usar peso_kg
                    if 'peso_kg' in coletas.columns:
                        peso_kg_sum = coletas['peso_kg'].fillna(0).sum()
                        if peso_kg_sum is not None:
                            peso_total += float(peso_kg_sum)
                    
                    # Se não tiver peso_kg ou for zero, usar quantidade_estimada
                    if peso_total == 0 and 'quantidade_estimada' in coletas.columns:
                        # Converter quantidade_estimada para float, tratando strings
                        for valor in coletas['quantidade_estimada']:
                            try:
                                if valor and str(valor).replace('.', '').replace(',', '').isdigit():
                                    peso_total += float(str(valor).replace(',', '.'))
                            except (ValueError, TypeError):
                                continue
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%); 
                            padding: 25px; border-radius: 15px; color: #2d3748; text-align: center; 
                            box-shadow: 0 6px 25px rgba(210, 153, 194, 0.3); margin-bottom: 20px;">
                    <div style="font-size: 2.5rem; font-weight: 700; margin-bottom: 8px;">{peso_total:.1f}kg</div>
                    <div style="font-size: 1rem; opacity: 0.8; font-weight: 500;">⚖️ Peso Total Coletado</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Gráficos interativos
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de distribuição de usuários
            st.markdown("""
            <div style="background: rgba(255,255,255,0.05); padding: 25px; border-radius: 20px; 
                        margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1); 
                        backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
                <h3 style="margin: 0 0 20px 0; color: #2d3748; font-size: 1.4rem; font-weight: 600;">
                    👥 Distribuição de Usuários
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not users.empty:
                try:
                    tipo_stats = users['tipo'].value_counts().reset_index()
                    tipo_stats.columns = ['Tipo', 'Quantidade']
                    
                    if px is not None:
                        fig = px.pie(tipo_stats, values='Quantidade', names='Tipo', 
                                   color_discrete_sequence=['#667eea', '#f093fb', '#4facfe', '#fa709a'])
                        fig.update_layout(
                            font=dict(size=14),
                            showlegend=True,
                            margin=dict(t=10, b=10, l=10, r=10),
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.dataframe(tipo_stats, use_container_width=True)
                except Exception as e:
                    st.error(f"Erro ao processar tipos de usuários: {e}")
        
        with col2:
            # Gráfico de status das coletas
            st.markdown("""
            <div style="background: rgba(255,255,255,0.05); padding: 25px; border-radius: 20px; 
                        margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1); 
                        backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
                <h3 style="margin: 0 0 20px 0; color: #2d3748; font-size: 1.4rem; font-weight: 600;">
                    📋 Status das Coletas
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not coletas.empty:
                try:
                    status_stats = coletas['status'].value_counts().reset_index()
                    status_stats.columns = ['Status', 'Quantidade']
                    
                    if px is not None:
                        fig = px.bar(status_stats, x='Status', y='Quantidade', 
                                   color='Status',
                                   color_discrete_map={'pendente': '#ff9a9e', 'concluida': '#a8edea'})
                        fig.update_layout(
                            font=dict(size=14),
                            showlegend=False,
                            margin=dict(t=10, b=10, l=10, r=10),
                            height=400,
                            xaxis_title="Status",
                            yaxis_title="Quantidade"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.dataframe(status_stats, use_container_width=True)
                except Exception as e:
                    st.error(f"Erro ao processar status das coletas: {e}")
        
        # Análise por bairros
        if not coletas.empty and 'bairro' in coletas.columns:
            st.markdown("""
            <div style="background: rgba(255,255,255,0.05); padding: 25px; border-radius: 20px; 
                        margin: 20px 0; border: 1px solid rgba(255,255,255,0.1); 
                        backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
                <h3 style="margin: 0 0 20px 0; color: #2d3748; font-size: 1.4rem; font-weight: 600;">
                    🏘️ Coletas por Bairro
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                bairro_stats = coletas['bairro'].value_counts().head(10).reset_index()
                bairro_stats.columns = ['Bairro', 'Quantidade']
                
                if px is not None:
                    fig = px.bar(bairro_stats, x='Bairro', y='Quantidade', 
                               color='Quantidade',
                               color_continuous_scale='viridis')
                    fig.update_layout(
                        font=dict(size=14),
                        showlegend=False,
                        margin=dict(t=10, b=10, l=10, r=10),
                        height=400,
                        xaxis_title="Bairro",
                        yaxis_title="Quantidade de Coletas"
                    )
                    fig.update_xaxes(tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.dataframe(bairro_stats, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao processar coletas por bairro: {e}")
        
        # Resumo executivo
        st.markdown("""
        <div style="background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%); 
                    padding: 30px; border-radius: 20px; color: white; 
                    box-shadow: 0 12px 40px rgba(0,0,0,0.2); margin-top: 30px;">
            <h3 style="margin: 0 0 20px 0; font-size: 1.6rem; font-weight: 600;">
                📊 Resumo Executivo
            </h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; backdrop-filter: blur(10px);">
                    <h4 style="margin: 0 0 10px 0; color: #ffd700;">Sistema Ativo</h4>
                    <p style="margin: 0; opacity: 0.9;">O sistema está funcionando com usuários ativos e coletas sendo realizadas.</p>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; backdrop-filter: blur(10px);">
                    <h4 style="margin: 0 0 10px 0; color: #98fb98;">Engajamento</h4>
                    <p style="margin: 0; opacity: 0.9;">Moradores e catadores estão utilizando a plataforma regularmente.</p>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; backdrop-filter: blur(10px);">
                    <h4 style="margin: 0 0 10px 0; color: #87ceeb;">Impacto Ambiental</h4>
                    <p style="margin: 0; opacity: 0.9;">Contribuindo para a sustentabilidade através da coleta seletiva.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def show_educational_content(self):
        """Exibe e permite gerenciar conteúdo educativo"""
        st.header("Conteúdo Educativo")
        
        # Carrega conteúdo existente
        try:
            conteudo = load_conteudo_educativo()
            if conteudo is None:
                conteudo = {"artigos": [], "dicas": [], "materiais": []}
        except Exception as e:
            st.error(f"Erro ao carregar conteúdo: {e}")
            conteudo = {"artigos": [], "dicas": [], "materiais": []}
        
        # Tabs para diferentes tipos de conteúdo
        tab1, tab2, tab3 = st.tabs(["Artigos", "Dicas", "Materiais"])
        
        with tab1:
            st.subheader("📝 Gerenciar Artigos")
            
            # Formulário para adicionar novo artigo
            with st.expander("➕ Adicionar Novo Artigo"):
                with st.form("novo_artigo"):
                    titulo = st.text_input("Título do Artigo*")
                    categoria = st.selectbox("Categoria*", 
                                           ["Reciclagem", "Sustentabilidade", "Meio Ambiente", "Educação Ambiental"])
                    conteudo_artigo = st.text_area("Conteúdo do Artigo*", height=200)
                    autor = st.text_input("Autor", value="Prefeitura de Itajubá")
                    
                    if st.form_submit_button("Adicionar Artigo"):
                        if titulo and categoria and conteudo_artigo:
                            try:
                                novo_artigo = {
                                    "titulo": titulo,
                                    "categoria": categoria,
                                    "conteudo": conteudo_artigo,
                                    "autor": autor,
                                    "data": datetime.now().strftime("%Y-%m-%d")
                                }
                                
                                if "artigos" not in conteudo:
                                    conteudo["artigos"] = []
                                conteudo["artigos"].append(novo_artigo)
                                
                                save_conteudo_educativo(conteudo)
                                st.success("Artigo adicionado com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao adicionar artigo: {e}")
                        else:
                            st.error("Preencha todos os campos obrigatórios.")
            
            # Lista artigos existentes
            st.subheader("📚 Artigos Existentes")
            if "artigos" in conteudo and conteudo["artigos"]:
                for i, artigo in enumerate(conteudo["artigos"]):
                    with st.expander(f"{artigo.get('titulo', 'Sem título')} - {artigo.get('categoria', 'Sem categoria')}"):
                        st.write(f"**Autor:** {artigo.get('autor', 'N/A')}")
                        st.write(f"**Data:** {artigo.get('data', 'N/A')}")
                        st.write(f"**Conteúdo:** {artigo.get('conteudo', 'N/A')}")
                        
                        if st.button(f"🗑️ Remover", key=f"remove_artigo_{i}"):
                            conteudo["artigos"].pop(i)
                            save_conteudo_educativo(conteudo)
                            st.success("Artigo removido!")
                            st.rerun()
            else:
                st.info("Nenhum artigo cadastrado ainda.")
        
        with tab2:
            st.subheader("💡 Gerenciar Dicas")
            
            # Formulário para adicionar nova dica
            with st.expander("➕ Adicionar Nova Dica"):
                with st.form("nova_dica"):
                    titulo_dica = st.text_input("Título da Dica*")
                    conteudo_dica = st.text_area("Conteúdo da Dica*", height=100)
                    
                    if st.form_submit_button("Adicionar Dica"):
                        if titulo_dica and conteudo_dica:
                            try:
                                nova_dica = {
                                    "titulo": titulo_dica,
                                    "conteudo": conteudo_dica
                                }
                                
                                if "dicas" not in conteudo:
                                    conteudo["dicas"] = []
                                conteudo["dicas"].append(nova_dica)
                                
                                save_conteudo_educativo(conteudo)
                                st.success("Dica adicionada com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao adicionar dica: {e}")
                        else:
                            st.error("Preencha todos os campos obrigatórios.")
            
            # Lista dicas existentes
            st.subheader("💡 Dicas Existentes")
            if "dicas" in conteudo and conteudo["dicas"]:
                for i, dica in enumerate(conteudo["dicas"]):
                    with st.expander(dica.get('titulo', 'Sem título')):
                        st.write(dica.get('conteudo', 'N/A'))
                        
                        if st.button(f"🗑️ Remover", key=f"remove_dica_{i}"):
                            conteudo["dicas"].pop(i)
                            save_conteudo_educativo(conteudo)
                            st.success("Dica removida!")
                            st.rerun()
            else:
                st.info("Nenhuma dica cadastrada ainda.")
        
        with tab3:
            st.subheader("♻️ Informações sobre Materiais")
            
            # Mostra informações sobre materiais recicláveis
            st.info("Esta seção mostra informações sobre os materiais recicláveis aceitos no sistema.")
            
            # Lista materiais do sistema
            materiais_sistema = [
                {"nome": "Papel", "descricao": "Jornais, revistas, papelão, papel branco"},
                {"nome": "Plástico", "descricao": "Garrafas PET, embalagens, sacolas plásticas"},
                {"nome": "Metal", "descricao": "Latas de alumínio, ferro, aço"},
                {"nome": "Vidro", "descricao": "Garrafas, potes, frascos"},
                {"nome": "Orgânico", "descricao": "Restos de comida, cascas, folhas"}
            ]
            
            for material in materiais_sistema:
                with st.expander(f"♻️ {material['nome']}"):
                    st.write(f"**Incluí:** {material['descricao']}")
                    
# Função global para renderizar a página do administrador (necessária para compatibilidade com app.py)
def render_admin_page(user_data):
    """
    Função para renderizar a página do administrador.
    Mantida para compatibilidade com o restante do sistema.
    
    Args:
        user_data (dict): Dados do usuário administrador logado
    """
    admin_page = AdminPage(user_data)
    admin_page.render()
