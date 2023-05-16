from rest_framework.permissions import IsAuthenticated
from baselayer.baseapiviews import BaseAPIView
from baselayer.baseauthentication import JWTAuthentication
from user_deals.utilies import custom_pagination
from utils.baseutils import get_first_error_message_from_serializer_errors
from utils.mock_responses import ResponseMessages
from user_deals.serializers import (
    FilterPlotSerializer,
    PropertyGenericSerializer,
    PropertyHouseSerializer,
    PropertyPlotSerializer,
    PropertyComercialSerializer,
    FilterHouseSerializer, FilterCommercialSerializer
)
from user_deals.models import (
    Property,
    PropertyHouse,
    PropertyPlot,
    PropertyType,
    Whishlist,
    PropertyComercial,
    PropertyPurpose
)

# Create your views here.
class HouseDealsView(BaseAPIView):
    """House Property Deals"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = PropertyHouseSerializer

    def post(self, request, *args, **kwargs):
        """
        Add House Deal
        Request URL: /deals/house-deal/
        Header: Authorization: "JWT <token>"
        Request Body:
        {
            "title": "property title",
            "description": "property description",
            "purpose": "required",
            "property_type": "house",
            "category": "property category",
            "city": "Islamabad",
            "location": "Faisal town",
            "unit": 12.99,
            "marla": 5.00,
            "total_price": 12345843332,
            "contact_name": "Faisal",
            "contact_number": "03333333333",
            "house": "House ABC",
            "street": "i/9",
            "bedrooms": 5,
            "bathrooms": 3
        }
        Response:
        {
            "success": true,
            "payload": {
                "title": "property title",
                "description": "property description",
                "purpose": "required",
                "property_type": "house",
                "category": "property category",
                "city": "Islamabad",
                "location": "Faisal town",
                "unit": 12.99,
                "marla": 5.0,
                "total_price": "12345843332.00",
                "contact_name": "Faisal",
                "contact_number": "03333333333",
                "is_notified": true,
                "house": "House ABC",
                "street": "i/9",
                "bedrooms": 5,
                "bathrooms": 3
            },
            "message": "Ticket created successfully."
        }
        
        """
        serializer_data = self.serializer_class(data=request.data, context={"request": request})
        if not serializer_data.is_valid():
            return self.send_bad_request_response(
                message=get_first_error_message_from_serializer_errors(
                    serialized_errors=serializer_data.errors,
                    default_message=ResponseMessages.SOMETHING_MISSING_IN_RESET_PASSWORD_REQUEST,
                )
            )
    
        ticket = serializer_data.save()
        configure_firebase_notification(ticket)
        return self.send_success_response(
            message=ResponseMessages.TICKET_CREATED,
            payload= self.serializer_class(ticket).data
        )


class PlotDealsView(BaseAPIView):
    """Plot Property Deals"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = PropertyPlotSerializer

    def post(self, request, *args, **kwargs):
        """
        Add House Deal
        Request URL: /deals/plot-deal/
        Header: Authorization: "JWT <token>"
        Request Body:
            {
                "title": "property title",
                "description": "property description",
                "purpose": "required",
                "property_type": "house",
                "category": "property category",
                "city": "Islamabad",
                "location": "Faisal town",
                "unit": 12.99,
                "marla": 5.00,
                "total_price": 12345843332,
                "contact_name": "Faisal",
                "contact_number": "03333333333",
                "series_from": "1005",
                "series_to": "2000"
            }
        Response:
            {
                "success": true,
                "payload": {
                    "title": "property title",
                    "description": "property description",
                    "purpose": "required",
                    "property_type": "house",
                    "category": "property category",
                    "city": "Islamabad",
                    "location": "Faisal town",
                    "unit": 12.99,
                    "marla": 5.0,
                    "total_price": "12345843332.00",
                    "contact_name": "Faisal",
                    "contact_number": "03333333333",
                    "is_notified": true,
                    "series_from": "1005",
                    "series_to": "2000"
                },
                "message": "Ticket created successfully."
            }
        """
        serializer_data = self.serializer_class(data=request.data, context={"request": request})
        if not serializer_data.is_valid():
            return self.send_bad_request_response(
                message=get_first_error_message_from_serializer_errors(
                    serialized_errors=serializer_data.errors,
                    default_message=ResponseMessages.SOMETHING_MISSING_IN_RESET_PASSWORD_REQUEST,
                )
            )
    
        ticket = serializer_data.save()
        return self.send_success_response(
            message=ResponseMessages.TICKET_CREATED,
            payload= self.serializer_class(ticket).data
        )


