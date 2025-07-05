"""
Módulo de banco de dados do sistema Coleta Seletiva Conectada

Este módulo contém funções para gerenciar os dados do sistema, incluindo
usuários, coletas, notificações e conteúdo educativo.
"""

import pandas as pd
import os
import sys
import json
from datetime import datetime

# Definições de caminhos base para facilitar referências a arquivos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
USERS_FILE = os.path.join(DATA_DIR, 'usuarios.csv')
COLETAS_FILE = os.path.join(DATA_DIR, 'coletas.csv')
NOTIFICACOES_FILE = os.path.join(DATA_DIR, 'notificacoes.csv')
CONTEUDO_FILE = os.path.join(DATA_DIR, 'conteudo_educativo.json')

# Funções de carregamento de dados

def load_users():
    """
    Carrega os usuários do arquivo CSV.
    
    Returns:
        DataFrame: DataFrame com os usuários
    """
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    else:
        # Criar arquivo se não existir
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'tipo': ['admin', 'catador', 'catador', 'morador', 'morador'],
            'username': ['admin', 'catador1', 'catador2', 'morador1', 'morador2'],
            'senha': ['admin', 'admin', 'admin', 'admin', 'admin'],
            'nome': ['Administrador', 'João Silva', 'Maria Santos', 'Ana Oliveira', 'Carlos Pereira'],
            'email': ['admin@prefeitura.gov.br', 'joao@email.com', 'maria@email.com', 'ana@email.com', 'carlos@email.com'],
            'telefone': ['123456789', '987654321', '912345678', '998765432', '987651234'],
            'endereco': ['Prefeitura Municipal', 'Rua das Flores 123', 'Av Principal 456', 'Rua dos Ipês 789', 'Av das Palmeiras 321'],
            'bairro': ['Centro', 'Jardim Primavera', 'Vila Nova', 'Centro', 'Jardim Primavera'],
            'areas_atuacao': ['', 'Zona Norte;Centro', 'Zona Sul;Jardim Primavera', '', ''],
            'status': ['ativo', 'ativo', 'ativo', 'ativo', 'ativo'],
            'data_cadastro': ['2023-01-01', '2023-01-01', '2023-01-01', '2023-01-01', '2023-01-01'],
            'ultimo_login': ['', '', '', '', ''],
            'foto_perfil': ['', '', '', '', '']
        })
        df.to_csv(USERS_FILE, index=False)
        return df

def load_coletas():
    """
    Carrega as coletas do arquivo CSV.
    
    Returns:
        DataFrame: DataFrame com as coletas
    """
    if os.path.exists(COLETAS_FILE):
        return pd.read_csv(COLETAS_FILE)
    else:
        # Criar arquivo se não existir
        os.makedirs(os.path.dirname(COLETAS_FILE), exist_ok=True)
        df = pd.DataFrame({
            'id': [1, 2],
            'morador_id': [4, 5],
            'catador_id': [2, 3],
            'data': ['2025-07-01', '2025-07-02'],
            'hora': ['10:00', '15:00'],
            'endereco': ['Rua dos Ipês 789', 'Av das Palmeiras 321'],
            'bairro': ['Centro', 'Jardim Primavera'],
            'status': ['pendente', 'pendente'],
            'tipo_material': ['Plástico;Papel', 'Vidro;Metal'],
            'volume_estimado': ['Médio', 'Pequeno'],
            'observacoes': ['', ''],
            'avaliacao': [0, 0],
            'data_criacao': ['2025-06-01', '2025-06-01']
        })
        df.to_csv(COLETAS_FILE, index=False)
        return df

