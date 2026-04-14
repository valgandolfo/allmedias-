# Generated manually - cria tabela de notificacoes de compras

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificacaoCompra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto_completo', models.TextField(verbose_name='Texto completo da notificação')),
                ('app_origem', models.CharField(blank=True, max_length=100, verbose_name='App de origem (Google Wallet, Nubank, etc.)')),
                ('valor', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Valor da compra')),
                ('estabelecimento', models.CharField(blank=True, max_length=200, verbose_name='Estabelecimento/Local')),
                ('data_compra', models.DateField(blank=True, null=True, verbose_name='Data da compra')),
                ('hora_compra', models.TimeField(blank=True, null=True, verbose_name='Hora da compra')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notificacoes_compra', to='auth.user', verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Notificação de Compra',
                'verbose_name_plural': 'Notificações de Compras',
                'db_table': 'notificacao_compra',
                'ordering': ['-criado_em'],
            },
        ),
    ]
