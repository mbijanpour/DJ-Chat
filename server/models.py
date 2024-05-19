from django.conf import settings
from django.db import models


class Category(models.Model):
    """
    note that the sequence of creating the models is important.
    the category is created first, then the server, then the channel.
    """

    name = models.CharField(max_length=50)
    description = models.TextField(
        blank=True, null=True
    )  # the blank is for forms and null is for databases.

    def __str__(self):
        return self.name


class Server(models.Model):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="server_owner"
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="server_category"
    )  # each category can be associated with multiple servers so we have to use ForeignKey for server.
    description = models.TextField(
        null=True
    )  # the blank is for forms and null is for databases.
    member = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="server_member"
    )

    def __str__(self):
        return self.name


class Channel(models.Model):
    """
    the channel are like small rooms within a server,
    each channel has a name, topic, and server
    server can have multiple channel where as channel can only be
    associated with one server.
    same goes for the owner of the channel.
    """

    name = models.CharField(max_length=50)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="channel_owner"
    )
    topic = models.CharField(max_length=50)
    server = models.ForeignKey(
        Server, on_delete=models.PROTECT, related_name="channel_server"
    )  # in the description of the class

    def save(self, *args, **kwargs):
        """
        costume save method to save the name of the channel to lower
        case, as seen the name is only overridden to be lowercase.
        """
        self.name = self.name.lower()
        # args are just the vars that pass in to the function.
        # kwargs are the keyword arguments that pass in to the function. (same as arg but with key value pairs)
        # super is used to call the parent class save method.
        super(Channel, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
