from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.utils.timezone import localtime
from django.contrib.auth.models import User
from django.contrib import messages 
from .models import *
from django.utils.dateparse import parse_date
import textwrap
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from itertools import chain
from django.contrib.auth.decorators import login_required



def home_view(request):
    caterings = CateringOption.objects.all()
    return render(request, 'home.html', {'caterings': caterings})


def About_view(request):
    data = About.objects.all()
    return render(request, 'about.html', {'about_info': data})


def Contact_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        message = request.POST.get('message')

        # Save to database
        Contact.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile=mobile,
            message=message
        )
        messages.success(request, "Your message has been submitted successfully!")
        return redirect('home')
    
    return render(request, 'contactus.html')

def Search(request):
    venue_type = request.GET.get('venue_type')
    location = request.GET.get('location')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    attendees = request.GET.get('attendees')
    catering = request.GET.get('catering')

    venues = Venue.objects.all()
    
    if " ":
        messages.warning(request,"please chooose all fileds")
    
    if location:
        venues = venues.filter(location=location)
    if venue_type:
        venues = venues.filter(venue_type=venue_type)
    if min_price:
        venues = venues.filter(price__gte=min_price)
    if max_price:
        venues = venues.filter(price__lte=max_price)
    if attendees:
        venues = venues.filter(capacity__gte=attendees)
    if catering:
        venues = venues.filter(catering__id=catering)

    return render(request, 'results.html', {'venues': venues,'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY})


@login_required
def book_event(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        attendees = request.POST.get('attendees')
        event_date_str = request.POST.get('event_date')
        event_date = parse_date(event_date_str)  # convert string to date
        need_transport = request.POST.get('need_transport') == 'yes'
        transport_type = request.POST.get('transport_type') if need_transport else None

        booking = Booking.objects.create(
            user=request.user, 
            venue=venue,
            name=name,
            email=email,
            phone=phone,
            attendees=attendees,
            event_date=event_date,
            need_transport=need_transport,
            transport_type=transport_type,
            price=venue.price,
            location=venue.location,
            
        )
        booking.save()
        booking_time_ist = localtime(booking.timestamp)
        home_url = request.build_absolute_uri('/')
        email_message = textwrap.dedent(f"""
        Hi {name},

        Thank you for booking with us! Your venue reservation has been successfully confirmed.
        Booking Details:
           
        📍 Venue: {venue.for_booking}
        📍 location: {venue.location}
        📍 facilitator: {venue.facilitator}
        💰 Price: {venue.price}
        📅 Event Date: {event_date}
        📆 Booking Time: {booking_time_ist.strftime('%Y-%m-%d %I:%M %p')} 
        👥 Attendees: {attendees}
        📞 Phone: {phone}
        📧 Email: {email}

        We're excited to host your event and ensure everything goes smoothly. If you have any special requests or need assistance, feel free to reach out—we're here to help!

        You can view or manage your booking anytime from your account: {home_url}

        Looking forward to seeing you there!
        Regards,
        Event Team
        """)

        # Send email confirmation
        send_mail(
            subject=' Your Venue Booking is Confirmed! 🎉',
            message=email_message,
            from_email='noreply@example.com',
            recipient_list=[email],
            fail_silently=False,
        )

        return redirect('home')
    return render(request, 'booking.html', {'venue': venue})



@login_required
def My_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
 
    return render(request, 'booking/my_booking.html', {'bookings': bookings})

@login_required
def Update_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    venues = Venue.objects.all()  # 🛠 ADD THIS

    if request.method == 'POST':
        booking.name = request.POST.get('name')
        booking.event_date = request.POST.get('event_date')
        booking.attendees = request.POST.get('attendees')
        
        venue_id = request.POST.get('venue')
        if venue_id:
            venue = get_object_or_404(Venue, id=venue_id)
            booking.venue = venue
            booking.location = venue.location
            booking.price = venue.price
        
        booking.save()
        messages.success(request, 'Booking updated successfully!')
        return redirect('my_bookings')

    return render(request, 'booking/update_booking.html', {  
        'booking': booking,
        'venues': venues,
    })



@login_required
def Cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.delete()
    return redirect('my_bookings')


def Chat_view(request):
    return render(request, 'home.html')


@csrf_exempt
def Send_message(request):
     if request.method == 'POST':
        data = json.loads(request.body)
        user_msg = data.get('message', '').strip().lower()

        # Try to find a bot reply
        pair =PairMsg.objects.filter(user_query__iexact=user_msg).first()

        if pair:
            bot_reply = pair.bot_reply
        else:
            bot_reply = "Sorry, I don't understand that yet."

        return JsonResponse({'reply': bot_reply})
    
    


def Services_view(request):
    event_services = Service.objects.filter(category='event').prefetch_related('types', 'content_ideas')
    catering_services = Service.objects.filter(category='catering').prefetch_related('types', 'content_ideas')
    other_services = Service.objects.filter(category='other').prefetch_related('types', 'content_ideas')
    catering_and_other_services = list(chain(catering_services, other_services))
    return render(request, 'services.html', {
        'event_services': event_services,
        'catering_services': catering_services,
        'other_services': other_services,
        'catering_and_other_services': catering_and_other_services,
    })
    
    
    
    


def LogIn_view(request):
    if request.method == "POST":
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')
        next_url = request.POST.get('next')

       
        user = authenticate(request, username=username_or_email, password=password)

       
        if user is None:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            return redirect(next_url) if next_url else redirect('home')# Redirect to your home/dashboard
        else:
            return render(request, 'login.html', {'message': 'Invalid credentials'})

    return render(request, 'login.html', {'next': request.GET.get('next', '')})

# Logout view
def LogOut_view(request):
    logout(request)
    return redirect('login')  # Use named URL pattern 'login'

# Signup view
def Singup_view(request):
    
    if request.method == "POST":
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
       
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                
            )
            user.save()

            # Send confirmation email
            send_mail(
                "Welcome to Our Site!",
                f"Hi {first_name}, thanks for registering.",
                settings.EMAIL_HOST_USER ,
                [email],
                fail_silently=False,
            )

            messages.success(request, "Account created successfully. Check your email!")
            login(request, user)
            return render(request,'home.html')
    
    return render(request, 'signup.html')