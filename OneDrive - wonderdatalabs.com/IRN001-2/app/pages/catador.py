"""
Página do Catador do sistema Coleta Seletiva Conectada

Este módulo contém a implementação da página do catador, com funcionalidades para
visualizar solicitações de coleta, aceitar/recusar solicitações, registrar coletas
e acessar conteúdo educativo.
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import json
import random
from PIL import Image
import base64
import io

from app.utils.database import (
    load_users, load_coletas, update_coleta, get_coletas_by_catador,
    get_coletas_disponiveis, load_notificacoes, marcar_notificacao_como_lida,
    get_notificacoes_by_usuario, save_notificacao, load_conteudo_educativo,
    save_notificacao, update_user, save_profile_photo, get_chat_messages, save_chat_message
)

class CatadorPage:
    """
    Classe responsável pela página do catador do sistema.
    Implementa a separação entre lógica e layout.
    """
    
    def __init__(self, user_data):
        """
        Inicializa a página do catador
        
        Args:
            user_data (dict): Dados do usuário catador logado
        """
        self.user_data = user_data
        self.load_css()
        
    def load_css(self):
        """Carrega o CSS específico da página do catador"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            # Carrega o CSS do catador
            css_path = os.path.join(base_dir, "app", "css", "catador.css")
            with open(css_path) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
                
            # Carrega o CSS do perfil
            perfil_css_path = os.path.join(base_dir, "app", "css", "perfil.css")
            with open(perfil_css_path) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Erro ao carregar CSS: {e}")
    
    def render(self):
        """Renderiza a página principal do catador"""
        
        # Menu lateral com opções específicas do catador
        menu_option = st.sidebar.radio(
            "Menu", 
            ["Início", "Solicitações Disponíveis", "Minhas Coletas", "Conteúdo Educativo", "Meu Perfil"]
        )
        
        # Separador e botão de logout
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Sair do Sistema", type="primary", use_container_width=True):
            from app.utils.auth import logout
            logout()
            st.rerun()
        
        # Exibe o conteúdo conforme a opção selecionada
        if menu_option == "Início":
            self.render_inicio()
        elif menu_option == "Solicitações Disponíveis":
            self.render_solicitacoes_disponiveis()
        elif menu_option == "Minhas Coletas":
            self.render_minhas_coletas()
        elif menu_option == "Conteúdo Educativo":
            self.render_conteudo_educativo()
        elif menu_option == "Meu Perfil":
            self.render_perfil()
    
    def render_inicio(self):
        """Renderiza a página inicial do catador"""
        st.markdown(f"""
        <div class='catador-welcome-card'>
            <h1 class='catador-header'>Painel do Catador</h1>
            <h2>Bem-vindo, {self.user_data['nome']}!</h2>
            <p>Através deste painel você pode visualizar solicitações de coleta, gerenciar suas coletas e acessar conteúdo educativo.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar estatísticas do catador
        col1, col2, col3 = st.columns(3)
        
        # Obter dados de coletas do catador
        # Garantir que estamos usando 'id' e não 'username'
        catador_id = self.user_data.get('id')
        if not catador_id:
            st.error("ID de catador não encontrado nos dados do usuário")
            return
            
        coletas_df = get_coletas_by_catador(catador_id)
        
        # Converter DataFrame para lista de dicionários
        coletas = coletas_df.to_dict('records') if not coletas_df.empty else []
        
        total_coletas = len(coletas)
        coletas_pendentes = len([c for c in coletas if c['status'] in ['pendente', 'agendada']])
        coletas_concluidas = len([c for c in coletas if c['status'] == 'concluida'])
        
        # Calcular peso total de resíduos coletados
        peso_total = sum([float(c.get('peso_kg', 0)) for c in coletas if c['status'] == 'concluida'])
        
        with col1:
            st.markdown(f"""
            <div class='catador-stat-card catador-stat-total'>
                <h3>{total_coletas}</h3>
                <p>Total de Coletas</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class='catador-stat-card catador-stat-pending'>
                <h3>{coletas_pendentes}</h3>
                <p>Coletas Pendentes</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class='catador-stat-card catador-stat-completed'>
                <h3>{peso_total:.1f} kg</h3>
                <p>Resíduos Coletados</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Mostrar solicitações recentes
        self.mostrar_solicitacoes_recentes()
        
        # Mostrar notificações recentes
        self.mostrar_notificacoes_recentes()
    
    def mostrar_solicitacoes_recentes(self):
        """Mostra as solicitações recentes para o catador"""
        st.markdown("<h3 class='catador-section-title'>Solicitações Recentes</h3>", unsafe_allow_html=True)
        
        # O parâmetro deve ser uma lista de bairros, não um ID de usuário
        # Obtemos as áreas de atuação do catador através do campo areas_atuacao
        areas_atuacao = self.user_data.get('areas_atuacao', '')
        bairros = [area.strip() for area in areas_atuacao.split(',')] if areas_atuacao else []
        
        coletas_disponiveis_df = get_coletas_disponiveis(bairros)
        
        # Verificar se o DataFrame está vazio usando .empty e converter para lista de dicionários se não estiver
        if not coletas_disponiveis_df.empty:
            # Converter DataFrame para lista de dicionários
            coletas_disponiveis = coletas_disponiveis_df.to_dict('records')
            
            # Mostrar apenas as 3 mais recentes usando data_criacao (ou data se data_criacao não existir)
            try:
                if 'data_criacao' in coletas_disponiveis[0]:
                    coletas_recentes = sorted(coletas_disponiveis, key=lambda x: x['data_criacao'], reverse=True)[:3]
                else:
                    # Usar o campo 'data' se 'data_criacao' não existir
                    coletas_recentes = sorted(coletas_disponiveis, key=lambda x: x['data'], reverse=True)[:3]
            except (KeyError, IndexError):
                # Se houver qualquer erro, não aplicar ordenação
                coletas_recentes = coletas_disponiveis[:3]
            
            # Carregar usuários para obter detalhes dos moradores
            users = load_users()
            
            for coleta in coletas_recentes:
                # Obter dados do morador
                morador_row = users[users['id'] == coleta['morador_id']]
                morador_nome = morador_row['nome'].iloc[0] if not morador_row.empty else "Morador não encontrado"
                morador_endereco = morador_row['endereco'].iloc[0] if 'endereco' in morador_row.columns else "Endereço não especificado"
                
                st.markdown(f"""
                <div class='catador-solicitacao-card'>
                    <h4>Solicitação de {morador_nome}</h4>
                    <p><strong>Data solicitada:</strong> {coleta['data_coleta']} às {coleta['horario_coleta']}</p>
                    <p><strong>Materiais:</strong> {coleta['materiais']}</p>
                    <p><strong>Quantidade estimada:</strong> {coleta['quantidade_estimada']} kg</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Aceitar solicitação #{coleta['id']}", key=f"accept_{coleta['id']}"):
                        # Preparar os dados para atualização
                        update_data = {'status': 'agendada', 'catador_id': self.user_data['id']}
                        # Atualizar status da coleta
                        update_coleta(coleta['id'], update_data)
                        
                        # Criar notificação para o morador
                        nova_notificacao = {
                            "id": str(random.randint(10000, 99999)),
                            "usuario_id": coleta['morador_id'],
                            "tipo_usuario": "morador",
                            "titulo": "Solicitação de coleta aceita!",
                            "mensagem": f"O catador {self.user_data['nome']} aceitou sua solicitação de coleta para o dia {coleta['data_coleta']} às {coleta['horario_coleta']}.",
                            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "lida": False
                        }
                        save_notificacao(nova_notificacao)
                        
                        st.success("Solicitação aceita com sucesso!")
                        st.rerun()
                
                with col2:
                    if st.button(f"Recusar solicitação #{coleta['id']}", key=f"reject_{coleta['id']}"):
                        # Preparar os dados para atualização
                        update_data = {'status': 'recusada'}
                        # Atualizar status da coleta
                        update_coleta(coleta['id'], update_data)
                        
                        # Criar notificação para o morador
                        nova_notificacao = {
                            "id": str(random.randint(10000, 99999)),
                            "usuario_id": coleta['morador_id'],
                            "tipo_usuario": "morador",
                            "titulo": "Solicitação de coleta recusada",
                            "mensagem": f"O catador {self.user_data['nome']} não pôde aceitar sua solicitação de coleta para o dia {coleta['data_coleta']}. Por favor, tente novamente com outro catador ou em outra data.",
                            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "lida": False
                        }
                        save_notificacao(nova_notificacao)
                        
                        st.info("Solicitação recusada.")
                        st.rerun()
        else:
            st.info("Não há solicitações de coleta disponíveis no momento.")
    
    def mostrar_notificacoes_recentes(self):
        """Mostra as notificações do catador, separadas em Recebidas e Lidas"""
        st.markdown("<h3 class='catador-section-title'>Notificações</h3>", unsafe_allow_html=True)
        
        # Adiciona CSS personalizado para melhorar a aparência das notificações
        st.markdown("""
        <style>
        .catador-notification-card {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 3px 8px rgba(0,0,0,0.08);
            border-left: 4px solid #3498db;
            transition: transform 0.2s;
        }
        .catador-notification-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 12px rgba(0,0,0,0.12);
        }
        .catador-notification-card h4 {
            color: #3498db;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }
        .catador-notification-card p {
            color: #333;
            margin-bottom: 10px;
            line-height: 1.5;
        }
        .catador-notification-card small {
            display: block;
            text-align: right;
            color: #777;
            font-style: italic;
        }
        .catador-notification-card.notification-read {
            border-left-color: #95a5a6;
            background-color: #f9f9f9;
            opacity: 0.85;
        }
        .catador-notification-card.notification-read h4 {
            color: #7f8c8d;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Buscar todas as notificações do catador
        try:
            # Obtém as notificações com tratamento de erros aprimorado
            try:
                notificacoes = get_notificacoes_by_usuario(self.user_data['id'], 'catador')
            except Exception as e1:
                try:
                    notificacoes = get_notificacoes_by_usuario(self.user_data['id'])
                except Exception as e2:
                    # Se falhar, retornar um DataFrame vazio
                    import pandas as pd
                    notificacoes = pd.DataFrame()
            
            if notificacoes is None or notificacoes.empty:
                st.info("Você não tem notificações recentes.")
                return
                
            # Verificar se a coluna 'lida' existe
            if 'lida' not in notificacoes.columns:
                # Tratamento para diferentes formatos de notificações
                if 'usuario_id' in notificacoes.columns:
                    notificacoes['lida'] = False  # Assume não lidas como padrão
                else:
                    st.error("Formato de notificações inválido.")
                    return
                
            # Separar notificações lidas e não lidas
            notificacoes_nao_lidas = notificacoes[notificacoes['lida'] == False]
            notificacoes_lidas = notificacoes[notificacoes['lida'] == True]
            
            # Criar tabs para separar as notificações
            tab1, tab2 = st.tabs(["Não Lidas", "Lidas"])
            
            with tab1:
                if not notificacoes_nao_lidas.empty:
                    # Exibir as notificações não lidas (mais recentes primeiro)
                    for _, notif in notificacoes_nao_lidas.sort_values('data', ascending=False).iterrows():
                        # Verificar se todas as colunas necessárias existem
                        titulo = notif.get('titulo', 'Notificação')
                        mensagem = notif.get('mensagem', 'Sem conteúdo')
                        data = notif.get('data', 'Data desconhecida')
                        notif_id = notif.get('id', '0')
                        
                        st.markdown(f"""
                        <div class='catador-notification-card'>
                            <h4>{titulo}</h4>
                            <p>{mensagem}</p>
                            <small>Recebida em: {data}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Botão para marcar como lida
                        if st.button(f"Marcar como lida", key=f"mark_read_{notif_id}"):
                            marcar_notificacao_como_lida(notif_id)
                            st.success("Notificação marcada como lida!")
                            st.rerun()
                else:
                    st.info("Você não tem notificações não lidas.")
            
            with tab2:
                if not notificacoes_lidas.empty:
                    # Exibir as notificações lidas (mais recentes primeiro)
                    for _, notif in notificacoes_lidas.sort_values('data', ascending=False).head(10).iterrows():
                        # Verificar se todas as colunas necessárias existem
                        titulo = notif.get('titulo', 'Notificação')
                        mensagem = notif.get('mensagem', 'Sem conteúdo')
                        data = notif.get('data', 'Data desconhecida')
                        
                        st.markdown(f"""
                        <div class='catador-notification-card notification-read'>
                            <h4>{titulo}</h4>
                            <p>{mensagem}</p>
                            <small>Recebida em: {data}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Você não tem notificações lidas.")
        except Exception as e:
            st.error(f"Erro ao carregar notificações: {str(e)}")
            st.info("Não foi possível carregar suas notificações no momento.")
            # Mostrar o traceback completo para diagnóstico
            import traceback
            st.code(traceback.format_exc())
    
    def render_solicitacoes_disponiveis(self):
        """Renderiza a página de solicitações de coleta disponíveis"""
        st.markdown("<h1 class='catador-header'>Solicitações de Coleta Disponíveis</h1>", unsafe_allow_html=True)
        
        # Adiciona CSS personalizado para melhorar a aparência dos cartões
        st.markdown("""
        <style>
        .catador-solicitacao-card {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-left: 5px solid #2e8b57;
            transition: transform 0.2s;
        }
        .catador-solicitacao-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        .catador-solicitacao-card h4 {
            color: #2e8b57;
            font-size: 1.3rem;
            margin-bottom: 15px;
            border-bottom: 1px solid #f0f0f0;
            padding-bottom: 10px;
        }
        .catador-solicitacao-card p {
            margin-bottom: 8px;
        }
        .catador-solicitacao-card strong {
            color: #333;
        }
        .catador-solicitacao-info {
            margin-bottom: 15px;
        }
        .catador-solicitacao-actions {
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Obtém as áreas de atuação do catador
        areas_atuacao = self.user_data.get('areas_atuacao', '')
        bairros = [area.strip() for area in areas_atuacao.split(',')] if areas_atuacao else []
        
        # Filtro de bairro
        if bairros:
            bairro_filtro = st.selectbox("Filtrar por bairro", options=["Todos"] + bairros)
            bairros_filtrados = bairros if bairro_filtro == "Todos" else [bairro_filtro]
        else:
            st.info("Você não tem áreas de atuação configuradas. Entre em contato com o administrador.")
            bairros_filtrados = []
        
        # Obtém as coletas disponíveis nos bairros de atuação do catador
        coletas_disponiveis_df = get_coletas_disponiveis(bairros_filtrados)
        
        # Verificar se o DataFrame está vazio
        if coletas_disponiveis_df.empty:
            st.info("Não há solicitações de coleta disponíveis nas suas áreas de atuação no momento.")
            return
        
        # Converter DataFrame para lista de dicionários
        coletas_disponiveis = coletas_disponiveis_df.to_dict('records')
        
        # Carrega usuários para obter detalhes dos moradores
        users = load_users()
        
        # Mostrar as coletas disponíveis em cards
        for coleta in coletas_disponiveis:
            # Obter dados do morador
            morador_row = users[users['id'] == coleta['morador_id']]
            morador_nome = morador_row['nome'].iloc[0] if not morador_row.empty else "Morador não encontrado"
            morador_endereco = morador_row['endereco'].iloc[0] if 'endereco' in morador_row.columns and not morador_row.empty else "Endereço não especificado"
            morador_bairro = morador_row['bairro'].iloc[0] if 'bairro' in morador_row.columns and not morador_row.empty else "Bairro não especificado"
            
            st.markdown(f"""
            <div class='catador-solicitacao-card'>
                <h4>Solicitação #{coleta['id']} - {morador_nome}</h4>
                <div class='catador-solicitacao-info'>
                    <p><strong>Local:</strong> {morador_bairro} - {morador_endereco}</p>
                    <p><strong>Data solicitada:</strong> {coleta['data_coleta']} às {coleta['horario_coleta']}</p>
                    <p><strong>Materiais:</strong> {coleta.get('tipos_materiais', coleta.get('materiais', 'Não especificado'))}</p>
                    <p><strong>Quantidade estimada:</strong> {coleta['quantidade_estimada']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Aceitar solicitação #{coleta['id']}", key=f"accept_disp_{coleta['id']}"):
                    # Preparar os dados para atualização
                    update_data = {'status': 'agendada', 'catador_id': self.user_data['id']}
                    # Atualizar status da coleta
                    update_coleta(coleta['id'], update_data)
                    
                    # Criar notificação para o morador
                    nova_notificacao = {
                        "id": str(random.randint(10000, 99999)),
                        "usuario_id": coleta['morador_id'],
                        "tipo_usuario": "morador",
                        "titulo": "Solicitação de coleta aceita!",
                        "mensagem": f"O catador {self.user_data['nome']} aceitou sua solicitação de coleta para o dia {coleta['data_coleta']} às {coleta['horario_coleta']}.",
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "lida": False
                    }
                    save_notificacao(nova_notificacao)
                    
                    st.success("Solicitação aceita com sucesso!")
                    st.rerun()
            
            with col2:
                if st.button(f"Recusar solicitação #{coleta['id']}", key=f"reject_disp_{coleta['id']}"):
                    # Preparar os dados para atualização
                    update_data = {'status': 'recusada'}
                    # Atualizar status da coleta
                    update_coleta(coleta['id'], update_data)
                    
                    # Criar notificação para o morador
                    nova_notificacao = {
                        "id": str(random.randint(10000, 99999)),
                        "usuario_id": coleta['morador_id'],
                        "tipo_usuario": "morador",
                        "titulo": "Solicitação de coleta recusada",
                        "mensagem": f"O catador {self.user_data['nome']} não pôde aceitar sua solicitação de coleta para o dia {coleta['data_coleta']}. Por favor, tente novamente com outro catador ou em outra data.",
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "lida": False
                    }
                    save_notificacao(nova_notificacao)
                    
                    st.info("Solicitação recusada.")
                    st.rerun()
    
    def render_minhas_coletas(self):
        """Renderiza a página de coletas do catador"""
        st.markdown("<h1 class='catador-header'>Minhas Coletas</h1>", unsafe_allow_html=True)
        
        # Adiciona CSS personalizado para melhorar a aparência dos cartões de coleta
        st.markdown("""
        <style>
        .catador-coleta-card {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .catador-coleta-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        .catador-coleta-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            border-bottom: 1px solid #f0f0f0;
            padding-bottom: 10px;
        }
        .catador-coleta-header h3 {
            color: #333;
            font-size: 1.3rem;
            margin: 0;
        }
        .catador-coleta-status {
            font-size: 0.8rem;
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 20px;
        }
        .catador-coleta-info {
            margin-bottom: 15px;
        }
        .catador-coleta-info p {
            margin-bottom: 8px;
        }
        .catador-coleta-pending {
            border-left: 5px solid #f39c12;
        }
        .catador-coleta-pending .catador-coleta-status {
            background-color: #fef5e7;
            color: #f39c12;
        }
        .catador-coleta-scheduled {
            border-left: 5px solid #3498db;
        }
        .catador-coleta-scheduled .catador-coleta-status {
            background-color: #e8f4fc;
            color: #3498db;
        }
        .catador-coleta-completed {
            border-left: 5px solid #2ecc71;
        }
        .catador-coleta-completed .catador-coleta-status {
            background-color: #e8f8f2;
            color: #2ecc71;
        }
        
        /* Estilos para botões menores e mais sutis */
        .stButton button {
            border-radius: 4px !important;
            font-weight: 400 !important;
            font-size: 0.85rem !important;
            padding: 0.3rem 0.6rem !important;
            min-height: 2rem !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton button[kind="primary"] {
            background: #3498db !important;
            border: 1px solid #3498db !important;
            color: white !important;
        }
        
        .stButton button[kind="secondary"] {
            background: #f8f9fa !important;
            border: 1px solid #e0e0e0 !important;
            color: #666 !important;
        }
        
        .stButton button[kind="secondary"]:hover {
            background: #e9ecef !important;
            border-color: #3498db !important;
            color: #3498db !important;
        }
        
        .stButton button:disabled {
            opacity: 0.4 !important;
            cursor: not-allowed !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Obtém as coletas do catador
        coletas_df = get_coletas_by_catador(self.user_data['id'])
        
        # Verificar se há coletas atribuídas ao catador
        if coletas_df.empty:
            st.info("Você ainda não tem coletas atribuídas.")
            return
            
        # Converter DataFrame para lista de dicionários
        coletas = coletas_df.to_dict('records')
        
        # Carregar usuários para obter detalhes dos moradores
        users = load_users()
        
        # Tabs para separar coletas por status
        tab1, tab2 = st.tabs(["Pendentes", "Aceitas"])
        
        with tab1:
            # Filtrar coletas pendentes
            coletas_pendentes = [c for c in coletas if c['status'] == 'pendente']
            self.mostrar_lista_coletas(coletas_pendentes, users, "Pendentes")
            
        with tab2:
            # Filtrar coletas aceitas (concluídas)
            coletas_aceitas = [c for c in coletas if c['status'] == 'concluida']
            self.mostrar_lista_coletas(coletas_aceitas, users, "Aceitas")
    
    def mostrar_lista_coletas(self, coletas, users, tipo):
        """
        Mostra uma lista de coletas
        
        Args:
            coletas (list): Lista de coletas a serem exibidas
            users (DataFrame): DataFrame com dados dos usuários
            tipo (str): Tipo de coletas (Pendentes, Agendadas, Concluídas)
        """
        if not coletas:
            st.info(f"Você não possui coletas {tipo.lower()}.")
            return
        
        for coleta in coletas:
            # Obter dados do morador
            morador_row = users[users['id'] == coleta['morador_id']]
            morador_nome = morador_row['nome'].iloc[0] if not morador_row.empty else "Morador não encontrado"
            morador_endereco = morador_row['endereco'].iloc[0] if 'endereco' in morador_row.columns and not morador_row.empty else "Endereço não especificado"
            morador_bairro = morador_row['bairro'].iloc[0] if 'bairro' in morador_row.columns and not morador_row.empty else "Bairro não especificado"
            
            status_class = {
                'pendente': 'catador-coleta-pending',
                'agendada': 'catador-coleta-scheduled',
                'concluida': 'catador-coleta-completed'
            }.get(coleta['status'], '')
            
            # Informações comuns para todos os tipos de coletas
            st.markdown(f"""
            <div class='catador-coleta-card {status_class}'>
                <div class='catador-coleta-header'>
                    <h3>Coleta #{coleta['id']}</h3>
                    <span class='catador-coleta-status'>{coleta['status'].upper()}</span>
                </div>
                <div class='catador-coleta-info'>
                    <p><strong>Morador:</strong> {morador_nome}</p>
                    <p><strong>Local:</strong> {morador_bairro} - {morador_endereco}</p>
                    <p><strong>Data:</strong> {coleta.get('data_coleta', 'Não especificada')} às {coleta.get('horario_coleta', 'Não especificado')}</p>
                    <p><strong>Materiais:</strong> {coleta.get('tipos_materiais', coleta.get('materiais', 'Não especificado'))}</p>
                    <p><strong>Quantidade estimada:</strong> {coleta.get('quantidade_estimada', 'Não especificada')} kg</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Ações específicas para cada tipo de coleta
            if tipo == "Pendentes":
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Aceitar coleta #{coleta['id']}", key=f"accept_{coleta['id']}", type="primary"):
                        # Atualizar status da coleta para concluída (aceita)
                        update_data = {
                            'status': 'concluida',
                            'data_conclusao': datetime.now().strftime("%Y-%m-%d")
                        }
                        
                        # Atualizar status da coleta
                        update_coleta(coleta['id'], update_data)
                        
                        # Criar notificação para o morador
                        nova_notificacao = {
                            "id": str(random.randint(10000, 99999)),
                            "usuario_id": coleta['morador_id'],
                            "tipo_usuario": "morador",
                            "titulo": "Coleta aceita!",
                            "mensagem": f"O catador {self.user_data['nome']} aceitou sua solicitação de coleta #{coleta['id']}. Ele entrará em contato em breve.",
                            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "lida": False
                        }
                        save_notificacao(nova_notificacao)
                        
                        st.success("Coleta aceita com sucesso!")
                        st.rerun()
            
            elif tipo == "Aceitas":
                # Expandir para mostrar chat da coleta aceita
                with st.expander(f"💬 Chat da coleta #{coleta['id']}", expanded=False):
                    # Mostrar informações básicas da coleta apenas uma vez
                    st.markdown(f"""
                    **📋 Coleta #{coleta['id']}** - Morador: {morador_nome}  
                    **📅 Data:** {coleta.get('data_coleta', 'Não especificada')} às {coleta.get('horario_coleta', 'Não especificado')}  
                    **📦 Materiais:** {coleta.get('tipos_materiais', coleta.get('materiais', 'Não especificado'))}
                    """)
                    
                    if coleta.get('observacoes'):
                        st.markdown(f"**💡 Observações:** {coleta['observacoes']}")
                    
                    st.markdown("---")
                    
                    # Sistema de chat
                    st.markdown("### 💬 Conversa com o Morador")
                    
                    # Carregar mensagens do chat
                    
                    chat_messages = get_chat_messages(coleta['id'])
                    
                    # Mostrar histórico de mensagens
                    if not chat_messages.empty:
                        st.markdown("**Histórico da conversa:**")
                        
                        # Container para as mensagens com altura limitada
                        with st.container():
                            for _, msg in chat_messages.iterrows():
                                data_msg = msg.get('data', '')
                                remetente = msg.get('remetente_tipo', 'Usuário').title()
                                conteudo = msg.get('mensagem', '').replace(f"{remetente}: ", "")
                                
                                # Estilo diferente para catador e morador
                                if msg.get('remetente_tipo') == 'catador':
                                    st.markdown(f"""
                                    <div style="background: #e3f2fd; padding: 8px 12px; border-radius: 8px; margin: 5px 0; margin-left: 40px;">
                                        <strong>🔧 Você:</strong> {conteudo}
                                        <br><small style="color: #666;">{data_msg}</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown(f"""
                                    <div style="background: #f1f8e9; padding: 8px 12px; border-radius: 8px; margin: 5px 0; margin-right: 40px;">
                                        <strong>🏠 {morador_nome}:</strong> {conteudo}
                                        <br><small style="color: #666;">{data_msg}</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                    else:
                        st.info("Nenhuma mensagem ainda. Inicie a conversa!")
                    
                    # Campo para enviar nova mensagem
                    st.markdown("**Enviar mensagem:**")
                    
                    with st.form(key=f"chat_form_{coleta['id']}", clear_on_submit=True):
                        nova_mensagem = st.text_area(
                            "Digite sua mensagem",
                            placeholder="Ex: Vou passar aí na parte da tarde para fazer a coleta...",
                            height=80,
                            max_chars=500
                        )
                        
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            enviar = st.form_submit_button("📤 Enviar", type="primary")
                        
                        if enviar and nova_mensagem.strip():
                            # Enviar mensagem
                            sucesso, mensagem_resultado = save_chat_message(
                                coleta_id=coleta['id'],
                                remetente_id=self.user_data['id'],
                                remetente_tipo='catador',
                                destinatario_id=coleta['morador_id'],
                                destinatario_tipo='morador',
                                mensagem=nova_mensagem.strip()
                            )
                            
                            if sucesso:
                                st.success("✅ Mensagem enviada!")
                                # Usar session state para controlar atualização
                                if f'chat_updated_{coleta["id"]}' not in st.session_state:
                                    st.session_state[f'chat_updated_{coleta["id"]}'] = True
                                    st.rerun()
                            else:
                                st.error(f"❌ {mensagem_resultado}")
                        elif enviar and not nova_mensagem.strip():
                            st.warning("⚠️ Digite uma mensagem antes de enviar.")
                    
                    # Limpar flag de atualização após exibir
                    if f'chat_updated_{coleta["id"]}' in st.session_state:
                        del st.session_state[f'chat_updated_{coleta["id"]}']
    

    def render_conteudo_educativo(self):
        """Renderiza a página de conteúdo educativo sobre reciclagem"""
        st.markdown("<h1 class='catador-header'>Conteúdo Educativo</h1>", unsafe_allow_html=True)
        
        # Adiciona CSS personalizado para melhorar a aparência dos cartões
        st.markdown("""
        <style>
        .educativo-article-card, .educativo-tip-card, .educativo-material-card {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 3px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .educativo-article-card:hover, .educativo-tip-card:hover, .educativo-material-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        }
        .educativo-article-card h3, .educativo-tip-card h4, .educativo-material-card h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }
        .educativo-article-content, .educativo-tip-card p {
            margin: 15px 0;
            line-height: 1.6;
            color: #333;
        }
        .educativo-article-footer {
            font-style: italic;
            color: #666;
            text-align: right;
            margin-top: 15px;
            font-size: 0.9em;
        }
        .educativo-material-section {
            margin: 15px 0;
        }
        .educativo-material-section h4 {
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        .educativo-material-section ul {
            margin-left: 20px;
            margin-bottom: 15px;
        }
        .educativo-material-section li {
            margin-bottom: 5px;
            color: #555;
        }
        .material-color {
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-left: 10px;
            vertical-align: middle;
            border: 2px solid #fff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Carrega o conteúdo educativo
        try:
            conteudo = load_conteudo_educativo()
            # Verificar se o dicionário está vazio ou é None
            if conteudo is None:
                st.error("Não foi possível carregar o conteúdo educativo.")
                return
                
        except Exception as e:
            st.error(f"Erro ao carregar conteúdo educativo: {e}")
            return
            
        # Tabs para diferentes tipos de conteúdo
        tab1, tab2, tab3 = st.tabs(["Artigos", "Dicas Rápidas", "Materiais Recicláveis"])
        
        with tab1:
            # Obter artigos do JSON
            artigos = conteudo.get('artigos', [])
            
            if artigos:
                # Extrair categorias dos artigos para filtro
                todas_categorias = []
                for artigo in artigos:
                    categoria = artigo.get('categoria', '')
                    if categoria:
                        todas_categorias.append(categoria)
                
                categorias = sorted(set(todas_categorias))
                
                if categorias:
                    categoria_selecionada = st.selectbox("Filtrar por categoria", options=["Todas"] + categorias)
                    
                    # Filtrar artigos pela categoria selecionada
                    if categoria_selecionada != "Todas":
                        artigos_filtrados = [a for a in artigos if a.get('categoria', '') == categoria_selecionada]
                    else:
                        artigos_filtrados = artigos
                else:
                    artigos_filtrados = artigos
                
                # Exibir artigos
                for artigo in artigos_filtrados:
                    st.markdown(f"""
                    <div class='educativo-article-card'>
                        <h3>{artigo.get('titulo', 'Sem título')}</h3>
                        <div class='educativo-article-content'>
                            {artigo.get('conteudo', 'Sem conteúdo')}
                        </div>
                        <div class='educativo-article-footer'>
                            <small>Publicado em: {artigo.get('data_publicacao', 'N/A')} | Autor: {artigo.get('autor', 'N/A')}</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum artigo disponível no momento.")
        
        with tab2:
            # Obter dicas do JSON
            dicas = conteudo.get('dicas', [])
            
            if dicas:
                # Layout em colunas para dicas
                col1, col2 = st.columns(2)
                
                for i, dica in enumerate(dicas):
                    with col1 if i % 2 == 0 else col2:
                        st.markdown(f"""
                        <div class='educativo-tip-card'>
                            <h4>{dica.get('titulo', 'Sem título')}</h4>
                            <p>{dica.get('conteudo', 'Sem conteúdo')}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Nenhuma dica disponível no momento.")
        
        with tab3:
            # Obter materiais do JSON
            materiais = conteudo.get('materiais', [])
            
            if materiais:
                for material in materiais:
                    tipo = material.get('tipo', 'Material').capitalize()
                    cor_lixeira = material.get('cor_lixeira', 'cinza').lower()
                    
                    # Mapear cores para cores CSS
                    cores_css = {
                        'azul': 'blue',
                        'vermelho': 'red', 
                        'verde': 'green',
                        'amarelo': 'yellow',
                        'marrom': 'brown',
                        'laranja': 'orange'
                    }
                    cor_css = cores_css.get(cor_lixeira, 'gray')
                    
                    st.markdown(f"""
                    <div class='educativo-material-card'>
                        <h3>Material: {tipo} <span class='material-color' style='background-color: {cor_css};'></span></h3>
                        <div class='educativo-material-section'>
                            <h4>✅ O que pode ser reciclado:</h4>
                            <ul>
                                {''.join([f"<li>{item}</li>" for item in material.get('o_que_pode', [])])}
                            </ul>
                        </div>
                        <div class='educativo-material-section'>
                            <h4>❌ O que não pode ser reciclado:</h4>
                            <ul>
                                {''.join([f"<li>{item}</li>" for item in material.get('o_que_nao_pode', [])])}
                            </ul>
                        </div>
                        <div class='educativo-material-section'>
                            <h4>💡 Dicas importantes:</h4>
                            <p>{material.get('dicas', 'Nenhuma dica disponível.')}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum material reciclável disponível no momento.")
    
    def render_perfil(self):
        """Renderiza a página de perfil do catador com opções para visualizar e editar informações"""
        
        # Obtendo dados atualizados do usuário
        users_df = load_users()
        user_id = self.user_data.get('id')
        user_data = users_df[users_df['id'] == user_id].iloc[0].to_dict() if not users_df[users_df['id'] == user_id].empty else self.user_data
        
        # Cartão de título igual ao da página "Início"
        st.markdown(f"""
        <div class='catador-welcome-card'>
            <h1 class='catador-header'>🔧 Meu Perfil</h1>
            <p>Visualize e edite suas informações pessoais e áreas de atuação.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Foto de perfil e informações
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown("<div class='profile-photo-container'>", unsafe_allow_html=True)
            
            # Verificar se o usuário tem foto de perfil
            foto_perfil = user_data.get('foto_perfil', '')
            # Converter para string para evitar problemas com tipos não string
            if foto_perfil is None or not isinstance(foto_perfil, str):
                foto_perfil = str(foto_perfil) if foto_perfil else ''
            
            # Normalizar o caminho (converter barras invertidas para barras normais)
            foto_perfil = foto_perfil.strip().replace('\\', '/')
            
            # Verificar se a foto existe
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            full_img_path = os.path.join(base_path, foto_perfil) if foto_perfil else ""
            
            # Tratamento seguro para exibição da imagem em base64
            try:
                if foto_perfil and os.path.exists(full_img_path):
                    # Converter imagem para base64 para evitar ícone de expandir
                    import base64
                    with open(full_img_path, "rb") as img_file:
                        img_base64 = base64.b64encode(img_file.read()).decode()
                    
                    # Determinar o tipo MIME da imagem
                    img_ext = os.path.splitext(full_img_path)[1].lower()
                    mime_type = {
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.png': 'image/png',
                        '.gif': 'image/gif'
                    }.get(img_ext, 'image/jpeg')
                    
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <img src="data:{mime_type};base64,{img_base64}" 
                             style="width: 180px; height: 180px; object-fit: cover; border-radius: 15px; 
                                    box-shadow: 0 8px 20px rgba(0,0,0,0.15); border: 3px solid rgba(0,0,0,0.1);">
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Se a foto não existir, mostra um placeholder
                    st.markdown("""
                    <div style="width:180px; height:180px; background-color:rgba(0,0,0,0.05); 
                                display:flex; align-items:center; justify-content:center; 
                                border-radius:15px; text-align:center; color:#666; margin: 0 auto;
                                border: 3px solid rgba(0,0,0,0.1); box-shadow: 0 8px 20px rgba(0,0,0,0.1);">
                        <div>
                            <div style="font-size: 4rem; margin-bottom: 10px; opacity: 0.6;">👤</div>
                            <p style="margin: 0; font-size: 0.9em; opacity: 0.7;">Sem foto</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div style="width:180px; height:180px; background-color:rgba(255,0,0,0.1); 
                            display:flex; align-items:center; justify-content:center; 
                            border-radius:15px; text-align:center; color:#666; margin: 0 auto;
                            border: 2px solid rgba(255,100,100,0.3);">
                    <div>
                        <div style="font-size: 2rem; margin-bottom: 10px;">⚠️</div>
                        <p style="margin: 0; font-size: 0.8em;">Erro ao carregar</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            # Informações do usuário em um cartão
            st.markdown(f"""
            <div class='catador-stat-card' style="margin-bottom: 20px; text-align: left;">
                <h3 style="color: #3498db; margin-bottom: 15px; text-align: left;">Informações Pessoais</h3>
                <p style="margin: 8px 0; color: #333; text-align: left;"><strong>Nome:</strong> {user_data.get('nome', '')}</p>
                <p style="margin: 8px 0; color: #333; text-align: left;"><strong>Email:</strong> {user_data.get('email', '')}</p>
                <p style="margin: 8px 0; color: #333; text-align: left;"><strong>Telefone:</strong> {user_data.get('telefone', '')}</p>
                <p style="margin: 8px 0; color: #333; text-align: left;"><strong>Áreas de Atuação:</strong> {user_data.get('areas_atuacao', '').replace(',', ', ')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Opções de edição dentro de um expander
        with st.expander("✏️ Editar Informações", expanded=False):
            with st.form("edit_form"):
                novo_nome = st.text_input("Nome", value=user_data.get('nome', ''))
                novo_email = st.text_input("Email", value=user_data.get('email', ''))
                novo_telefone = st.text_input("Telefone", value=user_data.get('telefone', ''))
                novas_areas_atuacao = st.text_input("Áreas de Atuação", value=user_data.get('areas_atuacao', '').replace(' ', ''))
                
                # Upload de nova foto de perfil
                st.markdown("<p>Foto de Perfil (JPG, PNG ou GIF)</p>", unsafe_allow_html=True)
                nova_foto = st.file_uploader("Foto de Perfil", type=["jpg", "jpeg", "png", "gif"], label_visibility="collapsed")
                
                # Preview da nova foto se foi carregada
                if nova_foto:
                    try:
                        import base64
                        # Converter para base64 para preview
                        nova_foto_base64 = base64.b64encode(nova_foto.read()).decode()
                        nova_foto.seek(0)  # Reset do buffer
                        
                        # Determinar tipo MIME
                        img_ext = os.path.splitext(nova_foto.name)[1].lower()
                        mime_type = {
                            '.jpg': 'image/jpeg',
                            '.jpeg': 'image/jpeg',
                            '.png': 'image/png',
                            '.gif': 'image/gif'
                        }.get(img_ext, 'image/jpeg')
                        
                        st.markdown(f"""
                        <div style="text-align: center; margin: 15px 0;">
                            <img src="data:{mime_type};base64,{nova_foto_base64}" 
                                 style="width: 150px; height: 150px; object-fit: cover; border-radius: 10px; 
                                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                            <p style="font-size: 0.9em; color: #666; margin-top: 8px;">Preview da nova foto</p>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Erro ao carregar preview: {str(e)}")
                
                # Botão para salvar alterações
                submitted = st.form_submit_button("💾 Salvar Alterações")
                
                if submitted:
                    # Validar e processar os dados
                    if not novo_nome or not novo_email:
                        st.error("Nome e Email são obrigatórios.")
                    else:
                        try:
                            # Atualizar dados do usuário
                            update_data = {
                                'nome': novo_nome,
                                'email': novo_email,
                                'telefone': novo_telefone,
                                'areas_atuacao': novas_areas_atuacao.replace(' ', ''),  # Remove espaços em branco
                            }
                            
                            # Processar upload da nova foto
                            if nova_foto:
                                success, foto_path = save_profile_photo(user_id, nova_foto)
                                if success:
                                    update_data['foto_perfil'] = foto_path
                                    st.success("Foto de perfil atualizada com sucesso!")
                                else:
                                    st.error(foto_path)  # Retorna a mensagem de erro da função
                                    return
                            
                            # Atualizar informações do usuário na base de dados
                            update_user(user_id, update_data)
                            
                            # Atualizar dados da sessão
                            st.session_state.user_data.update(update_data)
                            
                            # Mostrar mensagem de sucesso
                            st.success("✅ Informações atualizadas com sucesso!")
                            
                            # Se alterou foto, pedir para recarregar
                            if nova_foto:
                                st.info("💡 Pressione F5 para ver a nova foto de perfil atualizada.")
                            
                        except Exception as e:
                            st.error(f"Erro ao salvar alterações: {str(e)}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Botão para voltar
        if st.button("Voltar"):
            st.session_state.page = "inicio"
            st.experimental_rerun()

# Função para renderizar a página do catador (função de ponto de entrada)
def render_catador_page(user_data):
    """Renderiza a página do catador do sistema"""
    catador = CatadorPage(user_data)
    catador.render()
