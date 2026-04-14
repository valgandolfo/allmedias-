# Generated manually - adds social media fields and removes preference fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0002_remove_userprofile_pix_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='facebook',
            field=models.CharField(blank=True, max_length=100, verbose_name='Facebook'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='instagram',
            field=models.CharField(blank=True, max_length=100, verbose_name='Instagram'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='youtube',
            field=models.CharField(blank=True, max_length=100, verbose_name='YouTube'),
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='tema_escuro',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='notificacoes_email',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='compartilhamento_publico',
        ),
    ]
