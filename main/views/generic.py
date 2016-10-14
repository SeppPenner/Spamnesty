from annoying.decorators import render_to
from django.db.models import Max, Count
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.crypto import constant_time_compare

from ..models import Conversation


@render_to("home.html")
def home(request):
    if not (request.get_host().startswith("spa.") or settings.DEBUG):
        return {"TEMPLATE": "fake.html"}
    conversations = Conversation.objects.annotate(
            last_message_time=Max('message__timestamp'),
            num_messages=Count("message"),
        ).filter(num_messages__gt=2).order_by('-last_message_time')
    return {"conversations": conversations}


@render_to("conversation_view.html")
def conversation_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, pk=conversation_id)
    own_conversation = constant_time_compare(request.GET.get("key"), conversation.secret_key)
    return {"conversation": conversation, "own": own_conversation}
