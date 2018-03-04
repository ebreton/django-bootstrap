from rest_framework import serializers

from myapp.models import Greeting


class GreetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Greeting
        fields = ('id', 'name',)
