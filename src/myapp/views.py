from django.urls import reverse_lazy as django_reverse_lazy
from django.db import transaction
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, DetailView, UpdateView, \
    DeleteView

from rest_framework import viewsets, permissions, mixins
from rest_framework.request import Request

from log_utils import LogMixin
from myapp import format_version
from .models import Greeting
from .serializers import GreetingSerializer
from .forms import GreetingForm


class GreetingViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):

    queryset = Greeting.objects.all()
    serializer_class = GreetingSerializer
    permission_classes = (permissions.IsAuthenticated,)


class LoggedGreetingViewSet(LogMixin, GreetingViewSet):
    # log any creation
    def perform_create(self, serializer):
        super(LoggedGreetingViewSet, self).perform_create(serializer)
        self.logger.info("A new greeting as been created")


class MockGreetingViewSet(GreetingViewSet):
    queryset = Greeting.mock_objects.all()

    def dispatch(self, request, *args, **kwargs):
        """
        Don't dispatch the call if the url has the "fake" arg
        """
        query_string = Request(request).query_params
        fake_code = query_string.get('fake')

        if fake_code:
            fake_code = int(fake_code)
            return HttpResponse(status=fake_code)
        else:
            # NB: the 'mock' db is configured with ATOMIC_REQUESTS = True
            sid = transaction.savepoint(using='mock')
            response = super(MockGreetingViewSet, self).dispatch(request, *args, **kwargs)
            transaction.savepoint_rollback(sid, using='mock')
            return response


class GreetingList(LogMixin, ListView):
    model = Greeting
    paginate_by = 20

    def get(self, *args, **kwargs):
        to_return = super(GreetingList, self).get(*args, **kwargs)
        self.logger.info("Get a list of greetings")
        return to_return


class GreetingCreate(CreateView):
    model = Greeting
    form_class = GreetingForm
    success_url = django_reverse_lazy('crud:greeting-list')


class GreetingDetail(DetailView):
    model = Greeting


class GreetingUpdate(UpdateView):
    model = Greeting
    form_class = GreetingForm
    success_url = django_reverse_lazy('crud:greeting-list')


class GreetingDelete(DeleteView):
    model = Greeting
    success_url = django_reverse_lazy('crud:greeting-list')


def version(request, label='version'):
    return HttpResponse(format_version(label))
