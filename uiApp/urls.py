# water_level_monitoring/urls.py

from django.contrib import admin
from django.urls import path
from uiApp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.spikedata, name='spikedata'),  # Main view for uploading and processing data
    path('export-spikedata/', views.export_spikedata, name='export_spikedata'),  # Export processed data
    path('upload-station-data/', views.upload_station_data, name='upload_station_data'),  # Upload station data
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
