from Buses.models import Buses, SeatsDetail, Bookings

from datetime import timedelta, datetime

from rest_framework.serializers import ModelSerializer, SerializerMethodField, ListField
from rest_framework.validators import ValidationError
from rest_framework.response import Response
from rest_framework import status

from django.core.exceptions import ObjectDoesNotExist

class BusSerializer(ModelSerializer):
    """Serializer class for Buses models, used for validating,creating the data, it has 4 additional properties tax, total, departureDate, arrivalDate which are computed using class methods 

    Args:
        ModelSerializer (class): Built in serializer class for models 

    """
    tax = SerializerMethodField()
    total = SerializerMethodField()
    departureDate = SerializerMethodField()
    arrivalDate = SerializerMethodField()
    
    class Meta:
        model = Buses
        fields = "__all__"
    
    def __init__(self, instance=None, *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        
        if not self.context.get('isdate'):
            self.fields.pop('departureDate')
            self.fields.pop('arrivalDate')
    
    def get_departureDate(self, obj):
        """returns the date from the context 

        Args:
            obj (model object): current instance of the model as passed by the view 

        Returns:
            string: returns the date value from the context of the current serializer
        """
        currentDate = self.context.get('date')
        return currentDate
    
    def get_arrivalDate(self, obj):
        """It returns the arrival date after performing operations on the departure time, departure date and the duration as fetched from the current bus instance

        Args:
            obj (model object): refers to the current instance of the model 

        Returns:
            string: returns the arrival date as a string 
        """
        departureDate = self.get_departureDate(obj)
        departureDate = datetime.strptime(departureDate, "%d-%m-%Y").date()
        departureTime = obj.departuretime
        duration = obj.duration
        
        duration = timedelta(hours=duration.hour, minutes = duration.minute, seconds=duration.second)
        departure = datetime.combine(departureDate, departureTime)
        
        arrival = departure + duration
        arrival = arrival.date()
        arrival = arrival.strftime("%d-%m-%Y")
        return arrival
    
    def get_tax(self, obj):
        """computes the value for the tax field, uses the price field from the current bus instance

        Args:
            obj (model object): refers to the current instance of the model

        Returns:
            float: returns the value for the tax after rounding it to 2 decimal places 
        """
        price = float(obj.price)
        return round(price*0.18, 2)
    
    def get_total(self, obj):
        """computes the value for the total field after adding the tax value and the price of the current bus instance 

        Args:
            obj (model object ): refers to the current instance of the model

        Returns:
            float: returns the value for the total after rounding it to 2 decimal places
        """
        tax = self.get_tax(obj)
        price = float(obj.price)
        return round(price + tax, 2)

class SeatsSerializer(ModelSerializer):
    """built-in serializer class for model SeatsDetail used for validating and creating the data for the specific model and validates the age field from the data input by the user

    Args:
        ModelSerializer (class): built-in class in rest_framework.serializers

    Raises:
        ValidationError: if the age of a certain passenger is less than 5 then it raises the error
    """
    class Meta:
        model = SeatsDetail
        fields = "__all__"
        
        
    def validate_age(self, age):
        """validates the age field 

        Args:
            age (int): age value for the corresponding passenger 

        Raises:
            ValidationError: age of any passenger can't be less than 5 

        Returns:
            int: if the age is more than or equal to 5 it just simply returns it back
        """
        if age < 5:
            raise ValidationError("Age can't be less than 5")
        else:
            return age 
        
class BookingSerializer(ModelSerializer):
    """Serializer class for the model Bookings. It validates the data for both Bookings class and SeatsDetail class and also helps to create the data for both of the models.
    price is an extra field which is computed using class method. It overrides the create method where it creates and saves the data for the booking model,
    and pops the passenger data from the validated data and uses the SeatsSerializer class to creat the data for SeatsDetail model

    Args:
        ModelSerializer (class): built-in serializer class for models in rest_framework.serializers

    Raises:
        ValidationError: if the no. of seats entered by the user is greater than the available seats then the error is raised 
    """
    passengers = ListField()
    price = SerializerMethodField()
    
    class Meta:
        model = Bookings 
        fields = "__all__"
    
    def create(self, validated_data):
        passengerDetails = validated_data.pop('passengers')
        booking = Bookings.objects.create(**validated_data)
        
        for passenger in passengerDetails:
            passenger.update({'booking':booking.id})
            data = SeatsSerializer(data = passenger)
            if data.is_valid(raise_exception=True):
                data.save()
            else:
                print(data.errors)
                
        return booking
            
    def validate_no_of_seats(self, value):
        """ validates the no. of seats field 
        Args:
            value (int): no. of seats entered by the user 

        Raises:
            ValidationError: if the no. of seats entered by the user is greater than the available seats then the error is raised

        Returns:
            int: returns the no. of seats if its greater than available seats 
        """
        id = self.initial_data.get('bus')
        try:
            bus_instance = Buses.objects.get(bus_id = id)
        except ObjectDoesNotExist:
            return Response({'status':'Failure', 'message':"Bus no longer exists"}, status=status.HTTP_404_NOT_FOUND)
        else:
            available_seats = bus_instance.available_seats
            
        if value <= available_seats:
            return value
        else:
            raise ValidationError("Number of Seats selected is greater than available seats")
    
    def get_price(self, obj):
        """computes the value for price field

        Args:
            obj (model object): refers to the current instance of the model 

        Returns:
            float: it gives the total price value against the no. of seats booked by the user
        """
        seats = obj.no_of_seats
        serialized_data = BusSerializer(obj.bus).data
        
        price = serialized_data.get('total')
        return price*seats
    
