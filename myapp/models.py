
from django.db import models
from django.core.exceptions import ValidationError
import requests
from django.conf import settings
from django.contrib.auth.models import User

class About(models.Model):
    eve_name=models.CharField(max_length=100)
    eve_discription=models.TextField()
    image = models.ImageField(upload_to='about_images/')
    def __str__(self):
        return self.eve_name


class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class CateringOption(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Venue(models.Model):
    VENUE_TYPES = [
        ('hall', 'Hall'),
        ('hotel', 'Hotel'),
        ('lawn', 'Lawn'),
    ]
    for_booking= models.CharField(max_length=100)
    facilitator= models.CharField(max_length=300,null=True,blank=True)
    venue_type = models.CharField(max_length=10, choices=VENUE_TYPES)
    location = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()
    catering = models.ManyToManyField(CateringOption)

    def __str__(self):
        return self.for_booking
    
    
    def save(self, *args, **kwargs):
        if self.location and (self.latitude is None or self.longitude is None):
            self._fetch_coordinates()
        super().save(*args, **kwargs)

    def _fetch_coordinates(self):
        address = f"{self.location}, India"
        api_key = settings.GOOGLE_MAPS_API_KEY
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
        response = requests.get(url)
        data = response.json()
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            self.latitude = location['lat']
            self.longitude = location['lng']
        else:
            raise ValidationError("Could not fetch coordinates for the given address.")

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=300,default='Unknown' )
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True) 
    attendees= models.PositiveIntegerField()
    email = models.EmailField()
    event_date = models.DateField()  # Date the event is booked for
    timestamp = models.DateTimeField(auto_now_add=True)  # Booking creation time
    need_transport = models.BooleanField(default=False)
    transport_type = models.CharField(max_length=50,blank=True,null=True )

    
    def __str__(self):
        return f"{self.name} booking at {self.venue.for_booking} on {self.event_date}"



class PairMsg(models.Model):
    user_query = models.CharField(max_length=255, unique=True)
    bot_reply = models.TextField()

    def __str__(self):
        return f"User: {self.user_query} → Bot: {self.bot_reply[:30]}"
   
class Service(models.Model):
    CATEGORY_CHOICES = [
        ('event', 'Event'),
        ('catering', 'Catering'),
        ('other', 'Other'),
    ]
    name=models.CharField(max_length=120)
    image = models.ImageField(upload_to='service_images/')
    decs=models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='event')  
    
    def __str__(self):
        return self.name


class EventType(models.Model):
    service = models.ForeignKey(Service, related_name='types', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ContentIdea(models.Model):
    service = models.ForeignKey(Service, related_name='content_ideas', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name