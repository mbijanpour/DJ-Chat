from django.shortcuts import render
from django.db.models import Count
from rest_framework import viewsets
from rest_framework import response
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from .serializer import ServerSerializer
from .models import Server
from rest_framework.response import Response


# viewsets are used for performing CRUDE operations
class ServerListViewSet(viewsets.ViewSet):
    """
    this class based end point for a general filtering operation
    which is a simpler approach rather than creating classes
    for each filtering or other operations
    viewset will provide us with a default implementation of CRUD operations
    """

    queryset = Server.objects.all()

    def list(self, request):
        """
        this method is for listing all the category
        the list method itself is used for GET request to return a list of
        objects from the database
        """

        # with the get_params we extract the category id from the get request
        category = request.query_params.get("category")
        by_user = request.query_params.get("by_user") == "true"
        qty = request.query_params.get("qty")
        by_server_id = request.query_params.get("by_server_id")
        with_num_members = request.query_params.get("with_num_members") == "true"
        
        # check if the user is authenticated to show the users servers 
        if by_user or by_server_id and not request.user.is_authenticated:
            raise AuthenticationFailed()
            

        if category:
            self.queryset = self.queryset.filter(
                category__name=category
            )  # get the object in queryset which have "category"

        if by_user:
            user_id = request.user.id

            self.queryset = self.queryset.filter(
                member=user_id
            )  # get the object in queryset which have members with "user_id" value
            
        if with_num_members:
            # we use annotation to perform more complex operations on querysets
            self.queryset = self.queryset.annotate(
                num_members=Count("member")
            )  # it will return the number of members associated with each server

        if qty:
            self.queryset = self.queryset[
                : int(qty)
            ]  # it will only return servers up to qty index
            
        if by_server_id:
            """ 
            its a simple error handling for two scenarios:
            1. if the id not found (validation error)
            2. if the the by_server_id value is not suitable for filtering (value error)
            all these handlings will be done in the front end side will get to that later
            """
            
            try:
                self.queryset = self.queryset.filter(
                    id=by_server_id
                )  # get the object in queryset which have "id" value
                # if the sent integer id was not found this part catch the validation error
                if not self.queryset.exists(): 
                    raise ValidationError(detail=f"server id {by_server_id} not found (validation error).")
            # it is expecting an integer by sending a Boolean for example this part will catch the value error
            except ValueError: 
                raise ValidationError(detail=f"server id {by_server_id} not found (value error).")

        serializer = ServerSerializer(self.queryset, many=True, context={"num_members": with_num_members})
        return Response(serializer.data)
