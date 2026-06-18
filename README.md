# RotaFácil - Sistema de Gestão de Transportes

O **RotaFácil** é um sistema moderno, leve e totalmente responsivo para gestão completa de pequenas frotas de caminhões e controle financeiro de rotas. Projetado com foco em alta legibilidade e facilidade de uso para celular e computador, o sistema permite o controle absoluto da empresa de forma simples e direta.

O projeto foi inteiramente estruturado seguindo os princípios de **Arquitetura Limpa (Clean Architecture)**, garantindo que a lógica de negócios permaneça isolada de detalhes técnicos como bancos de dados ou frameworks web.

---

## 🌟 Recursos Principais

- **Painel Geral (Dashboard):** Visão consolidada de Faturamento Bruto, Despesas Totais e Lucro Líquido Real, com gráficos interativos mensais.
- **Controle de Frota:** Cadastro de caminhões, gerenciamento e acompanhamento de status atual (Livre, Em Viagem, Oficina).
- **Gestão Contextualizada de Viagens:** O registro, a edição e a exclusão de viagens são realizados diretamente do painel de cada veículo (placa) e da tela inicial, sem uma aba global genérica. A comissão (12%) e os impostos (10%) são calculados em tempo real na interface.
- **Tela de Carregamento Premium (UX):** Interceptação global de formulários e cliques de navegação para exibir um overlay escuro com efeito de *glassmorphism* e um spinner animado. Isso garante um visual de alta qualidade e evita que usuários leigos achem que o sistema travou.
- **Controle Mecânico (Oficina):** Registro de despesas mecânicas com peças e manutenções, separadas por Preventivas e Corretivas.
- **Relatório Financeiro Completo:** Balanço consolidado de fluxo de caixa, demonstrativo composto de custos operacionais e tabela detalhada de lucratividade individual por caminhão.
- **Layout Adaptativo (Mobile/Desktop):** Barra lateral fixa intuitiva no computador e barra de navegação inferior estilo aplicativo móvel nativo no celular (com alvos de toque generosos de no mínimo `48px`).

---

## 🏗️ Camadas da Arquitetura Limpa

A estrutura do projeto está organizada em camadas concêntricas e desacopladas:

1. **Domínio (`domain/`):** Contém as entidades puras de negócio (`Caminhao`, `Viagem`, `Manutencao`, `Usuario`) desenvolvidas em Python puro, totalmente livre de dependências externas.
2. **Infraestrutura (`infrastructure/`):** Implementação física do banco de dados (SQLite/PostgreSQL) com SQLAlchemy e o padrão **Repository** (`repositories.py`) para isolamento total do acesso a dados.
3. **Aplicação (`application/`):** Contém os casos de uso e serviços orquestradores de fluxo (`AuthService`, `FleetService`, `TripService`, `FinanceService`).
4. **Apresentação (`app.py` & `templates/`):** Controlador web fino em Flask, segurança de sessões de cookies criptografadas e Views responsivas em HTML5, CSS Vanilla e Javascript Vanilla.

---

## 🔒 Segurança & DevSecOps

Para proteger os dados e garantir a estabilidade do sistema ao implantar em nuvem, o **RotaFácil** possui:

1. **Criptografia de Senhas:** Todas as senhas operacionais são criptografadas antes de serem salvas utilizando o algoritmo seguro SHA-256 via `werkzeug.security`.
2. **Políticas de Sessão Segura:** As rotas financeiras e de frota são 100% protegidas por interceptores e cookies criptografados com Secret Keys.
3. **Ausência de Credenciais Padronizadas (Zero Default Passwords):**
   - Ao iniciar o sistema com um banco de dados vazio (em produção), o **RotaFácil** detecta automaticamente a ausência de administradores e exibe a tela de **Cadastro de Configuração Inicial** no primeiro acesso.
4. **Proteção de Rotas & Validação:** Todos os acessos não autenticados a páginas internas são bloqueados, com tratamento de exceções para parâmetros inválidos e restrições rígidas no banco (ex: placas de caminhão duplicadas).

---

## 🧪 Testes Automatizados & CI/CD

O projeto conta com testes automatizados integrados a uma esteira de entrega contínua:

- **Suíte de Testes (Python `unittest`):** Valida a segurança das rotas (bloqueio de usuários anônimos), integridade dos dados (unicidade de placa), regras de cálculo de comissão/imposto de viagens e redirecionamento seguro para parâmetros inválidos.
- **GitHub Actions (CI):** Pipeline configurado em `.github/workflows/ci.yml` que roda automaticamente toda a suíte de testes em cada push ou pull request na branch principal `main`.

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- Python 3.10 ou superior instalado.
- Banco SQLite local ou PostgreSQL (compatível com Supabase).

### Passo a Passo

1. **Clonar o Repositório:**
   ```bash
   git clone https://github.com/Jntgirardi/J-G-Frotas.git
   cd J-G-Frotas
   ```

2. **Configurar o Ambiente Virtual (venv):**
   ```bash
   python -m venv .venv
   # No Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # No Linux/macOS:
   source .venv/bin/activate
   ```

3. **Instalar as Dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicializar o Banco e Dados de Demonstração (Sandbox Local):**
   Execute o script inicializador para criar as tabelas físicas do SQLite localmente e gerar registros de teste (caminhões, viagens e manutenções) para visualização imediata do painel:
   ```bash
   python init_db.py
   ```
   *(Este script gera uma conta local padrão: Usuário: `admin` / Senha: `admin123` apenas para testes em máquina local).*

5. **Executar a Suíte de Testes:**
   ```bash
   python -m unittest discover -s tests
   ```

6. **Iniciar o Servidor:**
   ```bash
   python app.py
   ```
   Acesse [http://127.0.0.1:5000](http://127.0.0.1:5000) no seu navegador.
