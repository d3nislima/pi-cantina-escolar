from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Adiciona uma CheckConstraint no banco para garantir que estoque_atual
    nunca seja negativo — camada de segurança adicional além da validação
    no service. Se por algum bug a validação do Python for bypassada,
    o banco rejeita a gravação com IntegrityError.
    """

    dependencies = [
        ("estoque", "0003_add_categoria_ativo"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="produto",
            constraint=models.CheckConstraint(
                check=models.Q(estoque_atual__gte=0),
                name="estoque_atual_nao_negativo",
                violation_error_message="O estoque atual não pode ser negativo.",
            ),
        ),
    ]
