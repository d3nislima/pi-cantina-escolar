# Fluxo de Movimentacoes

## Estoque

- `entrada`: compra, doacao ou ajuste positivo.
- `saida`: venda, perda ou ajuste negativo.
- `ajuste`: correcao manual ou inventario.

## Vendas

- Uma venda nasce com `itens`, `forma_pagamento`, `vendido_em`, `janela_atendimento` e `modo_atendimento`.
- `vendido_em` guarda o instante real da venda para permitir leitura precisa em relatorios.
- `janela_atendimento` marca se a venda ocorreu em recreio, almoco, fora de intervalo ou evento especial.
- `modo_atendimento` permite otimizar a tela para venda rapida, pedido antecipado ou fluxo normal.
- Ao confirmar a venda, o sistema calcula valor bruto, descontos, total, troco e gera a saida de estoque.
- O cadastro de item aceita `produto_id`, `produto_codigo` ou `produto_nome`, para reduzir digitação no atendimento.

## Agendamento

- `fornecedor`: cadastro base.
- `conta_a_pagar`: obrigação financeira ligada ou nao a fornecedor.
- `entrega`: compromisso de recebimento.
- `compra`: rotina planejada para reposicao.

## Relatorios

- `balanco`: consolida entradas e saidas de caixa.
- `fiscal`: agrega receita, custo, despesas e tributos estimados.
- `estoque`: acompanha giro e saldo.
