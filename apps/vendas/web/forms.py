from django import forms

from apps.vendas.models.venda import JanelaAtendimento


class JanelaAtendimentoForm(forms.ModelForm):
    class Meta:
        model = JanelaAtendimento
        fields = ["nome", "hora_inicio", "hora_fim", "ativo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-input"
