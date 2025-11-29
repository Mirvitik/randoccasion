__all__ = ()

from django.db.models import Q

from events.models import Event


def q_search(query):
    if query.isdigit():
        return Event.objects.filter(id=query)

    keywords = [word for word in query.split() if word]

    q_objects = Q()

    for token in keywords:
        q_objects |= Q(description__icontains=token)
        q_objects |= Q(name__icontains=token)
        q_objects |= Q(location__icontains=token)
        q_objects |= Q(topic__icontains=token)
        q_objects |= Q(creator__username__icontains=token)

    return Event.objects.filter(q_objects)
