from django.shortcuts import render
from django.db.models import Count
from rest_framework import viewsets
from rest_framework import response
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from .serializer import ServerSerializer
from .models import Server
from rest_framework.response import Response
from .schema import server_list_docs

# viewsets are used for performing CRUDE operations
class ServerListViewSet(viewsets.ViewSet):
    """
    this class based end point for a general filtering operation
    which is a simpler approach rather than creating classes
    for each filtering or other operations
    viewset will provide us with a default implementation of CRUD operations
    """

    queryset = Server.objects.all()

    @server_list_docs
    def list(self, request):
        """
        List servers based on filtering criteria.

        This method handles GET requests to return a list of server objects from the database.
        It supports the following filtering options via query parameters:

        - `category`: Filters servers by category name.
        - `by_user`: Filters servers by membership of the authenticated user.
        - `qty`: Limits the number of returned servers.
        - `by_server_id`: Filters servers by a specific server ID.
        - `with_num_members`: Includes the number of members for each server.

        Args:
           - `request (Request)`: The request object containing query parameters for filtering.

        Returns:
           - `Response`: A Response object containing the serialized server data.

        Raises:
           - `AuthenticationFailed`: If the user is not authenticated when required.
           - `ValidationError`: If the provided server ID is not found or invalid.
        """

        # with the get_params we extract the category id from the get request
        category = request.query_params.get("category")
        by_user = request.query_params.get("by_user") == "true"
        qty = request.query_params.get("qty")
        by_server_id = request.query_params.get("by_server_id")
        with_num_members = request.query_params.get("with_num_members") == "true"
        
        # we should nit interact with the self.queryset itself cause if the API was set to 
        # manage multiple requests then if for example the first request was handled and the
        # queryset was filtered based on the query of the first requests then the for the 
        # second request we have the filtered queryset not the whole.
        queryset = self.queryset

        if category:
            queryset = queryset.filter(
                category__name=category
            )  # get the object in queryset which have "category"

        if by_user:
            user_id = request.user.id
            if by_user and request.user.is_authenticated:
                queryset = queryset.filter(
                    member=user_id
                )  # get the object in queryset which have members with "user_id" value
            else:
                raise AuthenticationFailed()
            
        if with_num_members:
            # we use annotation to perform more complex operations on querysets
            queryset = queryset.annotate(
                num_members=Count("member")
            )  # it will return the number of members associated with each server

        if qty:
            # it will only return servers up to qty index
            try:
                qty = int(qty)
                queryset = queryset[:qty]
            except ValueError:
                raise ValidationError(detail="Invalid value for 'qty' parameter.")
            
        if by_server_id:
            """ 
            its a simple error handling for two scenarios:
            1. if the id not found (validation error)
            2. if the the by_server_id value is not suitable for filtering (value error)
            all these handlings will be done in the front end side will get to that later
            """
            
            if by_server_id and request.user.is_authenticated:
                try:
                    queryset = queryset.filter(
                        id=by_server_id
                    )  # get the object in queryset which have "id" value
                    # if the sent integer id was not found this part catch the validation error
                    if not queryset.exists(): 
                        raise ValidationError(detail=f"server id {by_server_id} not found (validation error).")
                # it is expecting an integer by sending a Boolean for example this part will catch the value error
                except ValueError: 
                    raise ValidationError(detail=f"server id {by_server_id} not found (value error).")
            else:
                raise AuthenticationFailed()

        serializer = ServerSerializer(queryset, many=True, context={"num_members": with_num_members})
        return Response(serializer.data)
