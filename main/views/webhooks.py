import datetime

from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from ..models import Message
from ..utils import construct_reply

import tbvaccine
tbvaccine.add_hook()


@csrf_exempt
def forwarded(request):
    "The webhook that fires when a user forwards a legitimate email."

    # Parse the forwarded message.
    message = Message.parse_from_mailgun(request.POST, forwarded=True)

    # Notify the sender that we've received it.
    EmailMessage(
        subject=render_to_string(
            "emails/forward_received_subject.txt",
            request=request
        ).strip(),
        body=render_to_string(
            "emails/forward_received_body.txt",
            context={"message": message},
            request=request
        ),
        to=[message.conversation.reporter_email],
    ).send()

    # Reply to the spammer.
    reply = construct_reply(message)
    reply.send()

    return HttpResponse("OK")


@csrf_exempt
def email(request):
    "The webhook that fires when we get some spam."

    # Parse the received message.
    message = Message.parse_from_mailgun(request.POST)

    # Reply to the spammer.
    reply = construct_reply(message)
    reply.queue()

    return HttpResponse("OK")


@csrf_exempt
def cron(request):
    "The webhook that is called when it's time to send emails."
    unsent_messages = Message.objects.exclude(send_on=None).filter(send_on__lt=datetime.datetime.now())
    for message in unsent_messages:
        message.send()

    return HttpResponse("OK")
