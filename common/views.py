from django.http import HttpResponse
import os
from django.conf import LazySettings
settings = LazySettings()


def download_csv(request):
    file_name = request.GET.get('file_name', None)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    file = open(os.path.join(settings.BASE_DIR, f'downloadables/{file_name}'))
    response.content = file
    return response
