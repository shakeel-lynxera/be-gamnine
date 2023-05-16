from rest_framework import serializers
from user_deals.models import (
    Property,
    PropertyHouse,
    PropertyPlot,
    Whishlist,
    PropertyComercial
    )

class PropertyGenericSerializer(serializers.ModelSerializer):
    meta = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()

    class Meta:
        fields = ["id",
                 "title",
                 "description",
                 "purpose",
                 "property_type",
                 "category",
                 "city",
                 "location",
                 "marla",
                 "from_price",
                "to_price",
                 "total_price",
                 "contact_name",
                 "contact_number",
                 "is_wishlisted",
                 "is_notified",
                 "created_at",
                 "meta"
                 ]
        model = Property
    
    def get_meta(self, obj):
        try:
            instance = PropertyHouse.objects.get(property=obj)
            return {
                "house": instance.house,
                "street": instance.street,
                "bedrooms": instance.bedrooms,
                "bathrooms": instance.bathrooms
            }
        except:
            try:
                instance = PropertyPlot.objects.get(property=obj)
                return {
                    "series_from": instance.series_from,
                    "series_to": instance.series_to
                }
            except:
                try:
                    instance = PropertyComercial.objects.get(property=obj)
                    return {
                        "series_from": instance.series_from,
                        "series_to": instance.series_to,
                        "bedrooms": instance.bedrooms,
                        "bathrooms": instance.bathrooms
                    }
                except:
                    return None

    def get_is_wishlisted(self, obj):
        user = self.context.get("user")
        if Whishlist.objects.filter(user=user, deals=obj).exists():
            return True
        else:
            return False


class PropertyHouseSerializer(serializers.ModelSerializer):
    house = serializers.CharField(max_length=250, write_only=True)
    street = serializers.CharField(max_length=250, write_only=True)
    bedrooms = serializers.IntegerField(write_only=True)
    bathrooms = serializers.IntegerField(write_only=True)
    user  = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class  Meta:
        model = Property
        fields = [
            "id",
            "title",
            "description",
            "purpose",
            "property_type",
            "category",
            "city",
            "location",
            "marla",
            "from_price",
            "to_price",
            "total_price",
            "contact_name",
            "contact_number",
            "is_notified",
            "house",
            "street",
            "bedrooms",
            "bathrooms",
            "user"
            ]
    
    def create(self, validated_data):
        house = validated_data.pop('house')
        street = validated_data.pop('street')
        bedrooms = validated_data.pop('bedrooms')
        bathroom = validated_data.pop('bathrooms')
        instance = self.Meta.model.objects.create(**validated_data)
        PropertyHouse.objects.create(house=house, street=street, bedrooms=bedrooms, bathrooms=bathroom, property=instance)
        return instance
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["house"] = instance.propertyhouse.house
        data["street"] = instance.propertyhouse.street
        data["bedrooms"] = instance.propertyhouse.bedrooms
        data["bathrooms"] = instance.propertyhouse.bathrooms
        return data


class PropertyPlotSerializer(serializers.ModelSerializer):
    series_from = serializers.CharField(max_length=150, write_only=True)
    series_to = serializers.CharField(max_length=150, write_only=True)
    user  = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class  Meta:
        model = Property
        fields = [
            "id",
            "title",
            "description",
            "purpose",
            "property_type",
            "category",
            "city",
            "location",
            "marla",
            "from_price",
            "to_price",
            "total_price",
            "contact_name",
            "contact_number",
            "is_notified",
            "series_from",
            "series_to",
            "user"
            ]
    
    def create(self, validated_data):
        series_from = validated_data.pop('series_from')
        series_to = validated_data.pop('series_to')
        instance = self.Meta.model.objects.create(**validated_data)
        PropertyPlot.objects.create(series_from=series_from, series_to=series_to, property=instance)
        return instance
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["series_from"] = instance.propertyplot.series_from
        data["series_to"] = instance.propertyplot.series_to
        return data


