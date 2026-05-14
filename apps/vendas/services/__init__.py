from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.estoque.models.movimento import MovimentoEstoque
from apps.estoque.models.produto import Produto
from apps.vendas.models.venda import ItemVenda, JanelaAtendimento, Venda


class EstoqueInsuficienteError(Exception):
    """
    Levantada quando um produto não tem estoque suficiente para a venda.
    Carrega o nome do produto e os valores envolvidos para exibição na view.
    """
    def __init__(self, produto_nome: str, disponivel: Decimal, solicitado: Decimal):
        self.produto_nome = produto_nome
        self.disponivel = disponivel
        self.solicitado = solicitado
        super().__init__(
            f"Estoque insuficiente para '{produto_nome}': "
            f"disponível {disponivel}, solicitado {solicitado}."
        )


def _validar_estoque(itens_carrinho: list[dict]) -> None:
    """
    Percorre todos os itens do carrinho e levanta EstoqueInsuficienteError
    no primeiro produto com estoque insuficiente.

    Faz isso ANTES de abrir a transaction para não segurar lock desnecessariamente.
    """
    for item in itens_carrinho:
        produto = Produto.objects.get(pk=item["produto_id"])
        quantidade = Decimal(str(item["quantidade"]))
        if produto.estoque_atual < quantidade:
            raise EstoqueInsuficienteError(
                produto_nome=produto.nome,
                disponivel=produto.estoque_atual,
                solicitado=quantidade,
            )


def realizar_venda(
    itens_carrinho: list[dict],
    forma_pagamento: str,
    modo_atendimento: str = "rapido",
    janela: JanelaAtendimento | None = None,
    valor_recebido: Decimal | None = None,
) -> Venda:
    """
    Cria uma Venda completa: valida estoque, persiste Venda + ItemVenda +
    MovimentoEstoque e atualiza estoque_atual de cada produto.

    Levanta EstoqueInsuficienteError antes de gravar qualquer coisa se
    algum produto não tiver estoque suficiente.

    Todo o trabalho de escrita é feito dentro de transaction.atomic() para
    garantir consistência: ou tudo é gravado, ou nada é.
    """
    # Validação fora da transaction — falha rápido, sem custo de rollback
    _validar_estoque(itens_carrinho)

    with transaction.atomic():
        valor_total = sum(
            Decimal(str(item["subtotal"])) for item in itens_carrinho
        )
        troco = None
        if valor_recebido is not None and forma_pagamento == "dinheiro":
            troco = valor_recebido - valor_total

        venda = Venda.objects.create(
            forma_pagamento=forma_pagamento,
            janela_atendimento=janela,
            modo_atendimento=modo_atendimento,
            valor_bruto=valor_total,
            valor_total=valor_total,
            valor_recebido=valor_recebido,
            troco=troco,
            vendido_em=timezone.now(),
        )

        for item in itens_carrinho:
            produto = Produto.objects.get(pk=item["produto_id"])
            quantidade = Decimal(str(item["quantidade"]))
            preco = Decimal(str(item["preco_unitario"]))

            ItemVenda.objects.create(
                venda=venda,
                produto=produto,
                quantidade=quantidade,
                valor_unitario=preco,
                valor_total=quantidade * preco,
            )

            MovimentoEstoque.objects.create(
                produto=produto,
                operacao="saida",
                origem="venda",
                quantidade=quantidade,
                valor_unitario=preco,
                saldo_antes=produto.estoque_atual,
                saldo_depois=produto.estoque_atual - quantidade,
                data_movimento=venda.vendido_em,
            )

            produto.estoque_atual -= quantidade
            produto.save(update_fields=["estoque_atual", "atualizado_em"])

        return venda


def realizar_venda_pedido(pedido) -> Venda:
    """
    Wrapper para retirada de pedido antecipado.
    Constrói o carrinho no formato esperado por realizar_venda() a partir
    dos itens do PedidoAntecipado, reutilizando toda a lógica de validação.
    """
    itens_carrinho = [
        {
            "produto_id": item.produto_id,
            "quantidade": str(item.quantidade),
            "preco_unitario": str(item.valor_unitario),
            "subtotal": str(item.valor_total),
        }
        for item in pedido.itens.select_related("produto").all()
    ]

    return realizar_venda(
        itens_carrinho=itens_carrinho,
        forma_pagamento=pedido._forma_pagamento,  # injetado pela view antes de chamar
        modo_atendimento="pedido_antecipado",
        janela=pedido.janela_atendimento,
        valor_recebido=pedido._valor_recebido,    # idem
    )