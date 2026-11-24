from rest_framework import serializers

from accounts.validation import (
    DEPARTMENTS,
    DESIGNATION_ERROR,
    EMAIL_ERROR,
    EMAIL_PATTERN,
    NAME_ERROR,
    NAME_PATTERN,
)


class RegisterSerializer(serializers.Serializer):
    full_name = serializers.RegexField(NAME_PATTERN, max_length=120, error_messages={"invalid": NAME_ERROR})
    email = serializers.RegexField(EMAIL_PATTERN, max_length=254, error_messages={"invalid": EMAIL_ERROR})
    department = serializers.ChoiceField(choices=list(DEPARTMENTS))
    designation = serializers.CharField(max_length=120)
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)

    def validate(self, data):
        if data["designation"] not in DEPARTMENTS[data["department"]]:
            raise serializers.ValidationError({"designation": DESIGNATION_ERROR})
        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(max_length=128, write_only=True)
