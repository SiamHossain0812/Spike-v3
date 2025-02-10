from django.db import models

class SpikeData(models.Model):
    dateTime = models.CharField(max_length=100)  # To store dateTime as string
    value = models.FloatField(null=True, blank=True)  # To store the original numeric value
    spike_value = models.FloatField(null=True, blank=True)  # To store the original value if replaced by NULL

    def __str__(self):
        return f"{self.dateTime}: {self.value} (Spike: {self.spike_value})"


class StationName(models.Model):
    station_name = models.CharField(max_length=255)

    def __str__(self):
        return self.station_name

class StationRecord(models.Model):
    station_id = models.CharField(max_length=50)  # Station identifier
    recorded_highest_wl = models.FloatField()  # Highest water level
    recorded_lowest_wl = models.FloatField()  # Lowest water level
    river_type = models.CharField(max_length=100, null=True, blank=True)  # New column for river type

    def __str__(self):
        return self.station_id
    
class RiverTypeThreshold(models.Model):
    river_type = models.CharField(max_length=50, unique=True)  # Either 'tidal' or 'hill'
    threshold_value = models.FloatField()  # Corresponding threshold (e.g., 0.5 or 0.75)

    def __str__(self):
        return f"{self.river_type}: {self.threshold_value}"