def load_notificacoes():
    """
    Carrega as notificações do arquivo CSV.
    
    Returns:
        DataFrame: DataFrame com as notificações
    """
    if os.path.exists(NOTIFICACOES_FILE):
        return pd.read_csv(NOTIFICACOES_FILE)
    else:
        # Criar arquivo se não existir
        os.makedirs(os.path.dirname(NOTIFICACOES_FILE), exist_ok=True)
        df = pd.DataFrame({
            'id': [1, 2],
            'para_usuario_id': [2, 3],
            'de_usuario_id': [4, 5],
            'mensagem': ['Tenho materiais recicláveis para coleta.', 'Por favor passe para coletar materiais recicláveis.'],
            'data': ['2025-07-01', '2025-07-02'],
            'lida': [False, False],
            'tipo': ['coleta', 'coleta']
        })
        df.to_csv(NOTIFICACOES_FILE, index=False)
        return df

def load_conteudo_educativo():
    """
    Carrega o conteúdo educativo do arquivo JSON.
    
    Returns:
        dict: Dicionário com o conteúdo educativo (artigos, dicas, materiais)
    """
    if os.path.exists(CONTEUDO_FILE):
        with open(CONTEUDO_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Criar arquivo se não existir com conteúdo básico
        os.makedirs(os.path.dirname(CONTEUDO_FILE), exist_ok=True)
        conteudo_default = {
            "artigos": [
                {
                    "id": 1,
                    "titulo": "Importância da Reciclagem",
                    "conteudo": "A reciclagem é fundamental para preservar o meio ambiente e reduzir o desperdício.",
                    "categoria": "meio_ambiente",
                    "data_publicacao": "2025-06-01",
                    "autor": "Admin"
                }
            ],
            "dicas": [
                {
                    "id": 1,
                    "titulo": "Separe os materiais corretamente",
                    "conteudo": "Mantenha recipientes separados para cada tipo de material reciclável.",
                    "categoria": "dia_a_dia"
                }
            ],
            "materiais": [
                {
                    "tipo": "papel",
                    "o_que_pode": ["Jornais", "Revistas", "Caixas"],
                    "o_que_nao_pode": ["Papel higiênico", "Papel sujo"],
                    "dicas": "Mantenha o papel seco e limpo.",
                    "cor_lixeira": "Azul"
                }
            ]
        }
        with open(CONTEUDO_FILE, 'w', encoding='utf-8') as f:
            json.dump(conteudo_default, f, ensure_ascii=False, indent=4)
        return conteudo_default

# Funções de salvamento de dados

def save_users(df):
    """
    Salva os usuários no arquivo CSV.
    
    Args:
        df (DataFrame): DataFrame com os usuários
    """
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    df.to_csv(USERS_FILE, index=False)

def save_coletas(df):
    """
    Salva as coletas no arquivo CSV.
    
    Args:
        df (DataFrame): DataFrame com as coletas
    """
    os.makedirs(os.path.dirname(COLETAS_FILE), exist_ok=True)
    df.to_csv(COLETAS_FILE, index=False)

def save_notificacoes(df):
    """
    Salva as notificações no arquivo CSV.
    
    Args:
        df (DataFrame): DataFrame com as notificações
    """
    os.makedirs(os.path.dirname(NOTIFICACOES_FILE), exist_ok=True)
    df.to_csv(NOTIFICACOES_FILE, index=False)

def save_conteudo_educativo(df):
    """
    Salva o conteúdo educativo no arquivo CSV.
    
    Args:
        df (DataFrame): DataFrame com o conteúdo educativo
    """
    os.makedirs(os.path.dirname(CONTEUDO_FILE), exist_ok=True)
    df.to_csv(CONTEUDO_FILE, index=False)

# Funções de manipulação de usuários

def check_user_exists(email):
    """
    Verifica se um usuário existe com o email fornecido.
    
    Args:
        email (str): Email do usuário
        
    Returns:
        bool: True se o usuário existir, False caso contrário
    """
    users_df = load_users()
    return email in users_df['email'].values

def save_user(user_data):
    """
    Salva um novo usuário no banco de dados.
    
    Args:
        user_data (dict): Dicionário com os dados do usuário
        
    Returns:
        tuple: (bool, str) - Sucesso da operação e mensagem
    """
    try:
        users_df = load_users()
        
        # Adicionar novo usuário
        new_user_df = pd.DataFrame([user_data])
        users_df = pd.concat([users_df, new_user_df], ignore_index=True)
        
        save_users(users_df)
        return True, "Usuário registrado com sucesso!"
    
    except Exception as e:
        return False, f"Erro ao salvar usuário: {str(e)}"

def update_user(user_id, user_data):
    """
    Atualiza os dados de um usuário existente.
    
    Args:
        user_id (int): ID do usuário
        user_data (dict): Dicionário com os dados atualizados
        
    Returns:
        tuple: (bool, str) - Sucesso da operação e mensagem
    """
    try:
        users_df = load_users()
        
        # Verificar se o usuário existe
        if not (users_df['id'] == user_id).any():
            return False, "Usuário não encontrado"
        
        # Atualizar campos
        for key, value in user_data.items():
            if key in users_df.columns:
                users_df.loc[users_df['id'] == user_id, key] = value
        
        save_users(users_df)
        return True, "Usuário atualizado com sucesso!"
    
    except Exception as e:
        return False, f"Erro ao atualizar usuário: {str(e)}"

def delete_user(user_id):
    """
    Remove um usuário do banco de dados.
    
    Args:
        user_id (int): ID do usuário
        
    Returns:
        tuple: (bool, str) - Sucesso da operação e mensagem
    """
    try:
        users_df = load_users()
        
        # Verificar se o usuário existe
        if not (users_df['id'] == user_id).any():
            return False, "Usuário não encontrado"
        
        # Remover usuário
        users_df = users_df[users_df['id'] != user_id]
        
        save_users(users_df)
        return True, "Usuário removido com sucesso!"
    
    except Exception as e:
        return False, f"Erro ao remover usuário: {str(e)}"

def register_user(user_data):
    """
    Registra um novo usuário.
    
    Args:
        user_data (dict): Dados do usuário
        
    Returns:
        tuple: (bool, str) - Sucesso da operação e mensagem
    """
    try:
        # Verificar se o email já existe
        if check_user_exists(user_data.get('email')):
            return False, "Já existe um usuário com este email"
        
        # Adicionar o usuário
        return save_user(user_data)
    
    except Exception as e:
        return False, f"Erro ao registrar usuário: {str(e)}"

# Funções de manipulação de coletas

def save_coleta(coleta_data):
    """
    Salva uma nova coleta no banco de dados.
    
    Args:
        coleta_data (dict): Dicionário com os dados da coleta
        
    Returns:
        tuple: (bool, str) - Sucesso da operação e mensagem
    """
    try:
        coletas_df = load_coletas()
        
        # Gerar novo ID
        coleta_data['id'] = 1 if coletas_df.empty else coletas_df['id'].max() + 1
        
        # Adicionar nova coleta
        new_coleta_df = pd.DataFrame([coleta_data])
        coletas_df = pd.concat([coletas_df, new_coleta_df], ignore_index=True)
        
        save_coletas(coletas_df)
        return True, "Coleta agendada com sucesso!"
    
    except Exception as e:
        return False, f"Erro ao agendar coleta: {str(e)}"

def update_coleta(coleta_id, coleta_data):
    """
    Atualiza os dados de uma coleta existente.
    
    Args:
        coleta_id (int): ID da coleta
        coleta_data (dict): Dicionário com os dados atualizados
        
    Returns:
        tuple: (bool, str) - Sucesso da operação e mensagem
    """
    try:
        coletas_df = load_coletas()
        
        # Verificar se a coleta existe
        if not (coletas_df['id'] == coleta_id).any():
            return False, "Coleta não encontrada"
        
        # Atualizar campos
        for key, value in coleta_data.items():
            if key in coletas_df.columns:
                coletas_df.loc[coletas_df['id'] == coleta_id, key] = value
        
        save_coletas(coletas_df)
        return True, "Coleta atualizada com sucesso!"
    
    except Exception as e:
        return False, f"Erro ao atualizar coleta: {str(e)}"

def get_coletas_by_morador(morador_id):
    """
    Retorna as coletas de um morador específico.
    
    Args:
        morador_id (int): ID do morador
        
    Returns:
        DataFrame: DataFrame com as coletas do morador
    """
    coletas_df = load_coletas()
    return coletas_df[coletas_df['morador_id'] == morador_id]

def get_coletas_by_catador(catador_id):
    """
    Retorna as coletas de um catador específico.
    
    Args:
        catador_id (int): ID do catador
        
    Returns:
        DataFrame: DataFrame com as coletas do catador
    """
    coletas_df = load_coletas()
    return coletas_df[coletas_df['catador_id'] == catador_id]

def get_coletas_disponiveis(bairros=None):
    """
    Retorna as coletas disponíveis (sem catador atribuído).
    
    Args:
        bairros (list, optional): Lista de bairros para filtrar as coletas. Default é None.
        
    Returns:
        DataFrame: DataFrame com as coletas disponíveis
    """
    coletas_df = load_coletas()
    disponivel = coletas_df[coletas_df['catador_id'].isna() | coletas_df['catador_id'].isnull()]
    
    # Se bairros não for None e não estiver vazio, filtrar por bairros
    if bairros and len(bairros) > 0:
        # Filtrar coletas que estão nos bairros especificados
        return disponivel[disponivel['bairro'].isin(bairros)]
    
    # Caso contrário, retornar todas as coletas disponíveis
    return disponivel

# Funções de manipulação de notificações

def save_notificacao(notificacao_data):
    """
    Salva uma nova notificação no banco de dados.
    
    Args:
        notificacao_data (dict): Dicionário com os dados da notificação
        
    Returns:
        tuple: (bool, str) - Sucesso da operação e mensagem
    """
    try:
        notificacoes_df = load_notificacoes()
        
        # Gerar novo ID
        notificacao_data['id'] = 1 if notificacoes_df.empty else notificacoes_df['id'].max() + 1
        
        # Adicionar nova notificação
        new_notificacao_df = pd.DataFrame([notificacao_data])
        notificacoes_df = pd.concat([notificacoes_df, new_notificacao_df], ignore_index=True)
        
        save_notificacoes(notificacoes_df)
        return True, "Notificação enviada com sucesso!"
    
    except Exception as e:
        return False, f"Erro ao enviar notificação: {str(e)}"

def marcar_notificacao_como_lida(notificacao_id):
    """
    Marca uma notificação como lida.
    
    Args:
        notificacao_id (int): ID da notificação
        
    Returns:
        tuple: (bool, str) - Sucesso da operação e mensagem
    """
    try:
        notificacoes_df = load_notificacoes()
        
        # Verificar se a notificação existe
        if not (notificacoes_df['id'] == notificacao_id).any():
            return False, "Notificação não encontrada"
        
        # Marcar como lida
        notificacoes_df.loc[notificacoes_df['id'] == notificacao_id, 'lida'] = True
        
        save_notificacoes(notificacoes_df)
        return True, "Notificação marcada como lida!"
    
    except Exception as e:
        return False, f"Erro ao marcar notificação como lida: {str(e)}"

def get_notificacoes_by_usuario(usuario_id, tipo_usuario=None):
    """
    Retorna as notificações de um usuário específico.
    
    Args:
        usuario_id (int): ID do usuário
        tipo_usuario (str, optional): Tipo de usuário (morador, catador, admin). Default é None.
        
    Returns:
        DataFrame: DataFrame com as notificações do usuário
    """
    notificacoes_df = load_notificacoes()
    
    # Verificar os nomes das colunas para garantir compatibilidade
    if 'usuario_id' in notificacoes_df.columns:
        usuario_id_col = 'usuario_id'
    elif 'para_usuario_id' in notificacoes_df.columns:
        usuario_id_col = 'para_usuario_id'
    else:
        # Se não encontrar nenhuma coluna esperada, retorna DataFrame vazio
        return pd.DataFrame()
    
    # Filtrar por ID do usuário usando a coluna identificada
    notificacoes = notificacoes_df[notificacoes_df[usuario_id_col] == usuario_id]
    
    # Se tipo_usuario for especificado e a coluna existir, filtrar também por tipo
    if tipo_usuario is not None and 'tipo_usuario' in notificacoes_df.columns:
        notificacoes = notificacoes[notificacoes['tipo_usuario'] == tipo_usuario]
    
    return notificacoes

# Funções de manipulação de conteúdo educativo

def add_artigo(titulo, conteudo, autor, tags):
    """
    Adiciona um novo artigo educativo.
    
    Args:
        titulo (str): Título do artigo
        conteudo (str): Conteúdo do artigo
        autor (str): Autor do artigo
        tags (str): Tags separadas por ponto e vírgula
        
    Returns:
        tuple: (bool, str) - Sucesso da operação e mensagem
    """
    try:
        conteudo_df = load_conteudo_educativo()
        
        # Gerar novo ID
        new_id = 1 if conteudo_df.empty else conteudo_df['id'].max() + 1
        
        # Adicionar novo artigo
        new_artigo = pd.DataFrame({
            'id': [new_id],
            'tipo': ['artigo'],
            'titulo': [titulo],
            'conteudo': [conteudo],
            'data_publicacao': [datetime.now().strftime('%Y-%m-%d')],
            'autor': [autor],
            'tags': [tags]
        })
        
        conteudo_df = pd.concat([conteudo_df, new_artigo], ignore_index=True)
        save_conteudo_educativo(conteudo_df)
        return True, "Artigo adicionado com sucesso!"
    
    except Exception as e:
        return False, f"Erro ao adicionar artigo: {str(e)}"

def add_dica(titulo, conteudo, autor, tags):
    """
    Adiciona uma nova dica educativa.
    
    Args:
        titulo (str): Título da dica
        conteudo (str): Conteúdo da dica
        autor (str): Autor da dica
        tags (str): Tags separadas por ponto e vírgula
        
    Returns:
        tuple: (bool, str) - Sucesso da operação e mensagem
    """
    try:
        conteudo_df = load_conteudo_educativo()
        
        # Gerar novo ID
        new_id = 1 if conteudo_df.empty else conteudo_df['id'].max() + 1
        
        # Adicionar nova dica
        new_dica = pd.DataFrame({
            'id': [new_id],
            'tipo': ['dica'],
            'titulo': [titulo],
            'conteudo': [conteudo],
            'data_publicacao': [datetime.now().strftime('%Y-%m-%d')],
            'autor': [autor],
            'tags': [tags]
        })
        
        conteudo_df = pd.concat([conteudo_df, new_dica], ignore_index=True)
        save_conteudo_educativo(conteudo_df)
        return True, "Dica adicionada com sucesso!"
    
    except Exception as e:
        return False, f"Erro ao adicionar dica: {str(e)}"

def save_profile_photo(user_id, uploaded_file):
    """
    Salva a foto de perfil de um usuário.
    
    Implementa a lógica para:
    1. Salvar foto com nome padronizado (user_{id}_foto_perfil.ext)
    2. Remover fotos antigas do mesmo usuário
    3. Garantir que cada usuário tenha apenas uma foto
    
    Args:
        user_id (int): ID do usuário
        uploaded_file: Arquivo de imagem carregado via streamlit
        
    Returns:
        tuple: (bool, str) - Sucesso da operação e caminho da imagem
    """
    try:
        # Garantir que user_id seja um inteiro
        user_id = int(user_id)
        
        # Cria o diretório de uploads se não existir
        import os
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            
        # Cria também o diretório específico para fotos de perfil
        fotos_perfil_dir = os.path.join(upload_dir, 'fotos_perfil')
        if not os.path.exists(fotos_perfil_dir):
            os.makedirs(fotos_perfil_dir)
        
        # Verificar se é uma extensão de imagem válida
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        if file_extension not in valid_extensions:
            return False, "Arquivo inválido. Por favor, envie uma imagem (jpg, png ou gif)."
        
        # Nome padronizado para a foto do usuário (sem timestamp)
        filename = f"user_{user_id}_foto_perfil{file_extension}"
        filepath = os.path.join(fotos_perfil_dir, filename)
        
        # Remover fotos antigas do mesmo usuário, se existirem
        for ext in valid_extensions:
            old_file = os.path.join(fotos_perfil_dir, f"user_{user_id}_foto_perfil{ext}")
            if os.path.exists(old_file) and old_file != filepath:
                try:
                    os.remove(old_file)
                except Exception as e:
                    # Continuar mesmo se não conseguir remover o arquivo antigo
                    print(f"Aviso: Não foi possível remover a foto antiga: {str(e)}")
        
        # Salvar o arquivo novo
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Verificar se o arquivo foi salvo corretamente
        if not os.path.exists(filepath):
            return False, f"Erro: Arquivo não foi salvo em {filepath}"
            
        # Caminho relativo para o banco de dados (sempre com barras normais)
        relative_path = 'uploads/fotos_perfil/' + filename
        
        # Carregar usuários e atualizar o caminho
        import pandas as pd
        # Usar USERS_FILE já definido no início do arquivo em vez de criar um novo caminho
        users_df = pd.read_csv(USERS_FILE)
        users_df.loc[users_df['id'] == user_id, 'foto_perfil'] = relative_path
        users_df.to_csv(USERS_FILE, index=False)
        
        print(f"Foto salva com sucesso em: {filepath}")
        print(f"Caminho relativo no CSV: {relative_path}")
        return True, relative_path
    
    except Exception as e:
        print(f"Erro ao salvar foto: {str(e)}")
        return False, f"Erro ao salvar foto: {str(e)}"

def save_chat_message(coleta_id, remetente_id, remetente_tipo, destinatario_id, destinatario_tipo, mensagem):
    """
    Salva uma mensagem de chat entre catador e morador para uma coleta específica.
    
    Args:
        coleta_id (int): ID da coleta
        remetente_id (int): ID do usuário que envia
        remetente_tipo (str): Tipo do remetente (catador/morador)
        destinatario_id (int): ID do usuário que recebe
        destinatario_tipo (str): Tipo do destinatário (catador/morador)
        mensagem (str): Conteúdo da mensagem
        
    Returns:
        tuple: (bool, str) - Sucesso da operação e mensagem
    """
    try:
        # Usar as notificações existentes para implementar o chat
        nova_mensagem = {
            "usuario_id": destinatario_id,
            "tipo_usuario": destinatario_tipo,
            "titulo": f"Mensagem sobre coleta #{coleta_id}",
            "mensagem": f"{remetente_tipo.title()}: {mensagem}",
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "lida": False,
            "referencia_id": coleta_id,
            "tipo": "chat_coleta",
            "remetente_id": remetente_id,
            "remetente_tipo": remetente_tipo
        }
        
        return save_notificacao(nova_mensagem)
        
    except Exception as e:
        return False, f"Erro ao enviar mensagem: {str(e)}"

def get_chat_messages(coleta_id):
    """
    Retorna todas as mensagens de chat de uma coleta específica.
    
    Args:
        coleta_id (int): ID da coleta
        
    Returns:
        DataFrame: DataFrame com as mensagens do chat
    """
    try:
        notificacoes_df = load_notificacoes()
        
        # Filtrar mensagens de chat desta coleta específica
        if 'tipo' in notificacoes_df.columns and 'referencia_id' in notificacoes_df.columns:
            chat_messages = notificacoes_df[
                (notificacoes_df['tipo'] == 'chat_coleta') & 
                (notificacoes_df['referencia_id'] == coleta_id)
            ]
            return chat_messages.sort_values('data', ascending=True) if not chat_messages.empty else pd.DataFrame()
        else:
            return pd.DataFrame()
            
    except Exception as e:
        return pd.DataFrame()