"""
Script de diagnóstico para identificar problemas com fotos de perfil
"""

import os
import pandas as pd
import sys
from PIL import Image

# Ajustar o path para encontrar os módulos do aplicativo
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Importar funções do database
from app.utils.database import BASE_DIR, USERS_FILE, load_users

def diagnose_profile_photos():
    """Diagnostica problemas com fotos de perfil"""
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"USERS_FILE: {USERS_FILE}")
    
    # Verificar diretório de uploads
    uploads_dir = os.path.join(BASE_DIR, 'uploads')
    print(f"Diretório de uploads: {uploads_dir}")
    print(f"Diretório existe: {os.path.exists(uploads_dir)}")
    
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        print("Diretório de uploads criado")
    
    # Verificar diretório de fotos de perfil
    fotos_perfil_dir = os.path.join(uploads_dir, 'fotos_perfil')
    print(f"Diretório de fotos de perfil: {fotos_perfil_dir}")
    print(f"Diretório existe: {os.path.exists(fotos_perfil_dir)}")
    
    if not os.path.exists(fotos_perfil_dir):
        os.makedirs(fotos_perfil_dir)
        print("Diretório de fotos de perfil criado")
    
    # Listar arquivos no diretório de fotos de perfil
    if os.path.exists(fotos_perfil_dir):
        fotos = os.listdir(fotos_perfil_dir)
        print(f"Fotos no diretório: {fotos}")
    
    # Verificar arquivo de usuários
    print(f"Arquivo de usuários existe: {os.path.exists(USERS_FILE)}")
    
    # Carregar usuários
    try:
        users_df = load_users()
        print(f"Usuários carregados: {len(users_df)} registros")
        
        # Verificar campo foto_perfil
        if 'foto_perfil' in users_df.columns:
            print("Campo foto_perfil encontrado na tabela de usuários")
            
            # Verificar usuários com foto de perfil
            users_with_photo = users_df[users_df['foto_perfil'].notna() & (users_df['foto_perfil'] != '')]
            print(f"Usuários com foto de perfil: {len(users_with_photo)}")
            
            # Detalhes de cada usuário com foto
            for idx, user in users_with_photo.iterrows():
                foto_perfil = user['foto_perfil']
                user_id = user['id']
                print(f"\nUsuário {user_id} ({user['nome']}):")
                print(f"Caminho da foto: {foto_perfil}")
                
                # Verificar se o arquivo existe
                full_path = os.path.join(BASE_DIR, foto_perfil.replace('\\', '/'))
                print(f"Caminho completo: {full_path}")
                print(f"Arquivo existe: {os.path.exists(full_path)}")
                
                # Tentar abrir a imagem
                try:
                    if os.path.exists(full_path):
                        img = Image.open(full_path)
                        print(f"Imagem carregada com sucesso: {img.format}, {img.size}")
                except Exception as e:
                    print(f"Erro ao carregar imagem: {str(e)}")
        else:
            print("Campo foto_perfil NÃO encontrado na tabela de usuários")
    
    except Exception as e:
        print(f"Erro ao carregar usuários: {str(e)}")

if __name__ == "__main__":
    print("="*50)
    print("DIAGNÓSTICO DE FOTOS DE PERFIL")
    print("="*50)
    diagnose_profile_photos()
