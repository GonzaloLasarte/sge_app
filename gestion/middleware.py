from django.urls import reverse
from django.http import HttpResponseRedirect


class ExpiredUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        try:
            if not request.user.has_not_expired:
                request.expired_user = True
                return HttpResponseRedirect(reverse('gestion:logout_view', kwargs={'expired_user': True}))
            else:
                request.expired_user = False
        except AttributeError:
            pass

        response = self.get_response(request)
        return response
