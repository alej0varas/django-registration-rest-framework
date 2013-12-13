from django.contrib.auth import get_user_model


def get_valid_user_fields():
    fields = []
    for f in get_user_model()._meta.fields:
        fields.append(f.name)
    return fields


VALID_USER_FIELDS = get_valid_user_fields()


def get_user_data(data):
    user_data = {}
    for field, data in data.items():
        if field in VALID_USER_FIELDS:
            user_data.update({field: data})
    return user_data
