from django.http import HttpResponse

from myapp import format_version


def home(request):
    return HttpResponse("Hello, World!")


def version(request, label='version'):
    return HttpResponse(format_version(label))
