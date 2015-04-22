from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, TemplateView

from django.core.exceptions import PermissionDenied
from django.apps import apps
from . import uwsgi


class UwsgiStatus(TemplateView):

    """uWSGI Status View"""

    if apps.is_installed('wagtail.wagtailadmin'):
        template_name = 'uwsgi/wagtail_uwsgi.html'
    else:
        template_name = 'uwsgi/uwsgi.html'

    def get_context_data(self, **kwargs):
        context = super(UwsgiStatus, self).get_context_data(**kwargs)
        if uwsgi is None:
            context['unavailable'] = True
            return context
        else:
            from .stats import get_uwsgi_stats
            context.update(get_uwsgi_stats())
            return context


class UwsgiCacheClear(View):

    """Clear uWSGI Cache View"""

    def get(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied
        if uwsgi is not None and uwsgi.masterpid() > 0:
            uwsgi.cache_clear()
            messages.add_message(request, messages.SUCCESS, _(
                'uWSGI Cache cleared!'), fail_silently=True)
        else:
            messages.add_message(request, messages.ERROR, _(
                'The uWSGI master process is not active'), fail_silently=True)
        return HttpResponseRedirect(reverse_lazy('uwsgi_index'))


class UwsgiReload(View):

    """Reload uWSGI View"""

    def get(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied
        if uwsgi is not None and uwsgi.masterpid() > 0:
            uwsgi.reload()
            messages.add_message(
                request, messages.SUCCESS, _('uWSGI reloaded!'), fail_silently=True)
        else:
            messages.add_message(request, messages.ERROR, _(
                'The uWSGI master process is not active'), fail_silently=True)
        return HttpResponseRedirect(reverse_lazy('uwsgi_index'))
