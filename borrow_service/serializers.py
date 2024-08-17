from rest_framework import serializers

from book_service.serializers import BookSerializer
from borrow_service.models import Borrow


class BorrowListSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title")

    class Meta:
        model = Borrow
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_title",
            "user"
        )


class BorrowRetrieveSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Borrow
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user"
        )


class BorrowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = ("book", "expected_return_date")

    def create(self, validated_data):
        return Borrow.objects.create(**validated_data)
