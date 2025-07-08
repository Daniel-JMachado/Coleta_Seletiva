"""
Página do Morador do sistema Coleta Seletiva Conectada

Este módulo contém a implementação da página do morador, com funcionalidades para
solicitar coletas, ver histórico, visualizar catadores disponíveis e acessar conteúdo educativo.
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json
import random

from app.utils.database import (
    load_users, load_coletas, save_coleta, get_coletas_by_morador, 
    load_notificacoes, marcar_notificacao_como_lida, get_notificacoes_by_usuario,
    load_conteudo_educativo, save_notificacao, update_user, save_profile_photo,
    get_chat_messages, save_chat_message
)

class MoradorPage:
    """
    Classe responsável pela página do morador do sistema.
    Implementa a separação entre lógica e layout.
    """
    
    def __init__(self, user_data):
        """
        Inicializa a página do morador
        
        Args:
            user_data (dict): Dados do usuário morador logado
        """
        self.user_data = user_data
        self.load_css()
        
    def load_css(self):
        """Carrega o CSS específico da página do morador"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Três níveis acima da pasta atual
            css_path = os.path.join(base_dir, "app", "css", "morador.css")
            with open(css_path) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Erro ao carregar CSS do morador: {e}")
    
    def render(self):
        """Renderiza a página principal do morador"""
        
        # Menu lateral com opções específicas do morador
        menu_option = st.sidebar.radio(
            "Menu", 
            ["Início", "Solicitar Coleta", "Minhas Coletas", "Conteúdo Educativo", "Meu Perfil"]
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
        elif menu_option == "Solicitar Coleta":
            self.render_solicitar_coleta()
        elif menu_option == "Minhas Coletas":
            self.render_minhas_coletas()
        elif menu_option == "Conteúdo Educativo":
            self.render_conteudo_educativo()
        elif menu_option == "Meu Perfil":
            self.render_perfil()
    
    def render_inicio(self):
        """Renderiza a página inicial do morador"""
        st.markdown(f"""
        <div class='morador-welcome-card'>
            <h1 class='morador-header'>Painel do Morador</h1>
            <h2>Bem-vindo, {self.user_data['nome']}!</h2>
            <p>Através deste painel você pode solicitar coletas, acompanhar seus agendamentos e aprender mais sobre reciclagem.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar estatísticas do morador
        col1, col2, col3 = st.columns(3)
        
        # Obter dados de coletas do morador
        coletas_df = get_coletas_by_morador(self.user_data['id'])
        
        # Verificar se coletas_df é um DataFrame válido
        if not isinstance(coletas_df, pd.DataFrame):
            coletas_df = pd.DataFrame()
        
        total_coletas = len(coletas_df)
        coletas_pendentes = len(coletas_df[coletas_df['status'].isin(['pendente', 'agendada'])]) if 'status' in coletas_df.columns else 0
        coletas_concluidas = len(coletas_df[coletas_df['status'] == 'concluida']) if 'status' in coletas_df.columns else 0
        
        # Calcular peso total aproximado de resíduos
        peso_total = 0.0
        if isinstance(coletas_df, pd.DataFrame) and 'peso_kg' in coletas_df.columns and len(coletas_df) > 0:
            # Converte para numérico apenas as coletas aceitas
            coletas_concluidas_df = coletas_df[coletas_df['status'] == 'concluida']
            if isinstance(coletas_concluidas_df, pd.DataFrame) and len(coletas_concluidas_df) > 0:
                # Tratar possíveis valores não numéricos
                for peso_str in coletas_concluidas_df['peso_kg']:
                    try:
                        peso_num = float(peso_str) if peso_str and str(peso_str).strip() not in ['', 'nan', 'NaN'] else 0.0
                        peso_total += peso_num
                    except (ValueError, TypeError):
                        continue
        
        with col1:
            st.markdown(f"""
            <div class='morador-stat-card morador-stat-total'>
                <h3>{total_coletas}</h3>
                <p>Total de Coletas</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class='morador-stat-card morador-stat-pending'>
                <h3>{coletas_pendentes}</h3>
                <p>Coletas Pendentes</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class='morador-stat-card morador-stat-completed'>
                <h3>{peso_total:.1f} kg</h3>
                <p>Resíduos Reciclados</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Notificações recentes
        self.mostrar_notificacoes_recentes()
        
        # Dicas de reciclagem
        self.mostrar_dica_aleatoria()
    
    def mostrar_notificacoes_recentes(self):
        """Mostra as notificações do morador, separadas em Recebidas e Lidas"""
        st.markdown("<h3 class='morador-section-title'>Notificações</h3>", unsafe_allow_html=True)
        
        try:
            # Buscar todas as notificações do morador
            notificacoes = get_notificacoes_by_usuario(self.user_data['id'], 'morador')
            
            if not notificacoes.empty:
                # Converter a coluna 'data' para datetime com tratamento de erros
                notificacoes['data_dt'] = pd.to_datetime(notificacoes['data'], errors='coerce')
                
                # Separar notificações lidas e não lidas
                notificacoes_nao_lidas = notificacoes[notificacoes['lida'] == False]
                notificacoes_lidas = notificacoes[notificacoes['lida'] == True]
                
                # Criar tabs para separar as notificações
                tab1, tab2 = st.tabs(["Recebidas", "Lidas"])
                
                with tab1:
                    if not notificacoes_nao_lidas.empty:
                        # Ordenar por data, do mais recente para o mais antigo
                        notificacoes_nao_lidas = notificacoes_nao_lidas.sort_values(by='data_dt', ascending=False)
                        
                        for _, notif in notificacoes_nao_lidas.iterrows():
                            # Verificar e formatar título, mensagem e data
                            titulo = notif.get('titulo', 'Notificação')
                            mensagem = notif.get('mensagem', 'Sem conteúdo')
                            
                            # Formatar a data
                            data_recebimento = "Data não disponível"
                            if 'data' in notif and pd.notna(notif['data']):
                                try:
                                    data_dt = pd.to_datetime(notif['data'])
                                    data_recebimento = data_dt.strftime("%d/%m/%Y %H:%M")
                                except:
                                    data_recebimento = notif['data']
                            
                            # Exibir o card da notificação
                            st.markdown(f"""
                            <div class='morador-notification-card'>
                                <h4>{titulo}</h4>
                                <p>{mensagem}</p>
                                <small>Recebida em: {data_recebimento}</small>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Botão para marcar como lida
                            if st.button(f"Marcar como lida", key=f"mark_read_{notif['id']}"):
                                try:
                                    marcar_notificacao_como_lida(notif['id'])
                                    st.success("Notificação marcada como lida!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao marcar notificação como lida: {str(e)}")
                    else:
                        st.info("Você não tem notificações não lidas.")
                
                with tab2:
                    if not notificacoes_lidas.empty:
                        # Ordenar por data, do mais recente para o mais antigo
                        notificacoes_lidas = notificacoes_lidas.sort_values(by='data_dt', ascending=False).head(10)
                        
                        for _, notif in notificacoes_lidas.iterrows():
                            # Verificar e formatar título, mensagem e data
                            titulo = notif.get('titulo', 'Notificação')
                            mensagem = notif.get('mensagem', 'Sem conteúdo')
                            
                            # Formatar a data
                            data_recebimento = "Data não disponível"
                            if 'data' in notif and pd.notna(notif['data']):
                                try:
                                    data_dt = pd.to_datetime(notif['data'])
                                    data_recebimento = data_dt.strftime("%d/%m/%Y %H:%M")
                                except:
                                    data_recebimento = notif['data']
                            
                            # Exibir o card da notificação com classe adicional para lidas
                            st.markdown(f"""
                            <div class='morador-notification-card notification-read'>
                                <h4>{titulo}</h4>
                                <p>{mensagem}</p>
                                <small>Recebida em: {data_recebimento}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("Você não tem notificações lidas.")
            else:
                st.info("Você não tem notificações.")
                
        except Exception as e:
            st.error(f"Erro ao carregar notificações: {str(e)}")
            st.info("Não foi possível carregar suas notificações. Tente novamente mais tarde.")
    
    def mostrar_dica_aleatoria(self):
        """Mostra uma dica aleatória de reciclagem"""
        st.markdown("<h3 class='morador-section-title'>Dica de Reciclagem</h3>", unsafe_allow_html=True)
        
        dicas = [
            {
                "titulo": "Separe corretamente os resíduos",
                "texto": "Separe os materiais recicláveis por tipo: papel, plástico, vidro e metal. Isso facilita o trabalho dos catadores e melhora a qualidade da reciclagem."
            },
            {
                "titulo": "Lave as embalagens",
                "texto": "Lave levemente as embalagens antes de separar para reciclagem, removendo restos de alimentos ou produtos. Isso evita mau cheiro e contaminação."
            },
            {
                "titulo": "Sabia que o vidro é 100% reciclável?",
                "texto": "O vidro pode ser reciclado infinitamente sem perder sua qualidade. Ao reciclar 1kg de vidro, economiza-se 1,2kg de matéria-prima."
            },
            {
                "titulo": "Dobre as caixas de papelão",
                "texto": "Dobre as caixas de papelão antes de descartar. Isso economiza espaço e facilita o transporte pelos catadores."
            }
        ]
        
        dica = random.choice(dicas)
        
        st.markdown(f"""
        <div class='morador-tip-card'>
            <h4>{dica['titulo']}</h4>
            <p>{dica['texto']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_solicitar_coleta(self):
        """Renderiza a página unificada de solicitação de coleta com lista de catadores"""
        st.markdown("<h1 class='morador-header'>Solicitar Nova Coleta</h1>", unsafe_allow_html=True)
        
        # Adiciona CSS específico para a nova interface
        st.markdown("""
        <style>
        .catador-list-item {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-bottom: 10px;
            background: white;
            transition: all 0.2s;
        }
        .catador-list-item:hover {
            border-color: #2e8b57;
            box-shadow: 0 2px 8px rgba(46, 139, 87, 0.1);
        }
        .catador-header {
            padding: 15px;
            background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 8px 8px 0 0;
            cursor: pointer;
        }
        .catador-expanded {
            padding: 20px;
            border-top: 1px solid #e0e0e0;
        }
        .catador-profile {
            display: flex;
            gap: 20px;
            margin-bottom: 25px;
            align-items: flex-start;
        }
        .catador-photo {
            flex-shrink: 0;
        }
        .catador-info {
            flex-grow: 1;
        }
        .form-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #2e8b57;
        }
        .pagination-info {
            text-align: center;
            color: #666;
            margin: 20px 0;
            font-style: italic;
        }
        
        /* Estilos para paginação */
        .stButton button {
            border-radius: 4px !important;
            font-weight: 400 !important;
            font-size: 0.85rem !important;
            padding: 0.3rem 0.6rem !important;
            min-height: 2rem !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton button[kind="primary"] {
            background: #2e8b57 !important;
            border: 1px solid #2e8b57 !important;
            color: white !important;
        }
        
        .stButton button[kind="secondary"] {
            background: #f8f9fa !important;
            border: 1px solid #e0e0e0 !important;
            color: #666 !important;
        }
        
        .stButton button[kind="secondary"]:hover {
            background: #e9ecef !important;
            border-color: #2e8b57 !important;
            color: #2e8b57 !important;
        }
        
        .stButton button:disabled {
            opacity: 0.4 !important;
            cursor: not-allowed !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Carregar lista de catadores
        users = load_users()
        catadores_df = users[users['tipo'] == 'catador'].copy()
        
        if catadores_df.empty:
            st.warning("Não há catadores disponíveis no momento.")
            return
        
        # Converter para lista de dicionários e ordenar alfabeticamente
        catadores = []
        for _, catador in catadores_df.iterrows():
            catador_dict = catador.to_dict()
            catador_dict['areas_list'] = []
            if pd.notna(catador_dict.get('areas_atuacao')):
                areas = str(catador_dict['areas_atuacao']).split(',')
                catador_dict['areas_list'] = [area.strip() for area in areas if area.strip()]
            catadores.append(catador_dict)
        
        # Ordenar alfabeticamente por nome
        catadores = sorted(catadores, key=lambda x: x['nome'])
        
        # Filtros na parte superior
        col1, col2 = st.columns([2, 1])
        
        with col1:
            busca_bairro = st.text_input(
                "🔍 Buscar por bairro", 
                placeholder="Digite o nome do bairro (ex: Centro, Varginha...)",
                help="Digite o nome do bairro para encontrar catadores que atendem essa região"
            )
        
        with col2:
            st.markdown("<div style='height: 26px;'></div>", unsafe_allow_html=True)  # Espaçador
            total_catadores = len(catadores)
            st.metric("Total de Catadores", total_catadores)
        
        # Filtrar catadores por bairro se busca foi feita
        catadores_filtrados = catadores
        if busca_bairro.strip():
            busca_lower = busca_bairro.lower().strip()
            catadores_filtrados = []
            for catador in catadores:
                # Buscar nas áreas de atuação
                encontrou = False
                for area in catador['areas_list']:
                    if busca_lower in area.lower():
                        encontrou = True
                        break
                # Buscar também no bairro do catador
                if not encontrou and pd.notna(catador.get('bairro')):
                    if busca_lower in str(catador['bairro']).lower():
                        encontrou = True
                
                if encontrou:
                    catadores_filtrados.append(catador)
        
        # Mostrar resultado da busca
        if busca_bairro.strip():
            if catadores_filtrados:
                st.success(f"✅ Encontrados {len(catadores_filtrados)} catadores que atendem '{busca_bairro}'")
            else:
                st.warning(f"❌ Nenhum catador encontrado para o bairro '{busca_bairro}'")
                return
        
        # Paginação
        items_per_page = 10
        total_pages = (len(catadores_filtrados) + items_per_page - 1) // items_per_page
        
        # Inicializar página atual na sessão se não existir
        if 'current_page_catadores' not in st.session_state:
            st.session_state.current_page_catadores = 1
        
        current_page = st.session_state.current_page_catadores
        
        # Sistema de paginação com botões (estilo Gmail)
        if total_pages > 1:
            st.markdown("---")
            
            # Criar layout para os botões de paginação
            pagination_cols = st.columns([1, 6, 1])
            
            with pagination_cols[1]:  # Coluna central para os botões
                btn_cols = []
                
                # Calcular quais páginas mostrar
                if total_pages <= 7:
                    # Se temos 7 ou menos páginas, mostrar todas
                    pages_to_show = list(range(1, total_pages + 1))
                else:
                    # Sistema inteligente para muitas páginas
                    if current_page <= 4:
                        # Início: 1 2 3 4 5 ... 10
                        pages_to_show = list(range(1, 6)) + ['...'] + [total_pages]
                    elif current_page >= total_pages - 3:
                        # Final: 1 ... 6 7 8 9 10
                        pages_to_show = [1] + ['...'] + list(range(total_pages - 4, total_pages + 1))
                    else:
                        # Meio: 1 ... 4 5 6 ... 10
                        pages_to_show = [1] + ['...'] + list(range(current_page - 1, current_page + 2)) + ['...'] + [total_pages]
                
                # Calcular número de colunas necessárias
                num_buttons = len(pages_to_show) + 2  # +2 para botões anterior/próximo
                btn_cols = st.columns(num_buttons)
                
                col_idx = 0
                
                # Botão "Anterior"
                with btn_cols[col_idx]:
                    if st.button("⬅️", disabled=(current_page == 1), key="prev_page", help="Página anterior"):
                        st.session_state.current_page_catadores = current_page - 1
                        st.rerun()
                col_idx += 1
                
                # Botões das páginas
                for page in pages_to_show:
                    with btn_cols[col_idx]:
                        if page == '...':
                            st.markdown("<div style='text-align: center; padding: 8px;'>...</div>", unsafe_allow_html=True)
                        else:
                            # Determinar se é a página atual
                            is_current = (page == current_page)
                            button_type = "primary" if is_current else "secondary"
                            
                            if st.button(
                                str(page), 
                                key=f"page_{page}",
                                type=button_type,
                                disabled=is_current,
                                use_container_width=True
                            ):
                                st.session_state.current_page_catadores = page
                                st.rerun()
                    col_idx += 1
                
                # Botão "Próximo"
                with btn_cols[col_idx]:
                    if st.button("➡️", disabled=(current_page == total_pages), key="next_page", help="Próxima página"):
                        st.session_state.current_page_catadores = current_page + 1
                        st.rerun()
        
        # Informações sobre paginação
        start_idx = (current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(catadores_filtrados))
        catadores_pagina = catadores_filtrados[start_idx:end_idx]
        
        # Mostrar informações da paginação
        if len(catadores_filtrados) > 0:
            st.markdown(f"""
            <div class="pagination-info">
                Mostrando catadores {start_idx + 1} a {end_idx} de {len(catadores_filtrados)} total
            </div>
            """, unsafe_allow_html=True)
        
        # Seção de catadores disponíveis
        st.markdown("## 👥 Catadores Disponíveis")
        
        if len(catadores_pagina) == 0:
            st.info("Nenhum catador encontrado para os critérios de busca especificados.")
        else:
            # Lista de catadores com expanders
            for idx, catador in enumerate(catadores_pagina):
                # Container para cada catador
                catador_container = st.container()
                
                with catador_container:
                    # Cabeçalho clicável do catador
                    with st.expander(f"📋 {catador.get('nome', 'Nome não informado')} • {catador.get('areas_atuacao', 'Áreas não informadas')}", expanded=False):
                        # Perfil completo do catador
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            # Foto do catador
                            foto_path = f"uploads/fotos_perfil/user_{catador.get('id', 0)}_foto_perfil.png"
                            if os.path.exists(foto_path):
                                # Converter para base64
                                with open(foto_path, "rb") as img_file:
                                    import base64
                                    img_base64 = base64.b64encode(img_file.read()).decode()
                                    
                                st.markdown(f"""
                                <div style="text-align: center; margin-bottom: 15px;">
                                    <img src="data:image/png;base64,{img_base64}" 
                                         style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; 
                                                border: 3px solid #2e8b57; box-shadow: 0 4px 12px rgba(46, 139, 87, 0.2);">
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div style="text-align: center; margin-bottom: 15px;">
                                    <div style="width: 120px; height: 120px; border-radius: 50%; background: linear-gradient(135deg, #2e8b57, #90EE90); 
                                                display: flex; align-items: center; justify-content: center; margin: 0 auto;
                                                box-shadow: 0 4px 12px rgba(46, 139, 87, 0.2);">
                                        <span style="font-size: 48px; color: white;">👤</span>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        with col2:
                            # Informações detalhadas
                            st.markdown(f"""
                            <div class="catador-info">
                                <h4 style="color: #2e8b57; margin-bottom: 15px;">Informações do Catador</h4>
                                <p><strong>Nome:</strong> {catador.get('nome', 'Não informado')}</p>
                                <p><strong>Email:</strong> {catador.get('email', 'Não informado')}</p>
                                <p><strong>Telefone:</strong> {catador.get('telefone', 'Não informado')}</p>
                                <p><strong>Áreas de Atuação:</strong> {catador.get('areas_atuacao', 'Não informado').replace(',', ', ')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Separador
                        st.markdown("---")
                        
                        # Seção de solicitação de coleta
                        st.markdown(f"""
                        <div class="form-section">
                            <h4 style="color: #2e8b57; margin-bottom: 15px;">📋 Solicitar Coleta</h4>
                            <p>Complete as informações abaixo para solicitar uma coleta com <strong>{catador.get('nome', 'este catador')}</strong>.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Formulário de solicitação
                        with st.form(key=f"form_coleta_{catador.get('id', idx)}", clear_on_submit=True):
                            col1_form, col2_form = st.columns(2)
                            
                            with col1_form:
                                data_coleta = st.date_input(
                                    "Data da Coleta",
                                    help="Selecione a data em que você gostaria que a coleta fosse realizada"
                                )
                                endereco_coleta = st.text_input(
                                    "Endereço da Coleta",
                                    placeholder="Rua, número, bairro...",
                                    help="Informe o endereço completo onde a coleta deve ser realizada"
                                )
                            
                            with col2_form:
                                horario_coleta = st.selectbox(
                                    "Horário Preferido",
                                    ["Manhã (8h às 12h)", "Tarde (12h às 18h)", "Noite (18h às 20h)"],
                                    help="Selecione o período do dia de sua preferência"
                                )
                                tipo_material = st.multiselect(
                                    "Tipos de Material",
                                    ["Papel", "Plástico", "Metal", "Vidro", "Eletrônicos", "Outros"],
                                    help="Selecione os tipos de material que você tem para coleta"
                                )
                                quantidade_estimada = st.number_input(
                                    "Quantidade Estimada (kg)",
                                    min_value=0.1,
                                    max_value=1000.0,
                                    value=1.0,
                                    step=0.1,
                                    help="Informe a quantidade estimada de material em quilogramas"
                                )
                            
                            observacoes = st.text_area(
                                "Observações",
                                placeholder="Informações adicionais sobre a coleta...",
                                help="Campo opcional para informações extras"
                            )
                            
                            submitted = st.form_submit_button("📞 Solicitar Coleta", type="primary", use_container_width=True)
                            
                            if submitted:
                                # Validações
                                if not endereco_coleta:
                                    st.error("Por favor, informe o endereço da coleta.")
                                elif not tipo_material:
                                    st.error("Por favor, selecione pelo menos um tipo de material.")
                                elif quantidade_estimada <= 0:
                                    st.error("Por favor, informe uma quantidade válida de material.")
                                else:
                                    # Processa a solicitação
                                    from app.utils.database import save_coleta, save_notificacao
                                    import random
                                    
                                    # Dados da solicitação
                                    coleta_data = {
                                        'morador_id': self.user_data.get('id'),
                                        'catador_id': None,  # Não atribuído ainda
                                        'data_coleta': data_coleta.strftime('%Y-%m-%d'),
                                        'horario_coleta': horario_coleta,
                                        'endereco_coleta': endereco_coleta,
                                        'tipos_materiais': ', '.join(tipo_material),
                                        'observacoes': observacoes,
                                        'status': 'pendente',
                                        'data_criacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                        'bairro': self.user_data.get('bairro', ''),
                                        'quantidade_estimada': f'{quantidade_estimada:.1f}',
                                        'peso_kg': quantidade_estimada  # Para compatibilidade com cálculos existentes
                                    }
                                    
                                    success, message = save_coleta(coleta_data)
                                    
                                    if success:
                                        st.success(f"🎉 Solicitação enviada com sucesso!")
                                        st.info("Você pode acompanhar o status da sua solicitação na seção 'Minhas Coletas'.")
                                        
                                        # Criar notificação para o catador
                                        nova_notificacao = {
                                            "usuario_id": catador.get('id'),
                                            "tipo_usuario": "catador",
                                            "titulo": "Nova solicitação de coleta",
                                            "mensagem": f"O morador {self.user_data['nome']} solicitou uma coleta para o dia {data_coleta.strftime('%d/%m/%Y')} ({horario_coleta}). Materiais: {', '.join(tipo_material)}. Quantidade estimada: {quantidade_estimada:.1f} kg",
                                            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            "lida": False
                                        }
                                        save_notificacao(nova_notificacao)
                                        
                                        st.balloons()
                                    else:
                                        st.error(f"Erro ao enviar a solicitação: {message}")
        
        # Garantir que current_page está dentro dos limites válidos
        if current_page > total_pages:
            st.session_state.current_page_catadores = total_pages
            current_page = total_pages
        elif current_page < 1:
            st.session_state.current_page_catadores = 1
            current_page = 1
    
    def render_minhas_coletas(self):
        """Renderiza a página de minhas coletas do morador"""
        st.markdown("<h1 class='morador-header'>Minhas Coletas</h1>", unsafe_allow_html=True)
        
        # Obter dados do morador
        try:
            coletas_df = get_coletas_by_morador(self.user_data['id'])
            users_df = load_users()
            
            # Verificar se há coletas
            if coletas_df.empty:
                st.info("Você ainda não solicitou nenhuma coleta.")
                return
            
            # Separar coletas por status
            coletas_pendentes = coletas_df[coletas_df['status'] == 'pendente']
            coletas_concluidas = coletas_df[coletas_df['status'] == 'concluida']
            
            # Criar tabs para organizar as coletas
            tab1, tab2 = st.tabs([f"Pendentes ({len(coletas_pendentes)})", f"Aceitas ({len(coletas_concluidas)})"])
            
            with tab1:
                st.markdown("### 🔄 Coletas Pendentes")
                if not coletas_pendentes.empty:
                    st.info("Estas coletas foram solicitadas e estão aguardando confirmação dos catadores.")
                    self.mostrar_lista_coletas(coletas_pendentes, users_df, "pendente")
                else:
                    st.info("Você não possui coletas pendentes.")
            
            with tab2:
                st.markdown("### ✅ Coletas Aceitas")
                if not coletas_concluidas.empty:
                    st.info("Estas coletas foram aceitas pelos catadores.")
                    self.mostrar_lista_coletas(coletas_concluidas, users_df, "concluida")
                else:
                    st.info("Você não possui coletas aceitas.")
                    
        except Exception as e:
            st.error(f"Erro ao carregar coletas: {str(e)}")
    
    def mostrar_lista_coletas(self, coletas, users, tipo):
        """
        Mostra uma lista de coletas
        
        Args:
            coletas (DataFrame): DataFrame de coletas a serem exibidas
            users (DataFrame): DataFrame com dados dos usuários
            tipo (str): Tipo de coletas (pendente, concluida)
        """
        if len(coletas) == 0:
            st.info(f"Você não possui coletas {tipo}s.")
            return
        
        for idx in range(len(coletas)):
            coleta = coletas.iloc[idx]
            
            # Obter dados do catador para coletas aceitas
            catador_nome = "Aguardando confirmação"
            if tipo == "concluida" and pd.notna(coleta.get('catador_id')):
                catador_row = users[users['id'] == coleta['catador_id']]
                catador_nome = catador_row['nome'].iloc[0] if not catador_row.empty else "Catador não encontrado"
            
            # Acessar valores de forma segura
            coleta_id = coleta.get('id', 'N/A')
            data_coleta = coleta.get('data_coleta', 'Não informada')
            horario_coleta = coleta.get('horario_coleta', 'Não informado')
            materiais = coleta.get('tipos_materiais', coleta.get('materiais', 'Não especificado'))
            endereco = coleta.get('endereco_coleta', coleta.get('endereco', 'Não especificado'))
            observacoes = coleta.get('observacoes', '')
            
            # Container para cada coleta
            with st.container():
                # Card da coleta
                status_emoji = "⏳" if tipo == "pendente" else "✅"
                status_color = "#f39c12" if tipo == "pendente" else "#2ecc71"
                
                # Usar um container com bordas via CSS
                st.markdown(f"""
                <div style="border: 1px solid {status_color}; border-left: 5px solid {status_color}; 
                           border-radius: 8px; padding: 15px; margin-bottom: 15px; background: white;">
                """, unsafe_allow_html=True)
                
                # Cabeçalho da coleta
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{status_emoji} Coleta #{coleta_id}**")
                with col2:
                    st.markdown(f'<span style="background: {status_color}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">{tipo.upper()}</span>', unsafe_allow_html=True)
                
                # Informações da coleta
                st.write(f"**Catador:** {catador_nome}")
                st.write(f"**Data:** {data_coleta} às {horario_coleta}")
                st.write(f"**Materiais:** {materiais}")
                st.write(f"**Endereço:** {endereco}")
                
                # Mostrar quantidade estimada
                quantidade_estimada = coleta.get('quantidade_estimada', coleta.get('peso_kg', 'Não especificada'))
                if str(quantidade_estimada).replace('.', '').isdigit():
                    st.write(f"**Quantidade estimada:** {quantidade_estimada} kg")
                else:
                    st.write(f"**Quantidade estimada:** {quantidade_estimada}")
                
                if observacoes:
                    st.write(f"**Observações:** {observacoes}")
                
                # Fechar div
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Para coletas aceitas, mostrar chat
                if tipo == "concluida":
                    with st.expander(f"💬 Conversa com {catador_nome}", expanded=False):
                        # Sistema de chat
                        st.markdown("### 💬 Mensagens sobre a coleta")
                        
                        # Carregar mensagens do chat
                        chat_messages = get_chat_messages(coleta_id)
                        
                        # Mostrar histórico de mensagens
                        if not chat_messages.empty:
                            st.markdown("**Conversa:**")
                            
                            # Container para as mensagens
                            with st.container():
                                for _, msg in chat_messages.iterrows():
                                    data_msg = msg.get('data', '')
                                    remetente = msg.get('remetente_tipo', 'Usuário').title()
                                    conteudo = msg.get('mensagem', '').replace(f"{remetente}: ", "")
                                    
                                    # Estilo diferente para catador e morador
                                    if msg.get('remetente_tipo') == 'morador':
                                        st.markdown(f"""
                                        <div style="background: #e8f5e8; padding: 8px 12px; border-radius: 8px; margin: 5px 0; margin-left: 40px;">
                                            <strong>🏠 Você:</strong> {conteudo}
                                            <br><small style="color: #666;">{data_msg}</small>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"""
                                        <div style="background: #f0f8ff; padding: 8px 12px; border-radius: 8px; margin: 5px 0; margin-right: 40px;">
                                            <strong>🔧 {catador_nome}:</strong> {conteudo}
                                            <br><small style="color: #666;">{data_msg}</small>
                                        </div>
                                        """, unsafe_allow_html=True)
                        else:
                            st.info("Nenhuma mensagem ainda.")
                        
                        # Campo para enviar nova mensagem
                        st.markdown("**Responder:**")
                        
                        with st.form(key=f"chat_form_morador_{coleta_id}", clear_on_submit=True):
                            nova_mensagem = st.text_area(
                                "Digite sua resposta",
                                placeholder="Ex: Perfeito! Estarei em casa aguardando...",
                                height=80,
                                max_chars=500
                            )
                            
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                enviar = st.form_submit_button("📤 Enviar", type="primary")
                            
                            if enviar and nova_mensagem.strip():
                                # Enviar mensagem
                                sucesso, mensagem_resultado = save_chat_message(
                                    coleta_id=coleta_id,
                                    remetente_id=self.user_data['id'],
                                    remetente_tipo='morador',
                                    destinatario_id=coleta.get('catador_id'),
                                    destinatario_tipo='catador',
                                    mensagem=nova_mensagem.strip()
                                )
                                
                                if sucesso:
                                    st.success("✅ Mensagem enviada!")
                                    # Usar session state para controlar atualização
                                    if f'chat_updated_morador_{coleta_id}' not in st.session_state:
                                        st.session_state[f'chat_updated_morador_{coleta_id}'] = True
                                        st.rerun()
                                else:
                                    st.error(f"❌ {mensagem_resultado}")
                            elif enviar and not nova_mensagem.strip():
                                st.warning("⚠️ Digite uma mensagem antes de enviar.")
                        
                        # Limpar flag de atualização após exibir
                        if f'chat_updated_morador_{coleta_id}' in st.session_state:
                            del st.session_state[f'chat_updated_morador_{coleta_id}']
                
                st.markdown("---")
    
    def render_conteudo_educativo(self):
        """Renderiza a página de conteúdo educativo sobre reciclagem"""
        st.markdown("<h1 class='morador-header'>Conteúdo Educativo</h1>", unsafe_allow_html=True)
        
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
        """Renderiza a página de perfil do morador com opções para visualizar e editar informações"""
        
        # Obtendo dados atualizados do usuário
        from app.utils.database import update_user, save_profile_photo
        users_df = load_users()
        user_id = self.user_data.get('id')
        user_data = users_df[users_df['id'] == user_id].iloc[0].to_dict() if not users_df[users_df['id'] == user_id].empty else self.user_data
        
        # Cartão de título igual ao da página "Início"
        st.markdown(f"""
        <div class='morador-welcome-card'>
            <h1 class='morador-header'>🏠 Meu Perfil</h1>
            <p>Visualize e edite suas informações pessoais.</p>
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
            <div class='morador-stat-card' style="margin-bottom: 20px; text-align: left;">
                <h3 style="color: #2e8b57; margin-bottom: 15px; text-align: left;">Informações Pessoais</h3>
                <p style="margin: 8px 0; color: #333; text-align: left;"><strong>Nome:</strong> {user_data.get('nome', '')}</p>
                <p style="margin: 8px 0; color: #333; text-align: left;"><strong>Email:</strong> {user_data.get('email', '')}</p>
                <p style="margin: 8px 0; color: #333; text-align: left;"><strong>Telefone:</strong> {user_data.get('telefone', '')}</p>
                <p style="margin: 8px 0; color: #333; text-align: left;"><strong>Bairro:</strong> {user_data.get('bairro', '')}</p>
                <p style="margin: 8px 0; color: #333; text-align: left;"><strong>Endereço:</strong> {user_data.get('endereco', '')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Opções de edição dentro de um expander
        with st.expander("✏️ Editar Informações", expanded=False):
            with st.form("edit_form"):
                novo_nome = st.text_input("Nome", value=user_data.get('nome', ''))
                novo_email = st.text_input("Email", value=user_data.get('email', ''))
                novo_telefone = st.text_input("Telefone", value=user_data.get('telefone', ''))
                novo_bairro = st.text_input("Bairro", value=user_data.get('bairro', ''))
                novo_endereco = st.text_input("Endereço", value=user_data.get('endereco', ''))
                
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
                                'bairro': novo_bairro,
                                'endereco': novo_endereco
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
    
# Função para renderizar a página do morador a partir do módulo principal
def render_morador_page(user_data):
    """
    Função principal para renderizar a página do morador.
    Esta função é chamada pelo app.py quando um usuário do tipo 'morador' faz login.
    
    Args:
        user_data (dict): Dados do usuário morador logado
    """
    page = MoradorPage(user_data)
    page.render()
