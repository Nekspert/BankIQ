from abc import ABCMeta

from rest_framework import serializers


class CombinedMeta(serializers.SerializerMetaclass, ABCMeta):
    ...
