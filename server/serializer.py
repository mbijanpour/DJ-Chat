# the serializer is used for forming the data we retrieved from the data base
# into a format that can be returned to the endpoint for the user

from rest_framework import serializers


from .models import Server, Channel


class ChannelSerializer(serializers.ModelSerializer):
    """
    if we wanted to return the channels associated with a server whenever
    we returned a server we should first serialize it as before but in the
    serverSerializer end we have to set up the RELATED_NAME as the channel serializer
    to set up the connection between these two models.
    """

    class Meta:
        model = Channel
        fields = "__all__"


class ServerSerializer(serializers.ModelSerializer):
    """
    this is a new field we want to add in our serialized data in order to count the
    members within one server and return it instead of the member felid in the model
    """

    num_members = serializers.SerializerMethodField()
    # many=True parameter is used to tell the view that multiply objects would be sent
    channel_server = ChannelSerializer(many=True)

    class Meta:
        model = Server
        exclude = ("member",)

    def get_num_members(self, obj):
        # obj is the instance of the server object thats being serialized

        if hasattr(obj, "num_members"):
            return obj.num_members
        return None

    def to_representation(self, instance):
        """
        in here the instance is the serialized server object
        so the data value is the serialized server object itself (all the fields)
        but it also include the num_members field that we added using the get_num_members method
        from self we can have access to the context that contains the request object
        meaning the content we passed through the view is accessed via self.
        """

        data = super().to_representation(instance)
        num_members = self.context.get("num_members")
        if not num_members:
            data.pop("num_members", None)
        return data
