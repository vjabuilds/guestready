from django.db import models

# Create your models here.

class Rental(models.Model):
    name = models.CharField(max_length=50)
    

class Reservation(models.Model):
    checkin = models.DateTimeField()
    checkout = models.DateTimeField()
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)