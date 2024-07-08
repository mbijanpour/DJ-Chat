# the serializer is used for forming the data we retrieved from the data base
# into a format that can be returned to the endpoint for the user

from rest_framework import serializers

from .models import Server, Category


class ServerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Server
        fields = "__all__" # meaning we return all the fields in the server model
        
    
