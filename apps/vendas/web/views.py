from datetime import date
from decimal import Decimal

from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, UpdateView

from apps.vendas.web.forms import JanelaAtendimentoForm
from apps.estoque.models.produto import Categoria, Produto
from apps.vendas.models.venda import ItemVenda, JanelaAtendimento, Venda
from apps.vendas.services import EstoqueInsuficienteError, realizar_venda


def _janela_atual():
    agora = timezone.localtime(timezone.now()).time()
    return JanelaAtendimento.objects.filter(
        ativo=True,
        hora_inicio__lte=agora,
        hora_fim__gte=agora,
    ).first()


def _contexto_nova_venda(request, erro=None):
    """Monta o contexto do template de nova venda — centralizado para evitar repetição."""
    carrinho = request.session.get("carrinho", [])
    for item in carrinho:
        item.setdefault("unidade_medida", "un")
    janela_atual = _janela_atual()
    total = sum(Decimal(str(item["subtotal"])) for item in carrinho)
    categorias = Categoria.objects.filter(
        produtos__ativo=True
    ).prefetch_related("produtos").distinct().order_by("nome")
    destaques = Produto.objects.filter(ativo=True, destaque=True).order_by("nome")

    ctx = {
        "categorias": categorias,
        "destaques": destaques,
        "carrinho": carrinho,
        "janelas": JanelaAtendimento.objects.filter(ativo=True),
        "janela_atual_id": janela_atual.pk if janela_atual else None,
        "total": total,
        "formas_pagamento": Venda.PAGAMENTO_CHOICES,
        "modos_atendimento": Venda.MODO_CHOICES,
        "data_hoje": date.today().isoformat(),
    }
    if erro:
        ctx["erro"] = erro
    return ctx


class NovaVendaView(View):
    template_name = "vendas/venda_nova.html"

    def get(self, request):
        return render(request, self.template_name, _contexto_nova_venda(request))


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
                "unidade_medida": produto.unidade_medida,
            })

        request.session["carrinho"] = carrinho
        return redirect("venda-create")


class RemoverItemView(View):
    def post(self, request):
        produto_id = int(request.POST.get("produto_id"))
        carrinho = request.session.get("carrinho", [])
        request.session["carrinho"] = [i for i in carrinho if i["produto_id"] != produto_id]
        return redirect("venda-create")


class AjustarQuantidadeView(View):
    def post(self, request):
        produto_id = int(request.POST.get("produto_id"))
        acao = request.POST.get("acao")
        carrinho = request.session.get("carrinho", [])

        for item in carrinho:
            if item["produto_id"] == produto_id:
                quantidade = Decimal(str(item["quantidade"]))
                quantidade = quantidade + 1 if acao == "mais" else quantidade - 1

                if quantidade <= 0:
                    carrinho = [i for i in carrinho if i["produto_id"] != produto_id]
                else:
                    item["quantidade"] = str(quantidade)
                    item["subtotal"] = str(quantidade * Decimal(str(item["preco_unitario"])))
                break

        request.session["carrinho"] = carrinho
        return redirect("venda-create")


class FinalizarVendaView(View):
    """
    Delega toda a lógica de negócio para realizar_venda().
    Responsabilidade desta view: ler o POST, chamar o service,
    tratar o erro de estoque e redirecionar.
    """
    def post(self, request):
        carrinho = request.session.get("carrinho", [])
        if not carrinho:
            return redirect("venda-create")

        forma_pagamento = request.POST.get("forma_pagamento")
        janela_id = request.POST.get("janela_atendimento")
        modo = request.POST.get("modo_atendimento", "rapido")
        valor_recebido_raw = request.POST.get("valor_recebido") or None

        janela = None
        if janela_id:
            try:
                janela = JanelaAtendimento.objects.get(pk=janela_id)
            except JanelaAtendimento.DoesNotExist:
                pass

        valor_recebido = Decimal(str(valor_recebido_raw)) if valor_recebido_raw else None

        try:
            realizar_venda(
                itens_carrinho=carrinho,
                forma_pagamento=forma_pagamento,
                modo_atendimento=modo,
                janela=janela,
                valor_recebido=valor_recebido,
            )
        except EstoqueInsuficienteError as e:
            # Não limpa o carrinho — operador corrige e tenta de novo
            erro = (
                f"Estoque insuficiente para '{e.produto_nome}': "
                f"disponível {e.disponivel} un., solicitado {e.solicitado} un."
            )
            return render(request, "vendas/venda_nova.html", _contexto_nova_venda(request, erro=erro))

        request.session["carrinho"] = []
        return redirect("venda-list")


# ─── Janelas de atendimento ───────────────────────────────────────────────────

class JanelaCreateView(CreateView):
    model = JanelaAtendimento
    form_class = JanelaAtendimentoForm
    template_name = "vendas/janela_form.html"
    success_url = reverse_lazy("configuracoes")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Nova Janela de Atendimento"
        return ctx


class JanelaUpdateView(UpdateView):
    model = JanelaAtendimento
    form_class = JanelaAtendimentoForm
    template_name = "vendas/janela_form.html"
    success_url = reverse_lazy("configuracoes")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = f"Editar: {self.object.nome}"
        return ctx


class JanelaToggleAtivoView(View):
    def post(self, request, pk):
        try:
            janela = JanelaAtendimento.objects.get(pk=pk)
        except JanelaAtendimento.DoesNotExist:
            return redirect("configuracoes")
        janela.ativo = not janela.ativo
        janela.save(update_fields=["ativo", "atualizado_em"])
        return redirect("configuracoes")