import aionostr
from django.shortcuts import render
from aionostr.event import Event
import json
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User
from .models import UserProfile
from asgiref.sync import sync_to_async


def verify_signed_event(signed_event):
    signed_event = Event(pubkey=signed_event["pubkey"], content=signed_event["content"],
                         kind=signed_event["kind"], created_at=signed_event["created_at"],
                         tags=signed_event["tags"], id=signed_event["id"], sig=signed_event["sig"])

    return signed_event.verify()


@sync_to_async
def get_user(pubkey):
    return User.objects.filter(username=pubkey).first()


@sync_to_async
def create_user(pubkey):
    user = User(username=pubkey)
    user.save()
    return user


@sync_to_async
def get_or_create_profile(user):
    return UserProfile.objects.get_or_create(user=user)[0]


@sync_to_async
def save_profile(profile):
    profile.save()


@sync_to_async
def get_profile(user):
    return UserProfile.objects.filter(user=user).first()


async def get_user_profile_data(pubkey):
    METADATA_KIND = 0 # this is for profile data for user
    default_relays = ['wss://purplepag.es', 'wss://relay.damus.io', 'wss://nos.lol', 'wss://relay.snort.social']
    query = {'authors':[pubkey], 'kinds': [METADATA_KIND]}
    profile_events = await aionostr.get_anything(query, relays=default_relays)
    print("result from aionostr.get() is {}".format(profile_events))
    if len(profile_events) > 0:
        latest_event = None
        latest_event_timestamp = 0
        for event in profile_events:
            event = event.to_json_object()
            timestamp = event['created_at']
            if timestamp > latest_event_timestamp:
                latest_event_timestamp = timestamp
                latest_event = event

        if latest_event is not None:
            # get the user obj from db
            user = await get_user(pubkey)
            # get or create a profile obj
            profile = await get_or_create_profile(user)
            # update the profile obj with the latest event
            latest_event_content = json.loads(latest_event['content'])
            if 'display_name' in latest_event_content:
                profile.display_name = latest_event_content['display_name']
            if 'lud16' in latest_event_content:
                profile.lud16 = latest_event_content['lud16']
            await save_profile(profile)

    return profile


async def handle_login(request):
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
            user = await get_user(pubkey)
            if user is None:
                print("user not found, about to create new user")
                # If the user doesn't exist, create a new user and profile
                # We set the username to be the same as the public key for simplicity
                user = await create_user(pubkey)
                print("new user saved")

            # Log the user in
            if user is not None:
                await sync_to_async(django_login)(request, user)
                print("user logged in")
                await get_user_profile_data(pubkey)
            else:
                print("Authentication failed because user is {}".format(user))
        else:
            print("FAILED to verify signed event")
    else:
        print("signed event not in request.POST")

    return request


async def handle_logout(request):
    if request.user.is_authenticated:
        await sync_to_async(django_logout)(request)
        print("User logged out")

    return request


async def index(request):
    context = {}
    if request.method == 'POST':
        request = await handle_login(request)
        # get the user's profile if they have one
        if request.user.is_authenticated:
            profile = await get_profile(request.user)
            if profile is not None:
                context['profile'] = profile
    elif request.method == 'GET' and request.GET.get('logout'):
        request = await handle_logout(request)
    else:
        pass

    return render(request,  'testapp/index.html', context)
