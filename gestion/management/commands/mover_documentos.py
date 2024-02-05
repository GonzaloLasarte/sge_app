import ftplib

from django.core.management.base import BaseCommand, CommandError

from gestion.models import Documento

FTP_STORAGE_LOCATION = 'ftp://media@gestion-sokagakkai.org:=ZPa$MXqjP@ftp.gestion-sokagakkai.org:21'
LOCATION = 'ftp://media@gestion-sokagakkai.org:=ZPa$MXqjP@ftp.gestion-sokagakkai.org'

FTP_HOST = 'ftp.gestion-sokagakkai.org'
FTP_USER = 'media@gestion-sokagakkai.org'
FTP_PASSWORD = '=ZPa$MXqjP'


class Command(BaseCommand):
    help = 'Busca documentos de la carpeta media/None de la FTP y los coloca en su carpeta de miembro correspondiente'

    def handle(self, *args, **options):
        
        ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASSWORD)

        # ftp.cwd("/None")
        
        # try:
        folders = ftp.nlst()
        
        # except(ftplib.error_perm, resp):
        #     if str(resp) == "550 No files found":
        #         print("No files in this directory")
        #     else:
        #         raise

        # data = []

        # ftp.dir(data.append)

        # ftp.quit()

        # for line in data:
        #     print("-", line)

        # with open('listfile_2.txt', 'w') as filehandle:
        #     filehandle.writelines("%s\n" % f for f in data)

        with open('listfile_2.txt', 'r') as filehandle:
            files = filehandle.readlines()

            for f in files[:1]:
                file_name = f[62:].strip()
                file_name = file_name.replace('Ñ', 'N')
                self.stdout.write(f'file_name: {file_name}')

                try:
                    # documento = Documento.objects.get(archivo__contains=f'None/{file_name}')
                    # member_id = f'{documento.member_id}'
                    member_id = '5805'
                    if member_id not in folders:
                        self.stdout.write(f'Directorio {member_id} no existe')
                        ftp.mkd(member_id)
                    # self.stdout.write(f'{documento.pk}')
                    # self.stdout.write(f'{documento.archivo}')
                    # self.stdout.write(f'{member_id}/{file_name}')
                    # documento.archivo = f'{member_id}/{file_name}'
                    # documento.save()
                    ftp.rename(f'None/{f[62:].strip()}', f'{member_id}/{file_name}')

                except Documento.DoesNotExist:
                    # pass
                    self.stdout.write(f'{file_name} no existe')
