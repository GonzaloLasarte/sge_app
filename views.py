from urllib import parse as urlparse
from PIL import Image
from ftplib import FTP
import io


from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import redirect, HttpResponse
from django.conf import settings

def redirect_view(request):
    response = redirect('gestion/')
    return response

@login_required
def media(request, pk, filename):
    ftp = FTP(
	settings.FTP_HOST,
	settings.FTP_USER,
	settings.FTP_PASSWORD)
    pwd = ftp.pwd()
    ftp.cwd(str(pk))
    
    memory_file = io.BytesIO()
    ftp.retrbinary('RETR ' + filename, memory_file.write)  #retrieve the file
    memory_file.seek(0)
    response = FileResponse(memory_file)
    response["Content-Disposition"] = "attachment; filename=" + filename

    ftp.cwd(pwd)

    return response
