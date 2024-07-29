from django.db import models

class ScanResult(models.Model):
    ip = models.CharField(max_length=15)
    result = models.JSONField()

    def __str__(self):
        return f"{self.ip}: {self.result}"
