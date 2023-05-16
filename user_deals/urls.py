from django.urls import path
from user_deals.views import (
    HouseDealsView,
    PlotDealsView,
    PublicDealsView,
    FilterDealsView,
    CommercialDealsView,
    WishlistView,
    InventoryView
    )

urlpatterns = [
    path("house-deal/", HouseDealsView.as_view(), name="new-deal"),
    path("plot-deal/", PlotDealsView.as_view(), name="new-deal"),
    path("commercial-deal/", CommercialDealsView.as_view(), name="new-deal"),
    path("get-public-deals/<str:deal_type>/<str:search_title>/<int:page>/", PublicDealsView.as_view(), name="available-deals"),
    path("filter/<int:page>/", FilterDealsView.as_view(), name="filter deal"),
    path("wishlist/<str:deal_type>/<str:property_type>/<str:search_title>/<int:page>/", WishlistView.as_view(), name="wishlist"),
    path("wishlist/<uuid:property_id>/", WishlistView.as_view(), name="wishlist"),
    path("inventory/<str:deal_type>/<str:property_type>/<str:search_title>/<int:page>/", InventoryView.as_view(), name="inventory"),
]
