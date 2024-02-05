from django.core.management.base import BaseCommand, CommandError
from gestion.models import Member

class Command(BaseCommand):
    help = 'Actualiza la estructura actual'

    def handle(self, *args, **options):
        
        members = Member.objects.all()
        for member in members:
            try:
                member.actualizar_estructura()
                member.save()

                self.stdout.write(self.style.SUCCESS('Successfully updated member "%s"' % member.pk))
            except:
                pass
        


