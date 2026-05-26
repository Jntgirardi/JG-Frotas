# RotaFácil - Sistema de Gestão de Transportes

O **RotaFácil** é um sistema moderno, leve e totalmente responsivo para gestão completa de pequenas frotas de caminhões e controle financeiro de rotas. Projetado com foco em alta legibilidade e facilidade de uso para celular e computador, o sistema permite o controle absoluto da empresa de forma simples e direta.

O projeto foi inteiramente estruturado seguindo os princípios de **Arquitetura Limpa (Clean Architecture)**, garantindo que a lógica de negócios permaneça isolada de detalhes técnicos como bancos de dados ou frameworks web.

---

## 🌟 Recursos Principais

- **Painel Geral (Dashboard):** Visão consolidada de Faturamento Bruto, Despesas Totais e Lucro Líquido Real, com gráficos interativos mensais.
- **Controle de Frota:** Cadastro de caminhões, gerenciamento e acompanhamento de status atual (Livre, Em Viagem, Oficina).
- **Registro de Viagens & Rotas:** Lançamento de fretes, gastos operacionais de rotas (Diesel, Pedágio e Outros) e cálculo automático de margem e lucro líquido da viagem em tempo real.
- **Controle Mecânico (Oficina):** Registro de despesas mecânicas com peças e manutenções, separadas por Preventivas e Corretivas.
- **Relatório Financeiro Completo:** Balanço consolidado de fluxo de caixa, demonstrativo composto de custos operacionais e tabela detalhada de lucratividade individual por caminhão.
- **Layout Adaptativo (Mobile/Desktop):** Barra lateral fixa intuitiva no computador e barra de navegação inferior estilo aplicativo móvel nativo no celular (com alvos de toque generosos de no mínimo `48px`).

---

## 🏗️ Camadas da Arquitetura Limpa

A estrutura do projeto está organizada em camadas concêntricas e desacopladas:

1. **Domínio (`domain/`):** Contém as entidades puras de negócio (`Caminhao`, `Viagem`, `Manutencao`, `Usuario`) desenvolvidas em Python puro, totalmente livre de dependências externas.
2. **Infraestrutura (`infrastructure/`):** Implementação física do banco de dados SQLite com SQLAlchemy e o padrão **Repository** (`repositories.py`) para isolamento total do acesso a dados (SQL).
3. **Aplicação (`application/`):** Contém os casos de uso e serviços orquestradores de fluxo (`AuthService`, `FleetService`, `TripService`, `FinanceService`).
4. **Apresentação (`app.py` & `templates/`):** Controlador web fino em Flask, segurança de sessões de cookies criptografadas e Views responsivas em HTML5, CSS Vanilla e Javascript Vanilla.

---

## 🔒 Segurança de Acesso

Para proteger os dados ao subir o sistema para a internet, implementamos uma política de segurança robusta:

1. **Criptografia de Senhas:** Todas as senhas operacionais são criptografadas antes de serem salvas utilizando o algoritmo seguro SHA-256 via `werkzeug.security`.
2. **Políticas de Sessão Segura:** As rotas financeiras e de frota são 100% protegidas por interceptores e cookies criptografados com Secret Keys.
3. **Ausência de Credenciais Padronizadas (Zero Default Passwords):**
   - Ao iniciar o sistema com um banco de dados vazio (em produção), o **RotaFácil** detecta automaticamente a ausência de administradores e exibe a tela de **Cadastro de Configuração Inicial** no primeiro acesso.
   - Isso permite que você defina suas próprias credenciais personalizadas de forma 100% segura diretamente no ar, sem expor nenhuma senha padrão no código público do GitHub.

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- Python 3.10 ou superior instalado.

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
   pip install flask flask-sqlalchemy
   ```

4. **Inicializar o Banco e Dados de Demonstração (Sandbox Local):**
   Execute o script inicializador para criar as tabelas físicas do SQLite localmente e gerar registros de teste (caminhões, viagens e manutenções) para visualização imediata do painel:
   ```bash
   python init_db.py
   ```
   *(Este script gera uma conta local padrão: Usuário: `admin` / Senha: `admin123` apenas para testes em máquina local).*

5. **Iniciar o Servidor:**
   ```bash
   python app.py
   ```
   Acesse [http://127.0.0.1:5000](http://127.0.0.1:5000) no seu navegador.
