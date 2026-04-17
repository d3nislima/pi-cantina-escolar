from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import CreateView, ListView, UpdateView
from django.urls import reverse_lazy

from apps.estoque.models.movimento import MovimentoEstoque
from apps.estoque.models.produto import Produto
from .forms import MovimentoEstoqueForm, ProdutoForm


class ProdutoListView(ListView):
    model = Produto
    template_name = "estoque/produto_list.html"
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
    success_url = reverse_lazy("movimentacao-list")

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
