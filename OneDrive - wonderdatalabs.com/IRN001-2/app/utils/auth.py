"""
Módulo de autenticação do sistema Coleta Seletiva Conectada

Este módulo contém funções para autenticação, login e verificação de permissões de usuários.
"""

import streamlit as st
import pandas as pd
import os
import hashlib
import json
from datetime import datetime

from app.utils.database import load_users, save_user, check_user_exists

# Caminho para o arquivo de usuários
USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'usuarios.csv')
# Caminho para o arquivo de sessão persistente
SESSION_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'session.json')

def hash_password(password):
    """
    Cria um hash da senha fornecida para armazenamento seguro.
    
    Args:
        password (str): Senha em texto plano
        
    Returns:
        str: Hash da senha
    """
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(email, password, user_type=None):
    """
    Autentica um usuário com base no email, senha e tipo opcional.
    
    Args:
        email (str): Email do usuário
        password (str): Senha do usuário
        user_type (str, optional): Tipo de usuário (morador, catador, admin)
        
    Returns:
        tuple: (bool, dict) - Sucesso da autenticação e dados do usuário
    """
    try:
        # Carrega os usuários do arquivo CSV
        users_df = load_users()
        
        if users_df is None or users_df.empty:
            st.error("Erro ao carregar usuários. Verifique o arquivo de dados.")
            return False, None
        
        # Gera o hash da senha fornecida
        hashed_password = hash_password(password)
        
        # Filtra o DataFrame para encontrar o usuário
        user_query = users_df[(users_df['email'] == email) & (users_df['senha'] == hashed_password)]
        
        # Se tipo de usuário foi especificado, filtra também por tipo
        if user_type:
            user_query = user_query[user_query['tipo'] == user_type]
        
        # Verifica se encontrou o usuário
        if not user_query.empty:
            # Converte a linha do DataFrame para um dicionário
            user_data = user_query.iloc[0].to_dict()
            return True, user_data
        else:
            return False, None
    
    except Exception as e:
        st.error(f"Erro na autenticação: {str(e)}")
        return False, None

def save_session(user_data):
    """
    Salva os dados da sessão em um arquivo para persistência.
    
    Args:
        user_data (dict): Dados do usuário logado
    """
    try:
        session_data = {
            'authenticated': True,
            'user_type': user_data['tipo'],
            'user_data': user_data
        }
        
        with open(SESSION_FILE, 'w') as f:
            json.dump(session_data, f)
    except Exception as e:
        st.warning(f"Não foi possível salvar a sessão: {e}")

def load_session():
    """
    Carrega os dados da sessão salva anteriormente.
    
    Returns:
        bool: True se a sessão foi carregada com sucesso
    """
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'r') as f:
                session_data = json.load(f)
                
            st.session_state.authenticated = session_data.get('authenticated', False)
            st.session_state.user_type = session_data.get('user_type')
            st.session_state.user_data = session_data.get('user_data')
            return True
        return False
    except Exception as e:
        st.warning(f"Não foi possível carregar a sessão: {e}")
        return False

def clear_session():
    """
    Remove o arquivo de sessão persistente.
    """
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
    except Exception as e:
        st.warning(f"Não foi possível limpar a sessão: {e}")

def login(email, password, user_type=None):
    """
    Realiza o login do usuário no sistema e atualiza o estado da sessão.
    
    Args:
        email (str): Email do usuário
        password (str): Senha do usuário
        user_type (str, optional): Tipo de usuário (morador, catador, admin)
        
    Returns:
        bool: Verdadeiro se o login foi bem-sucedido
    """
    success, user_data = authenticate(email, password, user_type)
    
    if success and user_data:
        # Atualiza o estado da sessão
        st.session_state.authenticated = True
        st.session_state.user_type = user_data['tipo']
        st.session_state.user_data = user_data
        
        # Salva a sessão para persistência
        save_session(user_data)
        
        # Registra o último login (opcional)
        users_df = load_users()
        users_df.loc[users_df['email'] == email, 'ultimo_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        users_df.to_csv(USERS_FILE, index=False)
        
        return True
    else:
        return False

def logout():
    """
    Realiza o logout do usuário, limpando o estado da sessão.
    """
    st.session_state.authenticated = False
    st.session_state.user_type = None
    st.session_state.user_data = None
    
    # Remove o arquivo de sessão persistente
    clear_session()

def check_authentication():
    """
    Verifica se o usuário está autenticado na sessão atual.
    
    Returns:
        bool: Verdadeiro se o usuário está autenticado
    """
    return st.session_state.get('authenticated', False)

def register_user(nome, email, senha, tipo, bairro, telefone=None, areas_atuacao=None, status="ativo"):
    """
    Registra um novo usuário no sistema.
    
    Args:
        nome (str): Nome completo do usuário
        email (str): Email do usuário (usado como identificador único)
        senha (str): Senha do usuário (será armazenada como hash)
        tipo (str): Tipo de usuário (morador, catador, admin)
        bairro (str): Bairro do usuário
        telefone (str, optional): Número de telefone
        areas_atuacao (str, optional): Áreas de atuação (para catadores)
        status (str, optional): Status do usuário (ativo, inativo)
        
    Returns:
        bool: Verdadeiro se o registro foi bem-sucedido
    """
    try:
        # Verifica se o usuário já existe
        if check_user_exists(email):
            return False, "Usuário já existe com este email"
        
        # Cria um novo usuário
        new_user = {
            'id': pd.read_csv(USERS_FILE)['id'].max() + 1 if os.path.exists(USERS_FILE) and not pd.read_csv(USERS_FILE).empty else 1,
            'nome': nome,
            'email': email,
            'senha': hash_password(senha),
            'tipo': tipo,
            'bairro': bairro,
            'telefone': telefone if telefone else "",
            'areas_atuacao': areas_atuacao if areas_atuacao else "",
            'data_cadastro': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ultimo_login': "",
            'status': status
        }
        
        # Salva o usuário
        result, message = save_user(new_user)
        return result, message
    
    except Exception as e:
        return False, f"Erro ao registrar usuário: {str(e)}"

def reset_password(email, new_password):
    """
    Redefine a senha de um usuário.
    
    Args:
        email (str): Email do usuário
        new_password (str): Nova senha
        
    Returns:
        bool: Verdadeiro se a redefinição foi bem-sucedida
    """
    try:
        # Carrega os usuários
        users_df = load_users()
        
        # Verifica se o usuário existe
        if users_df[users_df['email'] == email].empty:
            return False
        
        # Atualiza a senha
        users_df.loc[users_df['email'] == email, 'senha'] = hash_password(new_password)
        users_df.to_csv(USERS_FILE, index=False)
        
        return True
    
    except Exception as e:
        st.error(f"Erro ao redefinir senha: {str(e)}")
        return False
