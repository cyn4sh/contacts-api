from rest_framework import serializers

from contacts.models import Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ["id", "owner", "name", "phone", "email", "address", "notes", "created_at", "updated_at"]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]