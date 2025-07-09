from user_acc.models import user
from django.db import models

class Buses(models.Model):
    Bus_type_choice = [
        ('AC', 'AC'),
        ('NONAC', 'Non-AC')
    ]
    bus_id = models.AutoField(primary_key=True)
    operator = models.CharField(max_length=25)
    busnumber = models.IntegerField(unique=True)
    source = models.CharField(max_length=20)
    destination = models.CharField(max_length=20)
    departure = models.CharField(max_length=100)
    arrival = models.CharField(max_length = 100)
    departuretime = models.TimeField()
    arrivaltime = models.TimeField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    duration = models.TimeField()
    available_seats = models.IntegerField()
    type = models.CharField(max_length=5, choices=Bus_type_choice)
    
class Bookings(models.Model):
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(user, on_delete = models.CASCADE, related_name="booking")
    bus = models.ForeignKey(Buses, on_delete= models.CASCADE, related_name="booking")
    Date_TOB = models.DateTimeField(auto_now_add=True)
    no_of_seats = models.IntegerField()
    contact = models.BigIntegerField()
    email = models.EmailField()
    pincode = models.IntegerField()
    city = models.CharField(max_length = 50)
    state = models.CharField(max_length = 50)
    address = models.CharField(max_length=200)
    
class SeatsDetail(models.Model):
    
    booking = models.ForeignKey(Bookings, on_delete=models.CASCADE, related_name='seatDetail')
    first_name = models.CharField(max_length=20)
    middle_name = models.CharField(max_length=20, blank= True)
    last_name = models.CharField(max_length=20, blank=True)
    age = models.IntegerField()
    seat = models.IntegerField()