class PublicDealsView(BaseAPIView):
    """Public Deals"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = PropertyGenericSerializer
    queryset = Property.objects.all()
    
    def get(self, request, *args, **kwargs):
        query_params = dict()
        deal_type = kwargs['deal_type']
        page_number = kwargs['page']
        search_title = kwargs["search_title"]

        if not search_title == "default":
            query_params["title__icontains"] = search_title

        query_params.update({
            "purpose": deal_type,
        })

        instances = self.queryset.filter(**query_params).exclude(user=request.user).order_by('-created_at')
        if not instances:
            return self.send_success_response(ResponseMessages.NOT_FOUND)
            
        entries, pagination = custom_pagination(instances, page_number, 10)
        serailzered_data = self.serializer_class(entries, many=True, context={"user": request.user}).data
        data = {
            "data": serailzered_data,
            "pagination": pagination
        }
        return self.send_success_response(ResponseMessages.SUCCESS, data)


class CommercialDealsView(BaseAPIView):
    """Comercial Property Deals"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = PropertyComercialSerializer

    def post(self, request, *args, **kwargs):
        """
        Add House Deal
        Request URL: /deals/comercial-deal/
        Header: Authorization: "JWT <token>"
        Request Body:
        {
            "title": "property title",
            "description": "property description",
            "purpose": "required",
            "property_type": "house",
            "category": "property category",
            "city": "Islamabad",
            "location": "Faisal town",
            "unit": 12.99,
            "marla": 5.00,
            "total_price": 12345843332,
            "contact_name": "Faisal",
            "contact_number": "03333333333",
            "series_from": "r12",
            "series_to": "r15",
            "bedrooms": 5,
            "bathrooms": 3
        }
        Response:
        {
            "success": true,
            "payload": {
                "title": "property title",
                "description": "property description",
                "purpose": "required",
                "property_type": "house",
                "category": "property category",
                "city": "Islamabad",
                "location": "Faisal town",
                "unit": 12.99,
                "marla": 5.0,
                "total_price": "12345843332.00",
                "contact_name": "Faisal",
                "contact_number": "03333333333",
                "is_notified": true,
                "series_from": "r12",
                "series_to": "r15",
                "bedrooms": 5,
                "bathrooms": 3
            },
            "message": "Ticket created successfully."
        }
        
        """
        serializer_data = self.serializer_class(data=request.data, context={"request": request})
        if not serializer_data.is_valid():
            return self.send_bad_request_response(
                message=get_first_error_message_from_serializer_errors(
                    serialized_errors=serializer_data.errors,
                    default_message=ResponseMessages.SOMETHING_MISSING_IN_RESET_PASSWORD_REQUEST,
                )
            )
    
        ticket = serializer_data.save()
        return self.send_success_response(
            message=ResponseMessages.TICKET_CREATED,
            payload= self.serializer_class(ticket).data
        )