class PropertyComercialSerializer(serializers.ModelSerializer):
    series_from = serializers.CharField(max_length=150, write_only=True)
    series_to = serializers.CharField(max_length=150, write_only=True)
    bedrooms = serializers.IntegerField(allow_null=True)
    bathrooms = serializers.IntegerField(allow_null=True)
    user  = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class  Meta:
        model = Property
        fields = [
            "id",
            "title",
            "description",
            "purpose",
            "property_type",
            "category",
            "city",
            "location",
            "marla",
            "from_price",
            "to_price",
            "total_price",
            "contact_name",
            "contact_number",
            "is_notified",
            "series_from",
            "series_to",
            "bedrooms",
            "bathrooms",
            "user"
            ]
    
    def create(self, validated_data):
        series_from = validated_data.pop('series_from')
        series_to = validated_data.pop('series_to')
        bedrooms = validated_data.pop('bedrooms')
        bathrooms = validated_data.pop('bathrooms')
        instance = self.Meta.model.objects.create(**validated_data)
        PropertyComercial.objects.create(
            series_from=series_from,
             series_to=series_to,
             bedrooms=bedrooms,
             bathrooms=bathrooms,
             property=instance
        )
        return instance
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["series_from"] = instance.propertycomercial.series_from
        data["series_to"] = instance.propertycomercial.series_to
        data["bedrooms"] = instance.propertycomercial.bedrooms
        data["bathrooms"] = instance.propertycomercial.bathrooms
        return data


class FilterPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = "__all__"


class FilterHouseSerializer(serializers.ModelSerializer):
    is_wishlisted = serializers.SerializerMethodField()
    
    def get_is_wishlisted(self, obj):
        user = self.context.get("user")
        if Whishlist.objects.filter(user=user, deals=obj.property).exists():
            return True
        else:
            return False
        

    class Meta:
        model = PropertyHouse
        fields = "__all__"
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["title"] = instance.property.title
        data["description"] = instance.property.description
        data["purpose"] = instance.property.purpose
        data["property_type"] = instance.property.property_type
        data["category"] = instance.property.category
        data["city"] = instance.property.city
        data["location"] = instance.property.location
        data["marla"] = instance.property.marla
        data["from_price"] = instance.property.from_price
        data["to_price"] = instance.property.to_price
        data["total_price"] = instance.property.total_price
        data["contact_name"] = instance.property.contact_name
        data["contact_number"] = instance.property.contact_number
        data["is_wishlisted"] = self.get_is_wishlisted(instance)
        return data


class FilterPlotSerializer(serializers.ModelSerializer):
    is_wishlisted = serializers.SerializerMethodField()
    
    def get_is_wishlisted(self, obj):
        user = self.context.get("user")
        if Whishlist.objects.filter(user=user, deals=obj.property).exists():
            return True
        else:
            return False
    
    class Meta:
        model = PropertyPlot
        fields = "__all__"
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["title"] = instance.property.title
        data["description"] = instance.property.description
        data["purpose"] = instance.property.purpose
        data["property_type"] = instance.property.property_type
        data["category"] = instance.property.category
        data["city"] = instance.property.city
        data["location"] = instance.property.location
        data["marla"] = instance.property.marla
        data["from_price"] = instance.property.from_price
        data["to_price"] = instance.property.to_price
        data["total_price"] = instance.property.total_price
        data["contact_name"] = instance.property.contact_name
        data["contact_number"] = instance.property.contact_number
        data["is_wishlisted"] = self.get_is_wishlisted(instance)
        return data


class FilterCommercialSerializer(serializers.ModelSerializer):
    is_wishlisted = serializers.SerializerMethodField()

    def get_is_wishlisted(self, obj):
        user = self.context.get("user")
        if Whishlist.objects.filter(user=user, deals=obj.property).exists():
            return True
        else:
            return False

    class Meta:
        model = PropertyPlot
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["title"] = instance.property.title
        data["description"] = instance.property.description
        data["purpose"] = instance.property.purpose
        data["property_type"] = instance.property.property_type
        data["category"] = instance.property.category
        data["city"] = instance.property.city
        data["location"] = instance.property.location
        data["marla"] = instance.property.marla
        data["from_price"] = instance.property.from_price
        data["to_price"] = instance.property.to_price
        data["total_price"] = instance.property.total_price
        data["contact_name"] = instance.property.contact_name
        data["contact_number"] = instance.property.contact_number
        data["is_wishlisted"] = self.get_is_wishlisted(instance)
        return data
