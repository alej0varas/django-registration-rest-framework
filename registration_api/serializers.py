from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()

    def to_native(self, obj):
        """Remove password field when serializing an object"""
        ret = super(UserSerializer, self).to_native(obj)
        del ret['password']
        return ret
