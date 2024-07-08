from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import response

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

        if category:
            self.queryset = self.queryset.filter(
                category__name=category
            )  # get the object in queryset which have "category"

        serializer = ServerSerializer(self.queryset, many=True)
        return Response(serializer.data)
