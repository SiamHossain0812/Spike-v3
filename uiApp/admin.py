from django.contrib import admin
from .models import SpikeData, StationName

class SpikeDataAdmin(admin.ModelAdmin):
    list_display = ('dateTime', 'value', 'spike_value')  # Updated to reflect changes in model
    search_fields = ('dateTime',)  # Enable search functionality for the dateTime field
    ordering = ('dateTime',)  # Default ordering by dateTime

admin.site.register(SpikeData, SpikeDataAdmin)

@admin.register(StationName)
class StationNameAdmin(admin.ModelAdmin):
    list_display = ('station_name',)
