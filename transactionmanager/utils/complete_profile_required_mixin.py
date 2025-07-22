from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class CompleteProfileRequiredMixin:
    """
    User must have completed their profile (first name and last name)
    before accessing certain views. If not, redirect to the profile completion page.
    This mixin can be used in views that require a complete user profile.   
    """

    redirect_url = "complete_profile"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.first_name or not request.user.last_name:
                messages.warning(request, "Per favore completa il tuo profilo con nome e cognome.")
                return redirect(reverse(self.redirect_url))
        return super().dispatch(request, *args, **kwargs)
