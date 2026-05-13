# Aplicação web para controle de estoque de cantina escolar

## Sobre o projeto

Projeto Integrador em Computação I — UNIVESP (2026)

Desenvolvimento de uma aplicação web para controle de estoque da cantina escolar **Delícias da Mamãe**, localizada na ETEC Santa Isabel, no município de Santa Isabel - SP.

O sistema substitui o controle manual atualmente utilizado, permitindo o registro de entradas e saídas de produtos, acompanhamento do estoque disponível, registro de vendas e geração de relatórios.

## Integrantes

- Denis Alves de Lima
- Diego de Campos Sabor
- Diego Gonçalves do Prado
- Moara Cristina Beloni
- Onofre Silva do Nascimento
- Paulo José da Silva Neto

**Orientador:** Prof. Ernesto Manuel Distinto Ufuene

## Tecnologias

- Python 3.12+
- Django 4.2.29
- Pydantic 2.12.5
- SQLite
- Git/GitHub

## Como instalar

**Pré-requisitos:** Python 3.10+ e Git instalados.

### Setup automático

```bash
git clone https://github.com/d3nislima/pi-cantina-escolar.git
cd pi-cantina-escolar
chmod +x setup.sh
./setup.sh
```

### Setup manual

```bash
git clone https://github.com/d3nislima/pi-cantina-escolar.git
cd pi-cantina-escolar
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```

Acesse http://127.0.0.1:8000/ no navegador.

## Estrutura do projeto

```
pi-cantina-escolar/
├── setup.sh                 # Script de setup automático
├── manage.py                # Comando principal do Django
├── requirements.txt         # Dependências do projeto
├── README.md
├── .gitignore
├── Cantina/                 # Configurações Django (settings, urls)
├── apps/
│   ├── core/                # Dashboard e base
│   ├── estoque/             # Produtos e movimentações
│   ├── vendas/              # Registro de vendas
│   ├── relatorios/          # Relatórios e indicadores
│   └── agendamento/         # Fornecedores e compras
├── templates/               # Templates HTML
├── static/                  # CSS e arquivos estáticos
└── docs/                    # Documentação técnica e sprints
```

## Módulos

| Módulo | Descrição | Status |
|--------|-----------|--------|
| `core` | Dashboard com resumo do dia, estoque crítico e acesso rápido | ✅ Implementado |
| `estoque` | CRUD de produtos e categorias, movimentações (entrada/saída/ajuste), busca por nome | ✅ Implementado |
| `vendas` | Nova venda com carrinho, janelas de atendimento configuráveis, histórico de vendas | ✅ Implementado |
| `relatorios` | Hub de relatórios, log de movimentações de estoque, histórico de vendas | ✅ Implementado |
| `agendamento` | Pedido antecipado por aluno: agendamento, retirada e cancelamento | ✅ Implementado |

## Funcionalidades

### Estoque
- Cadastro de produtos com categorias e unidade de medida
- Entrada de estoque com atualização automática de preço de custo (compras)
- Saídas e ajustes manuais de estoque
- Alerta visual de produtos com estoque crítico no dashboard

### Vendas
- Fluxo de nova venda com carrinho em sessão
- Janelas de atendimento configuráveis pelo admin
- Detecção automática da janela pelo horário
- Pagamento em dinheiro (com troco) ou outros meios
- Histórico de vendas com total e itens

### Pedido Antecipado
- Alunos podem agendar pedidos antecipadamente
- Pedidos expiram automaticamente ao final da janela de atendimento do dia
- Cancelamento e retirada registrados com data e hora

### Relatórios
- Log completo de movimentações de estoque
- Histórico de vendas realizadas
- Dashboard com faturamento do dia e produtos mais vendidos

### Configurações
- Cadastro e ativação de janelas de atendimento
- Gerenciamento de categorias de produtos

## Fluxo de trabalho no Git

### Branches

- **main** — versão estável
- **dev** — branch de desenvolvimento
- **feature/nome-da-tarefa** — branch individual de cada tarefa

### Como trabalhar em uma tarefa

```bash
# 1. Atualize a dev local
git checkout dev
git pull origin dev

# 2. Crie sua branch
git checkout -b feature/nome-da-tarefa

# 3. Faça commits
git add .
git commit -m "tipo: descrição curta"

# 4. Envie para o GitHub
git push origin feature/nome-da-tarefa
```

Abra um Pull Request de `feature/nome-da-tarefa` para `dev` e solicite revisão de outro membro.

### Convenção de commits

| Prefixo | Uso |
|---------|-----|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `docs:` | Documentação |
| `style:` | Formatação, CSS |
| `refactor:` | Refatoração sem mudança de comportamento |
| `test:` | Adição ou correção de testes |