class FilterDealsView(BaseAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = FilterHouseSerializer
    queryset = Property.objects.all()
    
    def get(self, request, *args, **kwargs):
        key_values = {}
        page_number = kwargs['page']
        property_type = request.GET.get('property_type',None)
        if PropertyType.HOUSE == property_type:
            category = request.GET.get('category',None)
            city = request.GET.get('city',None)
            location = request.GET.get('location',None)
            house = request.GET.get('house',None)
            street = request.GET.get('street',None)
            marla = request.GET.get('marla',None)
            bedrooms = request.GET.get('bedrooms',None)
            bathrooms = request.GET.get('bathrooms',None)
            price_from = request.GET.get('price_from',None)
            price_to = request.GET.get('price_to',None)
            purpose = request.GET.get("purpose",None)


            if purpose is not None:
                key_values["property__purpose__icontains"] = purpose
            if category is not None:
                key_values["property__category__icontains"]=category 
            if city is not None:
                key_values["property__city__icontains"]=city 
            if location is not None:
                key_values["property__location__icontains"]=location 
            if house is not None:
                key_values["house__icontains"]=house 
            if street is not None:
                key_values["street__icontains"]=street
            if bedrooms is not None:
                key_values["bedrooms"]= bedrooms
            if bathrooms is not None:
                key_values["bathrooms"]= bathrooms
            if marla is not None:
                key_values["property__marla"] = marla
            if price_from is not None:
                key_values["property__from_price__gte"] = price_from
            if price_to is not None:
                key_values["property__to_price__lte"] = price_to
            key_values["property__property_type"] = PropertyType.HOUSE
            instances = PropertyHouse.objects.filter(**key_values)
            instances, pagination = custom_pagination(instances, page_number, 10)
            serialized_data = FilterHouseSerializer(instances, many=True, context = {"user": request.user}).data
            payload = {
                "data":  serialized_data,
                "pagination": pagination
            }
        
        elif PropertyType.PLOT == property_type:
            category = request.GET.get('category',None)
            city = request.GET.get('city',None)
            location = request.GET.get('location',None)
            marla = request.GET.get('marla',None)
            price_from = request.GET.get('price_from',None)
            price_to = request.GET.get('price_to',None)
            series_from = request.GET.get('series_from',None)
            series_to = request.GET.get('series_to',None)
            purpose = request.GET.get("purpose",None)

            if purpose is not None:
                key_values["property__purpose__icontains"] = purpose
            if category is not None:
                key_values["property__category__icontains"]=category 
            if city is not None:
                key_values["property__city__icontains"]=city 
            if location is not None:
                key_values["property__location__icontains"]=location 
            if series_from is not None:
                key_values["series_from__gte"]= series_from
            if series_to is not None:
                key_values["series_to__lte"]= series_to
            if marla is not None:
                key_values["property__marla"] = marla
            if price_from is not None:
                key_values["property__from_price__gte"] = price_from
            if price_to is not None:
                key_values["property__to_price__lte"] = price_to
            key_values["property__property_type"] = PropertyType.PLOT
            instances = PropertyPlot.objects.filter(**key_values)
            instances, pagination = custom_pagination(instances, page_number, 10)
            serialized_data = FilterPlotSerializer(instances, many=True, context = {"user": request.user}).data
            payload = {
                "data":  serialized_data,
                "pagination": pagination
            }

        elif PropertyType.COMMERCIAL == property_type:
            category = request.GET.get('category',None)
            city = request.GET.get('city',None)
            location = request.GET.get('location',None)
            marla = request.GET.get('marla',None)
            price_from = request.GET.get('price_from',None)
            price_to = request.GET.get('price_to',None)
            series_from = request.GET.get('series_from',None)
            series_to = request.GET.get('series_to',None)
            bedrooms = request.GET.get('bedrooms',None)
            bathrooms = request.GET.get('bathrooms',None)

            if category is not None:
                key_values["property__category__icontains"] = category
            if city is not None:
                key_values["property__city__icontains"] = city
            if location is not None:
                key_values["property__location__icontains"] = location
            if series_from is not None:
                key_values["series_from__gte"] = series_from
            if series_to is not None:
                key_values["series_to__lte"] = series_to
            if bedrooms is not None:
                key_values["bedrooms"] = bedrooms
            if bathrooms is not None:
                key_values["bathrooms"] = bathrooms
            if marla is not None:
                key_values["property__marla"] = marla
            if price_from is not None:
                key_values["property__from_price__gte"] = price_from
            if price_to is not None:
                key_values["property__to_price__lte"] = price_to
            key_values["property__property_type"] = PropertyType.COMMERCIAL
            instances = PropertyComercial.objects.filter(**key_values)
            instances, pagination = custom_pagination(instances, page_number, 10)
            serialized_data = FilterCommercialSerializer(instances, many=True, context = {"user": request.user}).data
            payload = {
                "data":  serialized_data,
                "pagination": pagination
            }

        else:
            return self.send_bad_request_response(ResponseMessages.INVALID_CATEGORY)
        return self.send_success_response(ResponseMessages.SUCCESS,payload= payload)


class WishlistView(BaseAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Whishlist.objects.all()
    serializer_class = FilterHouseSerializer
    
    def post(self, request, *args, **kwargs):
        property_id = kwargs.get('property_id', None)
        instance = Property.objects.filter(id=property_id).first()
        if instance:    
            object, cr = Whishlist.objects.update_or_create(
                user = request.user,
                deals = instance
            )
            return self.send_success_response(ResponseMessages.SUCCESS)
        else:
            return self.send_bad_request_response(ResponseMessages.INVALID_PROPERTY_ID)

    def delete(self, request, *args, **kwargs):
        property_id = kwargs.get('property_id', None)
        instance = Property.objects.filter(id=property_id).first()
        if instance:
            self.queryset.filter(
                user = request.user,
                deals = instance
            ).delete()
            return self.send_success_response(ResponseMessages.SUCCESS)
        else:
            return self.send_bad_request_response(ResponseMessages.INVALID_PROPERTY_ID)

    def get(self, request, *args, **kwargs):
        query_params = dict()
        page_number = self.kwargs.get('page_number', 1)
        property_type = self.kwargs.get('property_type', None)
        deal_type = self.kwargs.get('deal_type', PropertyPurpose.REQUIRED)
        search_title = self.kwargs.get('search_title', "default")
        if not search_title == "default":
            query_params["deals__title__icontains"] = search_title

        if not property_type == "default":
            query_params["deals__property_type"] = property_type

        if property_type is None or property_type == "default" or property_type == "":
            instances = Property.objects.filter(id__in=request.user.whishlists.filter(**query_params)
                                                .values_list('deals__id', flat=True), purpose=deal_type).order_by('-created_at')
        else:
            instances = Property.objects.filter(id__in=request.user.whishlists.filter(**query_params)
                                    .values_list('deals__id', flat=True), purpose=deal_type).order_by('-created_at')
        entries, pagination = custom_pagination(instances, page_number, 10)
        serailzered_data = PropertyGenericSerializer(entries, many=True, context={"user": request.user}).data
        data = {
            "data": serailzered_data,
            "pagination": pagination
        }
        return self.send_success_response(ResponseMessages.SUCCESS, payload=data)


class InventoryView(BaseAPIView):
    """User Inventory"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = PropertyGenericSerializer
    queryset = Property.objects.all()

    def get(self, request, *args, **kwargs):
        query_params = dict()
        page_number = self.kwargs.get('page', 1)
        deal_type = self.kwargs.get('deal_type', PropertyPurpose.REQUIRED)
        property_type = self.kwargs.get('property_type', None)
        search_title = self.kwargs.get('search_title', "default")

        if not search_title == "default":
            query_params["title__icontains"] = search_title

        if not property_type == "default":
            query_params["property_type"] = property_type

        query_params.update({
            "user": request.user,
            "purpose": deal_type
        })


        if not property_type or property_type == "" or property_type == "default":
            entries, pagination = custom_pagination(self.queryset.filter(**query_params).order_by('-created_at'), page_number, 10)
        else:
            entries, pagination= custom_pagination(self.queryset.filter(**query_params).order_by('-created_at'), page_number, 10)
        serailzered_data = self.serializer_class(entries, many=True, context={"user": request.user}).data
        data = {
            "data": serailzered_data,
            "pagination": pagination
        }
        return self.send_success_response(ResponseMessages.SUCCESS, data)
