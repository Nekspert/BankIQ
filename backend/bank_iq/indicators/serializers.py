from rest_framework import serializers


class BankInfoSerializer(serializers.Serializer):
    bic = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    reg_number = serializers.CharField(required=True)
    internal_code = serializers.CharField(required=True)
    registration_date = serializers.DateTimeField(required=True)
    region_code = serializers.CharField(required=True)
    tax_id = serializers.CharField(required=True)


class AllBanksSerializer(serializers.Serializer):
    banks = BankInfoSerializer(many=True)
