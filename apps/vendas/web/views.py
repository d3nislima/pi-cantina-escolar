from decimal import Decimal

from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import ListView

from apps.estoque.models.movimento import MovimentoEstoque
from apps.estoque.models.produto import Produto
from apps.vendas.models.venda import ItemVenda, JanelaAtendimento, Venda


def _janela_atual():
    agora = timezone.localtime(timezone.now()).time()
    return JanelaAtendimento.objects.filter(
        ativo=True,
        hora_inicio__lte=agora,
        hora_fim__gte=agora,
    ).first()


class VendaListView(ListView):
    model = Venda
    template_name = "vendas/venda_list.html"
    context_object_name = "vendas"
    ordering = ["-vendido_em"]
    paginate_by = 50


class NovaVendaView(View):
    template_name = "vendas/venda_nova.html"

    def get(self, request):
        carrinho = request.session.get("carrinho", [])
        produtos = Produto.objects.filter(ativo=True).order_by("nome")
        janelas = JanelaAtendimento.objects.filter(ativo=True)
        janela_atual = _janela_atual()
        total = sum(Decimal(str(item["subtotal"])) for item in carrinho)

        return render(request, self.template_name, {
            "produtos": produtos,
            "carrinho": carrinho,
            "janelas": janelas,
            "janela_atual_id": janela_atual.pk if janela_atual else None,
            "total": total,
            "formas_pagamento": Venda.PAGAMENTO_CHOICES,
            "modos_atendimento": Venda.MODO_CHOICES,
        })


class AdicionarItemView(View):
    def post(self, request):
        produto_id = request.POST.get("produto_id")
        quantidade = Decimal(request.POST.get("quantidade", "1"))

        try:
            produto = Produto.objects.get(pk=produto_id, ativo=True)
        except Produto.DoesNotExist:
            return redirect("venda-create")

        carrinho = request.session.get("carrinho", [])

        for item in carrinho:
            if item["produto_id"] == produto.pk:
                item["quantidade"] = str(Decimal(str(item["quantidade"])) + quantidade)
                item["subtotal"] = str(Decimal(str(item["quantidade"])) * Decimal(str(item["preco_unitario"])))
                break
        else:
            carrinho.append({
                "produto_id": produto.pk,
                "nome": produto.nome,
                "preco_unitario": str(produto.preco_venda),
                "quantidade": str(quantidade),
                "subtotal": str(produto.preco_venda * quantidade),
            })

        request.session["carrinho"] = carrinho
        return redirect("venda-create")


class RemoverItemView(View):
    def post(self, request):
        produto_id = int(request.POST.get("produto_id"))
        carrinho = request.session.get("carrinho", [])
        request.session["carrinho"] = [i for i in carrinho if i["produto_id"] != produto_id]
        return redirect("venda-create")


class FinalizarVendaView(View):
    def post(self, request):
        carrinho = request.session.get("carrinho", [])
        if not carrinho:
            return redirect("venda-create")

        forma_pagamento = request.POST.get("forma_pagamento")
        janela_id = request.POST.get("janela_atendimento")
        modo = request.POST.get("modo_atendimento", "rapido")
        valor_recebido = request.POST.get("valor_recebido") or None

        janela = None
        if janela_id:
            try:
                janela = JanelaAtendimento.objects.get(pk=janela_id)
            except JanelaAtendimento.DoesNotExist:
                pass

        valor_total = sum(Decimal(str(item["subtotal"])) for item in carrinho)
        troco = None
        if valor_recebido and forma_pagamento == "dinheiro":
            troco = Decimal(str(valor_recebido)) - valor_total

        venda = Venda.objects.create(
            forma_pagamento=forma_pagamento,
            janela_atendimento=janela,
            modo_atendimento=modo,
            valor_bruto=valor_total,
            valor_total=valor_total,
            valor_recebido=Decimal(str(valor_recebido)) if valor_recebido else None,
            troco=troco,
            vendido_em=timezone.now(),
        )

        for item in carrinho:
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
            produto.save()

        request.session["carrinho"] = []
        return redirect("venda-list")
