from datetime import date

from rest_framework import serializers

from transitions.services import PROGRESS_STATES


class KitCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=160)
    handover_date = serializers.DateField()
    successor_id = serializers.CharField(max_length=64)
    raw_notes = serializers.CharField(max_length=20000, allow_blank=True, required=False, default="")
    items = serializers.ListField(child=serializers.DictField(), required=False, default=list)

    def validate_handover_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Handover date cannot be in the past.")
        return value


class KitUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=160, required=False)
    handover_date = serializers.DateField(required=False)
    items = serializers.ListField(child=serializers.DictField(), required=False)


class PlaybookGenerateSerializer(serializers.Serializer):
    role_title = serializers.CharField(max_length=160)
    raw_notes = serializers.CharField(min_length=20, max_length=20000)


class ProgressSerializer(serializers.Serializer):
    progress = serializers.ChoiceField(choices=PROGRESS_STATES)


class ThreadMessageSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=1000)
