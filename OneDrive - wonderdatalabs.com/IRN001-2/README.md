# 🌱 Coleta Seletiva Conectada - Itajubá

![GitHub last commit](https://img.shields.io/github/last-commit/Daniel-JMachado/Coleta_Seletiva)
![GitHub repo size](https://img.shields.io/github/repo-size/Daniel-JMachado/Coleta_Seletiva)
![GitHub language count](https://img.shields.io/github/languages/count/Daniel-JMachado/Coleta_Seletiva)
![GitHub top language](https://img.shields.io/github/languages/top/Daniel-JMachado/Coleta_Seletiva)

## 📋 Sobre o Projeto

O **Coleta Seletiva Conectada** é um sistema web desenvolvido para modernizar e otimizar o processo de coleta seletiva na cidade de Itajubá-MG. A plataforma conecta moradores, catadores de materiais recicláveis e administradores públicos em uma única solução integrada.

### 🎯 Objetivos

- **Facilitar** o agendamento de coletas seletivas pelos moradores
- **Otimizar** as rotas dos catadores de materiais recicláveis
- **Monitorar** estatísticas e métricas do sistema de coleta
- **Educar** a população sobre sustentabilidade e reciclagem
- **Integrar** todos os stakeholders em uma plataforma única

## 🚀 Funcionalidades

### 👥 Para Moradores
- ✅ Agendamento de coletas seletivas
- ✅ Acompanhamento do status das coletas
- ✅ Visualização de estatísticas pessoais
- ✅ Acesso a conteúdo educativo sobre reciclagem
- ✅ Sistema de notificações
- ✅ Perfil personalizado com foto

### ♻️ Para Catadores
- ✅ Visualização de coletas disponíveis
- ✅ Aceite e recusa de coletas
- ✅ Mapa interativo com localização das coletas
- ✅ Histórico de coletas realizadas
- ✅ Sistema de avaliação
- ✅ Gerenciamento de perfil

### 🔧 Para Administradores
- ✅ Dashboard completo com estatísticas
- ✅ Gerenciamento de usuários
- ✅ Análise de dados e métricas
- ✅ Monitoramento do sistema
- ✅ Relatórios detalhados
- ✅ Gestão de conteúdo educativo

## 🛠️ Tecnologias Utilizadas

- **Frontend**: Streamlit
- **Backend**: Python
- **Visualização**: Plotly, Matplotlib
- **Mapas**: Folium
- **Dados**: Pandas, CSV
- **Styling**: CSS personalizado
- **Autenticação**: Sistema customizado

## 📁 Estrutura do Projeto

```
Coleta_Seletiva/
├── app/
│   ├── pages/           # Páginas da aplicação
│   │   ├── admin.py     # Dashboard administrativo
│   │   ├── catador.py   # Interface do catador
│   │   ├── morador.py   # Interface do morador
│   │   └── login.py     # Sistema de login
│   ├── utils/           # Utilitários
│   │   ├── auth.py      # Autenticação
│   │   └── database.py  # Gerenciamento de dados
│   ├── data/            # Arquivos de dados
│   ├── css/             # Estilos personalizados
│   └── assets/          # Imagens e recursos
├── uploads/             # Arquivos enviados pelos usuários
├── app.py              # Aplicação principal
├── requirements.txt    # Dependências
└── README.md          # Este arquivo
```

## 🔧 Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- pip (gerenciador de pacotes do Python)

### 1. Clone o repositório
```bash
git clone https://github.com/Daniel-JMachado/Coleta_Seletiva.git
cd Coleta_Seletiva
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
```

### 3. Ative o ambiente virtual
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. Instale as dependências
```bash
pip install -r requirements.txt
```

### 5. Execute a aplicação
```bash
streamlit run app.py
```

### 6. Acesse a aplicação
Abra seu navegador e acesse: `http://localhost:8501`

## 👤 Usuários de Demonstração

### Moradores
- **Email**: `joao.silva@email.com` | **Senha**: `123456`
- **Email**: `maria.santos@email.com` | **Senha**: `123456`

### Catadores
- **Email**: `pedro.catador@email.com` | **Senha**: `123456`
- **Email**: `ana.coletora@email.com` | **Senha**: `123456`

### Administrador
- **Email**: `admin@itajuba.mg.gov.br` | **Senha**: `admin123`

## 📊 Principais Métricas

O sistema monitora automaticamente:
- Total de usuários cadastrados
- Número de coletas realizadas
- Taxa de conclusão das coletas
- Quantidade de material coletado
- Distribuição por bairros
- Avaliações dos catadores

## 🌍 Impacto Ambiental

O sistema contribui para:
- **Redução** do lixo enviado para aterros sanitários
- **Aumento** da taxa de reciclagem municipal
- **Geração** de renda para catadores
- **Educação** ambiental da população
- **Otimização** da logística de coleta

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é open source e está disponível sob a licença MIT.

## 📞 Contato

**Daniel José Machado**
- GitHub: [@Daniel-JMachado](https://github.com/Daniel-JMachado)
- Email: daniel.machado@wonderdatalabs.com

---

## 🏆 Desenvolvido para a Prefeitura de Itajubá-MG

Este projeto foi desenvolvido como uma solução inovadora para modernizar o sistema de coleta seletiva da cidade de Itajubá, promovendo sustentabilidade e inclusão social.

**Acesse o projeto**: [https://github.com/Daniel-JMachado/Coleta_Seletiva](https://github.com/Daniel-JMachado/Coleta_Seletiva)
