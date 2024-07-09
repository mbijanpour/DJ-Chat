from django.conf import settings
from django.db import models
from django.shortcuts import get_object_or_404
from django.dispatch import receiver

from .validator import validate_icon_image_size, validate_image_file_extension


def category_icon_upload_path(instance, filename):
    """
    the path media/ has been set in the setting for media files
    so the path would be something like media/Category...
    """
    return f"Category/{instance.id}/category_icon/{filename}"


class Category(models.Model):
    """
    note that the sequence of creating the models is important.
    the category is created first, then the server, then the channel.
    """

    name = models.CharField(max_length=50)
    description = models.TextField(
        blank=True, null=True
    )  # the blank is for forms and null is for databases.
    icon = models.FileField(
        null=True,
        blank=True,
        upload_to=category_icon_upload_path,
        validators=[validate_icon_image_size, validate_image_file_extension],
    )  # this field is optional and the path is as defined in the method

    def save(self, *args, **kwargs):
        """
        we wanted to save in a way that if the icon is changed, the old icon is deleted.
        we first check if the current object has been saved or not then we go as proceed
        but the main point is that we just use self.id to check because we are within the
        class and we can directly access it within the class scope.
        """

        if self.id:
            existing = get_object_or_404(Category, id=self.id)
            if existing.icon != self.icon:
                existing.icon.delete(
                    save=False
                )  # we dont want to save the object here so False.
        super(Category, self).save(*args, **kwargs)

    @receiver(models.signals.pre_delete, sender=Category)
    def category_delete_icon_on_delete(sender, instance, using, **kwargs):
        """
        in this one we want to delete the icon when we delete the category, so we use django signals
        as to listen to the pre_delete signal and then delete the icon.
        the sender value is "appName.modelname" or since we are in the same class we can use Category
        and the using argument is to choose the database we want to
        interact with in case of the use of multiple data bases.
        """

        # we have to iterate through the fields of the instance that we wanted to delete
        # after finding the icon field we get th file in that field and then delete it.
        for field in instance._meta.get_fields():
            if field.name == "icon":
                file = getattr(instance, field.name)
                if file:
                    file.delete(
                        save=False
                    )  # we dont want to save that instance so False

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


def server_icon_upload_path(instance, filename):
    """
    the path media/ has been set in the setting for media files
    so the path would be something like media/Server...
    """
    return f"Server/{instance.id}/server_icon/{filename}"


def server_banner_upload_path(instance, filename):
    """
    the path media/ has been set in the setting for media files
    so the path would be something like media/Server...
    """
    return f"Server/{instance.id}/server_banner/{filename}"


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
    banner = models.ImageField(
        upload_to=server_banner_upload_path,
        null=True,
        blank=True,
        validators=[validate_image_file_extension],
    )
    icon = models.ImageField(
        upload_to=server_icon_upload_path,
        null=True,
        blank=True,
        validators=[validate_icon_image_size, validate_image_file_extension],
    )

    def save(self, *args, **kwargs):
        """
        the DocString is provided in Category section
        """

        if self.id:
            existing = get_object_or_404(Category, id=self.id)
            if existing.icon != self.icon:
                existing.icon.delete(save=False)
            if existing.banner != self.banner:
                existing.banner.delete(save=False)
        super(Category, self).save(*args, **kwargs)

    @receiver(models.signals.pre_delete, sender=server)
    def category_delete_icon_on_delete(sender, instance, using, **kwargs):
        """
        the DocString is provided in Category section
        """

        for field in instance._meta.get_fields():
            if field.name in ["icon", "banner"]:
                file = getattr(instance, field.name)
                if file:
                    file.delete(save=False)

    def __str__(self):
        return self.name
