from django.urls import path
from Buses import views
urlpatterns = [
    path("", views.BusesData.as_view(), name = "all buses"),
    path("source_dest_options/", views.SourceDestOptions.as_view(), name = "user options"),
    path("<int:id>/", views.BusInfo.as_view(), name = "bus info"),
    path("booking_details/", views.BookInfo.as_view(), name = "book info")
]
