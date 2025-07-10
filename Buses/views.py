from Buses.serializers import BusSerializer, BookingSerializer, SeatsSerializer
from Buses.models import Buses, Bookings, SeatsDetail

from datetime import datetime, time

from utility.functions import timeBasedData, priceBasedData, durationBasedData

from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import exceptions

from django.forms.models import model_to_dict
from django.db import transaction

class SourceDestOptions(APIView):
    serializer_class = BusSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """This function takes in the request object and returns the list of sources and destination as per the records in DATABASE, useful for providing the options for dropdown menu 

        Args:
            request (): request object coming from the client's browser

        Returns:
            response: list of sources and destination
        """
        source = Buses.objects.distinct().values_list('source', flat=True)
        destination = Buses.objects.distinct().values_list('destination', flat=True)
        return Response({"status":"Success", 'data' : {'source':source, 'destination': destination}}, status=status.HTTP_200_OK)
    
class BusesData(APIView):
    serializer_class = BusSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """This function takes in the request object and applies the sorting or filtering functionality as per the query parameters sent by the user and in the end returns the entries which will be sorted or filtered as per the conditions

        Args:
            request (_type_): request object coming from the browser

        Returns:
            response: entries satisying the source and destination which will be either sorted or filtered or as it is. 
        """
        try:
            source = request.query_params.get('source')
            destination = request.query_params.get('destination')
            date = request.query_params.get('date')
            
            if date:
                request.session['date'] = date
            else:
                return Response({'status':'Failure', 'message':"Date is required"}, status=status.HTTP_400_BAD_REQUEST)
        
            if source and destination:
                currTime = datetime.now().time()
                busdata = Buses.objects.filter(source = source, destination = destination, departuretime__gte = currTime)
                isdata = busdata.exists()
                if not isdata:
                    return Response({'status':"Failure", 'message':"No Buses availabele"}, status = status.HTTP_204_NO_CONTENT)
                
                deptTimeRange = request.query_params.get('depttimerange')
                arrivalTimeRange = request.query_params.get('arrivaltimerange')
                sortVal = request.query_params.get('sorting')
                userMinPrice = request.query_params.get('minprice')
                userMaxPrice = request.query_params.get('maxprice')
                userMinDuration = request.query_params.get('minduration')
                userMaxDuration = request.query_params.get('maxduration')
            
                if sortVal:
                    sortList = sortVal.split(",")
                    busdata = busdata.order_by(*sortList)
            
                if deptTimeRange or arrivalTimeRange:
                    busdata = timeBasedData(deptTimeRange, arrivalTimeRange, busdata)
            
                if userMinPrice or userMaxPrice:
                    priceList = busdata.values_list('price',flat=True)
                    minPrice = min(priceList)
                    maxPrice = max(priceList)
                
                    busdata = priceBasedData(minPrice, maxPrice, userMinPrice, userMaxPrice, busdata)
            
                if userMinDuration or userMaxDuration:
                    busdata = durationBasedData(userMinDuration, userMaxDuration, busdata)
                
                if busdata:        
                    paginator = PageNumberPagination()
                    pageqs = paginator.paginate_queryset(busdata, request)
                    serializer = BusSerializer(pageqs, many = True, context = {'isdate':False})
        
                    return paginator.get_paginated_response(serializer.data)
                else:
                    return Response({'status':"Failure", "message":"No Buses in desired duration"}, status = status.HTTP_204_NO_CONTENT)
        
            else:
                return Response({'status':"Failure", "message":"source and destination can't be empty"}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'status':"Failure", 'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class BusInfo(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, **kwargs):
        """This function takes request object and kwargs as the input and with the id parameter fetches the record of the desired Bus 

        Args:
            request (rest_framework.request object):

        Returns:
            Response: Returns Bus Data for the specific bus id 
        """
        try: 
            busData = Buses.objects.get(bus_id = kwargs['id'])
            serializer = BusSerializer(busData, context = {'isdate':True, 'date':request.session.get('date')})
            
        except Buses.DoesNotExist:
            return Response({'status':"Failure", 'message':"Bus no longer exists"}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            return Response({"status":"Success!", 'data':serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request, **kwargs):
        """This function fetches the data sent by the user, validates that data and if the data is valid then it saves the entry in the DB, and available seats are reduced after the record is saved 

        Args:
            request (rest_framework.request object): _description_

        Returns:
            rest_framework.response object: A JSON with the current status and corresponding message or error if any 
        """
        try:    
            with transaction.atomic():
                data = request.data
                
                user = request.user
                userId = user.id
                busId = kwargs['id']
                
                data.update({'user':userId, 'bus':busId})
                
                serializer = BookingSerializer(data = data)
                if serializer.is_valid():
                    serializer.save()
                    busId = data.get('bus')
                    busInstance = Buses.objects.get(bus_id = busId)
                    no_of_seats = data.get('no_of_seats')
                    
                    busInstance.available_seats = busInstance.available_seats - no_of_seats
                    busInstance.save()
                    
                    return Response({'status':'Success', 'message':'Seat Booked Successfully'}, status = status.HTTP_200_OK)
                else:
                    print(serializer.errors)
                    return Response({'status':'Failure', 'message':'Seat not booked please check the input credentials'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e: 
            return Response({'status':'Failure', 'errors':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BookInfo(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        """This function displays the booking details like billing details, passenger details, contact details using the user id of the authenticated user 

        Args:
            request (rest_framework.request object)

        Returns:
           rest_framework.response object: It sends json as a response containing the current status as well as the required data 
        """
        try:   
            user = request.user
            user_id = user.id
        
            booking_entry = Bookings.objects.filter(user = user_id).last()
            booking_dict = model_to_dict(booking_entry, fields=['no_of_seats', 'contact', 'email', 'pincode', 'city', 'state', 'address'])
        
            busId = booking_entry.bus_id
        
            bus_entry = Buses.objects.get(bus_id = busId)
            bus_dict = BusSerializer(bus_entry, context = {'isdate':True, 'date':request.session.get('date')}).data
        
            bookingId = booking_entry.id
            passengerDetails = SeatsDetail.objects.filter(booking = bookingId).values_list('first_name', 'middle_name', 'last_name', 'age', 'seat')
        
            passengerList = []
            for entry in passengerDetails:
                passengerList.append(list(entry))
    
            booking_data = [booking_dict, bus_dict, passengerList]
        
        except Exception as e:
            return Response({'status':"Failure", 'message':str(e)}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            return Response({'status':"Success", 'data':booking_data}, status=status.HTTP_200_OK)
        