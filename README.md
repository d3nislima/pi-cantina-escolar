# Aplicação web para controle de estoque de cantina escolar

## Sobre o projeto

Projeto Integrador em Computação I — UNIVESP (2026)

Desenvolvimento de uma aplicação web para controle de estoque da cantina escolar Delícias da Mamãe, localizada na ETEC Santa Isabel, no município de Santa Isabel - SP.

O sistema tem como objetivo substituir o controle manual atualmente utilizado, permitindo o registro de entradas e saídas de produtos, acompanhamento do estoque disponível e geração de relatórios.

## Integrantes

- Denis Alves de Lima
- Diego de Campos Sabor
- Diego Gonçalves do Prado
- Moara Cristina Beloni
- Onofre Silva do Nascimento
- Paulo José da Silva Neto

## Orientador

Prof. Ernesto Manuel Distinto Ufuene

## Tecnologias

- Python 3.12+
- Django 4.2
- Pydantic 2.12
- SQLite
- Git/GitHub

## Como instalar

### Pré-requisitos

- Python 3.10 ou superior instalado
- Git instalado

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

## Fluxo de trabalho no Git

### Branches

- **main** — versão estável do projeto. 
- **dev** — branch de desenvolvimento. 
- **feature/nome-da-tarefa** — branch individual de cada tarefa.

### Como trabalhar em uma tarefa

1. Atualize sua dev local:
```bash
git checkout dev
git pull origin dev
```

2. Crie sua branch a partir da dev:
```bash
git checkout -b feature/nome-da-tarefa
```

3. Faça suas alterações e commits:
```bash
git add .
git commit -m "tipo: descrição curta do que foi feito"
```

4. Envie para o GitHub:
```bash
git push origin feature/nome-da-tarefa
```

5. Abra um Pull Request no GitHub de `feature/nome-da-tarefa` para `dev`.

6. Outro membro do grupo revisa e aprova o merge.

### Convenção de commits

Usar o prefixo para identificar o tipo de alteração:

- **feat:** nova funcionalidade (ex: `feat: criar model Produto`)
- **fix:** correção de bug (ex: `fix: corrigir calculo do estoque`)
- **docs:** documentação (ex: `docs: atualizar README`)
- **style:** formatação, CSS (ex: `style: ajustar layout do dashboard`)
- **refactor:** refatoração sem mudar funcionalidade
- **test:** adição ou correção de testes

## Estrutura do projeto

```
pi-cantina-escolar/
├── setup.sh                 # Script de setup automático
├── README.md                # Este arquivo
├── .gitignore               # Arquivos ignorados pelo Git
├── manage.py            # Comando principal do Django
    ├── requirements.txt     # Dependências do projeto
    ├── Cantina/             # Configurações (settings, urls)
    ├── apps/
    │   ├── core/            # App base (dashboard, templates)
    │   ├── estoque/         # Cadastro de produtos e movimentações
    │   ├── vendas/          # Registro de vendas
    │   ├── relatorios/      # Relatórios e indicadores
    │   └── agendamento/     # Fornecedores e compras
    ├── templates/           # Templates HTML
    ├── static/              # CSS e arquivos estáticos
    ├── docs/                # Documentação técnica
    └── Sprints/             # Planejamento de sprints
```