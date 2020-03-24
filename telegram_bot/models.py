from django.db import models

class Subscription(models.Model):
    chat_id = models.IntegerField()
    tuewarning = models.BooleanField(default=False)
    citieswarning = models.TextField()
    top20warning = models.BooleanField(default=False)

    def __str__(self):
        return str(self.chat_id)
