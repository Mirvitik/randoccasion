__all__ = ()

from django.db.models import Q

from users.models import User


def q_search(query):
    if query.isdigit():
        return User.objects.filter(id=query)

    if "@" in query:
        user = User.objects.by_mail(query)
        if user:
            return User.objects.filter(id=user.id)
        
        return User.objects.none()
    
    keywords = [word for word in query.split() if word]

    q_objects = Q()

    for token in keywords:
        q_objects |= Q(username__icontains=token)
        q_objects |= Q(first_name__icontains=token)
        q_objects |= Q(last_name__icontains=token)
        q_objects |= Q(email__icontains=token)
        q_objects |= Q(profile__interests__name__icontains=token)

    return User.objects.filter(q_objects)