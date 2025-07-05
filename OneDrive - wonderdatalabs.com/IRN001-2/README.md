# Coleta Seletiva Conectada - POC

## Descrição
Prova de Conceito (POC) para um sistema de "Coleta Seletiva Conectada" desenvolvida para a Prefeitura de Itajubá. O sistema conecta catadores de materiais recicláveis e moradores, facilitando o processo de coleta seletiva na cidade.

## Funcionalidades

### Para Moradores:
- Solicitar coleta de material reciclável
- Visualizar catadores disponíveis no bairro
- Acompanhar histórico de coletas
- Acessar conteúdo educativo sobre reciclagem

### Para Catadores:
- Visualizar solicitações de coleta em suas áreas
- Aceitar/recusar solicitações
- Registrar coletas realizadas
- Ver rotas por bairro
- Acessar conteúdo educativo

### Para Administradores (Prefeitura):
- Cadastrar novos catadores e moradores
- Visualizar estatísticas gerais
- Gerenciar usuários
- Adicionar conteúdo educativo

## Tecnologias Utilizadas
- Python 3.8+
- Streamlit para interface web
- Arquivos CSV/JSON para armazenamento de dados
- Pandas para manipulação de dados

## Instalação e Execução

1. Clone o repositório
2. Crie um ambiente virtual (opcional, mas recomendado):
```
python -m venv venv
```
3. Ative o ambiente virtual:
   - Windows:
   ```
   venv\Scripts\activate
   ```
   - Linux/MacOS:
   ```
   source venv/bin/activate
   ```
4. Instale as dependências:
```
pip install -r requirements.txt
```
5. Execute o aplicativo:

   - Porta padrão (8501):
   ```
   streamlit run app.py
   ```
   
   - Porta alternativa (8502):
   ```
   streamlit run app.py --server.port 8502
   ```
   
   - Usando scripts auxiliares (porta 8502):
     - PowerShell: `.\iniciar_app.ps1`
     - Batch: `iniciar_app.bat`
     - Python: `python run_app.py`

## Estrutura do Projeto
```
IRN001-2/
│
├── app.py                 # Arquivo principal da aplicação
├── requirements.txt       # Dependências do projeto
├── README.md              # Documentação
│
├── app/                   # Diretório da aplicação
│   ├── pages/             # Páginas da interface
│   │   ├── __init__.py
│   │   ├── login.py       # Página de login
│   │   ├── morador.py     # Dashboard do morador
│   │   ├── catador.py     # Dashboard do catador
│   │   └── admin.py       # Dashboard do administrador
│   │
│   ├── utils/             # Utilitários
│   │   ├── __init__.py
│   │   ├── auth.py        # Funções de autenticação
│   │   └── database.py    # Funções de acesso a dados
│   │
│   ├── data/              # Arquivos de dados
│   │   ├── usuarios.csv   # Dados dos usuários
│   │   ├── coletas.csv    # Dados das coletas
│   │   └── notificacoes.csv # Notificações
│   │
│   ├── content/           # Conteúdo educativo
│   │   └── reciclagem.json # Informações sobre reciclagem
│   │
│   └── css/               # Estilos
│       └── style.css      # CSS principal
```

## Credenciais de Teste
- **Morador**
  - Email: morador@teste.com
  - Senha: 123

- **Catador**
  - Email: catador@teste.com
  - Senha: 123

- **Administrador**
  - Email: admin@prefeitura.itajuba.gov.br
  - Senha: 123

## Melhorias Futuras
- Implementação de banco de dados relacional ou NoSQL
- Sistema de autenticação mais seguro
- Integração com mapas para visualização de rotas
- Aplicativo móvel para usuários
- Sistema de gamificação para incentivar a reciclagem
- Métricas ambientais de impacto positivo

## Autor
Desenvolvido como projeto acadêmico para a disciplina de Ciências do Ambiente (IRN001) da Universidade Federal de Itajubá.
