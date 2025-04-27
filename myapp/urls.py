from django.urls import path
from .views import *  # or whatever view you're using
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', home_view, name='home'),  # Root path
    path('about/', About_view, name='about'),
    path('contact/', Contact_view, name='contact'),
    path('login/', LogIn_view, name='login'),  # Root path
    path('logout/', LogOut_view, name='logout'),  # Root path
    path('signup/', Singup_view, name='signup'),
    path('search/', Search, name='search'),
    path('book/<int:venue_id>/',book_event, name='book_event'),
    path('chat/',Chat_view, name='chat'),
    path('chat/send/', Send_message, name='chat_send'),
    path('services/', Services_view, name='services'),
    path('my-bookings/',My_bookings, name='my_bookings'),
    path('update/<int:booking_id>/', Update_booking, name='update_booking'),
    path('cancel/<int:booking_id>/', Cancel_booking, name='cancel_booking'),
   

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
