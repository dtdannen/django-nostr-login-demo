from django.shortcuts import render
from aionostr.event import Event
import json
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User


def verify_signed_event(signed_event):
    signed_event = Event(pubkey=signed_event["pubkey"], content=signed_event["content"],
                         kind=signed_event["kind"], created_at=signed_event["created_at"],
                         tags=signed_event["tags"], id=signed_event["id"], sig=signed_event["sig"])

    return signed_event.verify()


def handle_login(request):
    if request.method != 'POST':
        return request

    if 'signedEvent' in request.POST:
        print("signed event is: {}".format(request.POST['signedEvent']))
        signed_event_dict = json.loads(request.POST['signedEvent'])
        if verify_signed_event(signed_event_dict):
            print("SUCCESS in verifying signed event")
            pubkey = signed_event_dict['pubkey']

            # check if the user exists in the database with the public key
            print("attempting to find user")
            user = User.objects.filter(username=pubkey).first()
            if user is None:
                print("user not found, about to create new user")
                # If the user doesn't exist, create a new user and profile
                # We set the username to be the same as the public key for simplicity
                user = User(username=pubkey)
                user.save()
                print("new user saved")

            # Log the user in
            if user is not None:
                django_login(request, user)
                print("user logged in")
            else:
                print("Authentication failed because user is {}".format(user))
        else:
            print("FAILED to verify signed event")
    else:
        print("signed event not in request.POST")

    return request


def handle_logout(request):
    if request.user.is_authenticated:
        django_logout(request)
        print("User logged out")

    return request


def index(request):
    if request.method == 'POST':
        request = handle_login(request)
    elif request.method == 'GET' and request.GET.get('logout'):
        request = handle_logout(request)
    else:
        pass

    return render(request, 'testapp/index.html')