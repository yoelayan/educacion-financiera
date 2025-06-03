from django.shortcuts import render, redirect
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """
    Home view that renders different templates based on authentication status.
    - Authenticated users are redirected to the dashboard
    - Unauthenticated users see the landing page (landing.html)
    """

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        return super().get(request, *args, **kwargs)

    def get_template_names(self):
        return ["pages/landing.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Landing page context for unauthenticated users
        context.update({
            'page_type': 'landing',
            'show_sidebar': False,
            'show_search': False,
        })

        return context
