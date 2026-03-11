from rest_framework import serializers
from core.models import Testing, Transaction

class TestingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testing
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'title', 'amount', 'transaction_type', 'category', 'date', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be blank.")
        return value

    def validate(self, data):
        if data.get('transaction_type') == 'income' and not data.get('category'):
            raise serializers.ValidationError({"category": "Category is required for income transactions."})
        return data