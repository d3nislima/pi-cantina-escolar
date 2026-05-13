from decimal import Decimal

from django.db import transaction
from django.db.models import Count
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView
from django.urls import reverse_lazy

from apps.estoque.models.movimento import MovimentoEstoque
from apps.estoque.models.produto import Categoria, Produto
from .forms import CategoriaForm, MovimentacaoSimplificadaForm, ProdutoForm


ORIGEM_PARA_OPERACAO = {
    "compra": "entrada",
    "doacao": "entrada",
    "perda": "saida",
    "inventario": "ajuste",
    "ajuste_manual": "ajuste",
}


class EstoqueListView(ListView):
    model = Produto
    template_name = "estoque/estoque_list.html"
    context_object_name = "produtos"
    ordering = ["nome"]


class ProdutoUpdateView(UpdateView):
    model = Produto
    form_class = ProdutoForm
    template_name = "estoque/produto_form.html"
    success_url = reverse_lazy("produto-list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = f"Editar: {self.object.nome}"
        return ctx


class EntradaEstoqueView(View):
    template_name = "estoque/entrada_estoque.html"

    def get(self, request):
        modo = request.GET.get("modo", "existente")
        form = MovimentacaoSimplificadaForm() if modo == "existente" else ProdutoForm()
        return render(request, self.template_name, {"form": form, "modo": modo})

    def post(self, request):
        modo = request.POST.get("modo", "existente")
        if modo == "existente":
            return self._post_existente(request)
        return self._post_novo(request)

    def _post_existente(self, request):
        form = MovimentacaoSimplificadaForm(request.POST)
        if form.is_valid():
            produto = form.cleaned_data["produto"]
            origem = form.cleaned_data["origem"]
            quantidade = form.cleaned_data["quantidade"]
            valor_unitario = form.cleaned_data.get("valor_unitario") or Decimal("0")
            observacao = form.cleaned_data.get("observacao") or ""
            operacao = ORIGEM_PARA_OPERACAO[origem]
            saldo_antes = produto.estoque_atual
            if operacao == "entrada":
                produto.estoque_atual += quantidade
            elif operacao == "saida":
                produto.estoque_atual -= quantidade
            else:
                produto.estoque_atual = quantidade
            with transaction.atomic():
                update_fields = ["estoque_atual", "atualizado_em"]
                if origem == "compra" and valor_unitario > 0:
                    produto.preco_custo = valor_unitario
                    update_fields.append("preco_custo")
                produto.save(update_fields=update_fields)
                MovimentoEstoque.objects.create(
                    produto=produto,
                    operacao=operacao,
                    origem=origem,
                    quantidade=quantidade,
                    valor_unitario=valor_unitario,
                    saldo_antes=saldo_antes,
                    saldo_depois=produto.estoque_atual,
                    data_movimento=timezone.now(),
                    observacao=observacao,
                )
            return redirect("produto-list")
        return render(request, self.template_name, {"form": form, "modo": "existente"})

    def _post_novo(self, request):
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save()
            quantidade_inicial = form.cleaned_data.get("quantidade_inicial")
            valor_unitario = form.cleaned_data.get("valor_unitario") or Decimal("0")
            origem = form.cleaned_data.get("origem", "compra")
            if quantidade_inicial and quantidade_inicial > 0:
                produto.estoque_atual = quantidade_inicial
                with transaction.atomic():
                    update_fields = ["estoque_atual", "atualizado_em"]
                    if origem == "compra" and valor_unitario > 0:
                        produto.preco_custo = valor_unitario
                        update_fields.append("preco_custo")
                    produto.save(update_fields=update_fields)
                    MovimentoEstoque.objects.create(
                        produto=produto,
                        operacao=ORIGEM_PARA_OPERACAO.get(origem, "entrada"),
                        origem=origem,
                        quantidade=quantidade_inicial,
                        valor_unitario=valor_unitario,
                        saldo_antes=Decimal("0"),
                        saldo_depois=quantidade_inicial,
                        data_movimento=timezone.now(),
                    )
            return redirect("produto-list")
        return render(request, self.template_name, {"form": form, "modo": "novo"})


class MovimentacaoListView(ListView):
    model = MovimentoEstoque
    template_name = "estoque/movimentacao_list.html"
    context_object_name = "movimentacoes"
    ordering = ["-data_movimento"]
    paginate_by = 50


class CategoriaListView(ListView):
    model = Categoria
    template_name = "estoque/categoria_list.html"
    context_object_name = "categorias"

    def get_queryset(self):
        return (
            Categoria.objects.select_related("categoria_pai")
            .annotate(num_produtos=Count("produtos"))
            .order_by("categoria_pai__nome", "nome")
        )


class CategoriaCreateView(CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "estoque/categoria_form.html"
    success_url = reverse_lazy("configuracoes")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Nova Categoria"
        return ctx


class CategoriaUpdateView(UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "estoque/categoria_form.html"
    success_url = reverse_lazy("configuracoes")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = f"Editar: {self.object.nome}"
        return ctx


class CategoriaToggleAtivoView(View):
    def post(self, request, pk):
        try:
            categoria = Categoria.objects.get(pk=pk)
        except Categoria.DoesNotExist:
            return redirect("configuracoes")
        categoria.ativo = not categoria.ativo
        categoria.save(update_fields=["ativo", "atualizado_em"])
        return redirect("configuracoes")


class ProdutoToggleView(View):
    CAMPOS_PERMITIDOS = {"ativo", "destaque"}

    def post(self, request, pk, campo):
        if campo not in self.CAMPOS_PERMITIDOS:
            return redirect("produto-list")
        try:
            produto = Produto.objects.get(pk=pk)
        except Produto.DoesNotExist:
            return redirect("produto-list")
        setattr(produto, campo, not getattr(produto, campo))
        produto.save(update_fields=[campo, "atualizado_em"])
        return redirect("produto-list")
