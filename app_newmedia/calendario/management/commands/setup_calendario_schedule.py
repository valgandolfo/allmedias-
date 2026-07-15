from django.core.management.base import BaseCommand
from django_q.models import Schedule


class Command(BaseCommand):
    help = 'Registra o agendamento do lembrete de compromissos no Django-Q (roda a cada 5 minutos)'

    def handle(self, *args, **kwargs):
        schedule, created = Schedule.objects.get_or_create(
            name='enviar_lembretes_whatsapp',
            defaults={
                'func': 'django.core.management.call_command',
                'args': "'enviar_compromissos_whatsapp'",
                'schedule_type': Schedule.MINUTES,
                'minutes': 5,
                'repeats': -1,  # repetir para sempre
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(
                '✅ Schedule criado: enviar_lembretes_whatsapp (a cada 5 minutos)'
            ))
        else:
            # Garante que os parâmetros estão atualizados
            updated = False
            if schedule.minutes != 5:
                schedule.minutes = 5
                updated = True
            if schedule.repeats != -1:
                schedule.repeats = -1
                updated = True
            if updated:
                schedule.save()
                self.stdout.write(self.style.WARNING(
                    '⚠️  Schedule atualizado: enviar_lembretes_whatsapp'
                ))
            else:
                self.stdout.write(self.style.SUCCESS(
                    'ℹ️  Schedule já existe e está correto.'
                ))
