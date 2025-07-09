from datetime import date
from re import search

from .models import user

from rest_framework.serializers import ModelSerializer

from django.core.exceptions import ValidationError

class UserSerializer(ModelSerializer):
    """It is a serializer class for user model used for validating and creating the data entry in DB after hashing the password. 

    Args:
        ModelSerializer (class): built-in serializer class for model

    Raises:
        ValidationError: if the user's age is less than 18 it raises error as age must be 18+
        ValidationError: the password enetered by the user must contain alphabets,numbers and special characters
    """
    class Meta:
        model = user
        fields = "__all__"
        extra_kwargs = {'password' : {'write_only': True}}
    
    def create(self, validated_data):
        """overrides the create function of the inherited class inorder to hash the password before saving it in the db

        Args:
            validated_data (dict): _dictionary containing the data enetered by the user after validation

        Returns:
            user object: _returns the current instance of the user model after its creation
        """
        password = validated_data.pop('password')
        usr = user(**validated_data)
        usr.set_password(password)  
        usr.save()
        return usr
    
    def validate_DOB(value):
        """validates the DOB as entered by the user 

        Args:
            value (str): contains the DOB of the user 

        Raises:
            ValidationError: if user is under 18 then error is raised

        Returns:
            str: returns the DOB of the user after it is validated 
        """
        dobstr = str(value)
        dobyear, dobmonth, dobday = map(int, dobstr.split("-"))
    
        datestr = str(date.today())
        year, month, day = map(int, datestr.split("-"))
    
        yeardiff = year-dobyear
        monthdiff = month - dobmonth
        daydiff = day - dobday
    
        if yeardiff > 18:
            return value
        elif yeardiff == 18:
            if monthdiff >0:
                return value
            elif monthdiff == 0:
                if daydiff >=0:
                    return value
                else:
                    raise ValidationError("Age must be 18+")
            else:
                raise ValidationError("Age must be 18+")
            
        else:
            raise ValidationError("Age must be 18+")
    
    def validate_password(value):
        """validates the password field

        Args:
            value (str): password of the user 

        Raises:
            ValidationError: if the passwoord doesn't contain numbers and special characters, error is raised

        Returns:
            str: returns the password value after it is validated 
        """
        numbers = search(r'\d', value)
        specials = search(r'[^a-zA-Z\d]', value)
    
        if numbers and specials:
            return value
        else:
            raise ValidationError("password must contain numbers and special characters")