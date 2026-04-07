# Fluxo de Movimentacoes

## Estoque

- `entrada`: compra, doacao ou ajuste positivo.
- `saida`: venda, perda ou ajuste negativo.
- `ajuste`: correcao manual ou inventario.

## Vendas

- Uma venda nasce com `itens`, `forma_pagamento` e `data_venda`.
- Ao confirmar a venda, o sistema calcula valor bruto, descontos, total, troco e gera a saida de estoque.

## Agendamento

- `fornecedor`: cadastro base.
- `conta_a_pagar`: obrigação financeira ligada ou nao a fornecedor.
- `entrega`: compromisso de recebimento.
- `compra`: rotina planejada para reposicao.

## Relatorios

- `balanco`: consolida entradas e saidas de caixa.
- `fiscal`: agrega receita, custo, despesas e tributos estimados.
- `estoque`: acompanha giro e saldo.
