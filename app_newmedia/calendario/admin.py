from django.contrib import admin
from .models import Compromisso, LogCron


@admin.register(Compromisso)
class CompromissoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'data', 'hora', 'titulo', 'antecedencia_minutos', 'lembrete_enviado')
    list_filter = ('lembrete_enviado', 'usuario')
    search_fields = ('titulo', 'usuario__username')
    date_hierarchy = 'data'


@admin.register(LogCron)
class LogCronAdmin(admin.ModelAdmin):
    list_display = ('executado_em', 'status', 'mensagens_enviadas')
    list_filter = ('status',)
    readonly_fields = ('executado_em', 'status', 'mensagens_enviadas', 'detalhes')
    ordering = ('-executado_em',)

    def has_add_permission(self, request):
        return False  # logs só são criados pelo sistema

    def has_change_permission(self, request, obj=None):
        return False  # somente leitura
