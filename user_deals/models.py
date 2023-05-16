from django.db import models
from baselayer.basemodels import LogsMixin
from users.models import User


# Choices class
class PropertyPurpose(models.TextChoices):
    SALE = "sale", "Sale"
    REQUIRED = "required", "Required"
    RENT = "rent", "Rent"


class PropertyType(models.TextChoices):
    HOUSE = "house", "House"
    PLOT = "plot", "Plot"
    COMMERCIAL = "commercial", "Commercial"


class Property(LogsMixin):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name='properties')
    title = models.CharField(max_length = 100)
    description = models.TextField()
    purpose = models.CharField(max_length=50, choices=PropertyPurpose.choices)
    property_type = models.CharField(max_length=50, choices=PropertyType.choices)
    category = models.CharField(max_length=50)
    city = models.CharField(max_length= 50)
    location = models.TextField()
    #unit = models.FloatField(max_length=50)
    marla = models.IntegerField()
    total_price = models.DecimalField(max_digits=15, decimal_places=2, default=None, null=True, blank=True)
    from_price = models.DecimalField(max_digits=15, decimal_places=2, default=None, null=True, blank=True)
    to_price = models.DecimalField(max_digits=15, decimal_places=2, default=None, null=True, blank=True)
    contact_name = models.CharField(max_length=50)
    contact_number = models.CharField(max_length=50)
    is_notified = models.BooleanField(default=True)


# Property Houses class (More attributes can be added later)
class PropertyHouse(LogsMixin):
    house = models.CharField(max_length=250)
    street = models.CharField(max_length=250)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    property = models.OneToOneField(Property, on_delete = models.CASCADE)


# Property Plot class (More attributes can be added later)
class PropertyPlot(LogsMixin):
    series_from = models.CharField(max_length=150)
    series_to = models.CharField(max_length=150)
    property = models.OneToOneField(Property, on_delete = models.CASCADE)

class PropertyComercial(LogsMixin):
    bedrooms = models.IntegerField(null=True, blank=True)
    bathrooms = models.IntegerField(null=True, blank=True)
    series_from = models.CharField(max_length=150)
    series_to = models.CharField(max_length=150)
    property = models.OneToOneField(Property, on_delete = models.CASCADE)
    

class Whishlist(LogsMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='whishlists')
    deals = models.ForeignKey(Property, on_delete=models.CASCADE)
