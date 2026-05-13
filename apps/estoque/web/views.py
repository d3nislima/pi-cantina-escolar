from django.db.models import Count
from django.shortcuts import redirect
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView
from django.urls import reverse_lazy

from apps.estoque.models.movimento import MovimentoEstoque
from apps.estoque.models.produto import Categoria, Produto
from .forms import CategoriaForm, MovimentoEstoqueForm, ProdutoForm


class EstoqueListView(ListView):
    model = Produto
    template_name = "estoque/estoque_list.html"
    context_object_name = "produtos"
    ordering = ["nome"]


class ProdutoCreateView(CreateView):
    model = Produto
    form_class = ProdutoForm
    template_name = "estoque/produto_form.html"
    success_url = reverse_lazy("produto-list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Novo Produto"
        return ctx


class ProdutoUpdateView(UpdateView):
    model = Produto
    form_class = ProdutoForm
    template_name = "estoque/produto_form.html"
    success_url = reverse_lazy("produto-list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = f"Editar: {self.object.nome}"
        return ctx


class MovimentacaoListView(ListView):
    model = MovimentoEstoque
    template_name = "estoque/movimentacao_list.html"
    context_object_name = "movimentacoes"
    ordering = ["-data_movimento"]
    paginate_by = 50


class MovimentacaoCreateView(CreateView):
    model = MovimentoEstoque
    form_class = MovimentoEstoqueForm
    template_name = "estoque/movimentacao_form_avancado.html"
    success_url = reverse_lazy("produto-list")

    def form_valid(self, form):
        movimento = form.save(commit=False)
        movimento.data_movimento = timezone.now()
        produto = movimento.produto
        movimento.saldo_antes = produto.estoque_atual

        if movimento.operacao == "entrada":
            produto.estoque_atual += movimento.quantidade
            if movimento.origem == "compra":
                produto.preco_custo = movimento.valor_unitario
        elif movimento.operacao == "saida":
            produto.estoque_atual -= movimento.quantidade
        else:
            produto.estoque_atual = movimento.quantidade

        movimento.saldo_depois = produto.estoque_atual
        produto.save()
        movimento.save()
        return redirect(self.success_url)


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
    success_url = reverse_lazy("categoria-list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Nova Categoria"
        return ctx


class CategoriaUpdateView(UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "estoque/categoria_form.html"
    success_url = reverse_lazy("categoria-list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = f"Editar: {self.object.nome}"
        return ctx


class CategoriaToggleAtivoView(View):
    def post(self, request, pk):
        try:
            categoria = Categoria.objects.get(pk=pk)
        except Categoria.DoesNotExist:
            return redirect("categoria-list")
        categoria.ativo = not categoria.ativo
        categoria.save(update_fields=["ativo", "atualizado_em"])
        return redirect("categoria-list")


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
