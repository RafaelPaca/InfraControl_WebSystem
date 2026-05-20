# InfraControl - Gestão de Chamados de Manutenção com IA 🛠️🤖

O **InfraControl** é um sistema web moderno e responsivo desenvolvido para facilitar o fluxo completo de gestão de chamados de manutenção corporativos (abertura, atribuição, atendimento e conclusão). O seu grande diferencial é a utilização de **Inteligência Artificial (Machine Learning)** para prever o tempo estimado de conclusão de cada chamado, com base no histórico dos técnicos, na prioridade e na categoria da solicitação.

## 🚀 Principais Funcionalidades

- **Múltiplos Perfis de Acesso:** Usuário, Técnico, Gestor e Administrador, cada um com dashboards e permissões exclusivas.
- **Abertura Inteligente de Chamados:** Formulário dinâmico com lógica encadeada. Os tipos de problema exibidos mudam dinamicamente conforme a categoria da manutenção.
- **Previsão de Tempo com Machine Learning:** Modelo `RandomForestRegressor` (via Scikit-Learn) que prediz em horas o tempo de conclusão do chamado assim que ele é aberto.
- **Hierarquia Técnica (Líderes e Operacionais):** O gestor aciona equipes específicas (ex: Hidráulica, Elétrica) e designa um técnico temporariamente como *Líder*, sendo ele o único capaz de iniciar e concluir oficialmente o serviço.
- **Acessibilidade Universal (WCAG):** Foco via teclado, alto contraste, tags semânticas ARIA e um design intuitivo (Glassmorphism + Dark Mode).
- **Dashboards Gerenciais:** Gráficos interativos renderizados via Chart.js mostrando volume de chamados por categoria e status atual.

## 🛠️ Stack Tecnológico

### Backend
- **Python 3+**
- **Flask** (Framework Web e Rotas API)
- **Flask-SQLAlchemy** (ORM para persistência de dados)
- **Flask-Login** (Gestão de sessão de usuários)
- **SQLite** (Banco de dados inicial - facilmente migrável)
- **Pytest** (Testes unitários)

### Machine Learning
- **Scikit-Learn** (Treinamento do `RandomForestRegressor` para previsão temporal)
- **Pandas / Numpy** (Processamento de dados e encoders)

### Frontend
- **HTML5 & Vanilla CSS3** (Estilo moderno com CSS Variables, Flexbox, CSS Grid e Glassmorphism)
- **Vanilla JavaScript** (Interações de DOM dinâmico e Fetch API para integração com endpoints)
- **Chart.js** (Visualização gráfica de métricas de negócio)
- **Jest / JSDOM** (Testes unitários de interações da interface)

## ⚙️ Como Instalar e Rodar o Projeto Localmente

1. **Clone o Repositório:**
```bash
git clone https://github.com/RafaelPaca/InfraControl_WebSystem.git
cd InfraControl_WebSystem
```

2. **Crie e Ative o Ambiente Virtual (Python):**
```powershell
python -m venv venv
# No Windows
.\venv\Scripts\activate
# No Linux/Mac
source venv/bin/activate
```

3. **Instale as Dependências (Python & Node):**
```bash
pip install flask flask-sqlalchemy flask-login scikit-learn pytest pandas numpy Werkzeug
npm install
```

4. **Prepare o Banco de Dados e o Modelo de IA (Seed):**
*O script abaixo recriará as tabelas, populando os Setores, criando o Admin padrão e treinando o modelo de regressão.*
```bash
python seed.py
```

5. **Inicie o Servidor Local:**
```bash
python app.py
```

6. **Acesse a Aplicação:**
Abra o navegador e acesse: `http://127.0.0.1:5000/`

## 🔐 Acesso Administrativo Padrão
Após rodar o script de *seed*, um usuário mestre é criado automaticamente para que você possa manipular cargos (promover novos cadastros para Técnicos ou Gestores).

- **E-mail:** `admin@infracontrol.com`
- **Senha:** `infra123`

---
*Desenvolvido como projeto focado em integrar desenvolvimento web ágil, IA corporativa e rigorosas boas práticas de UI/UX.*
