from django.forms import widgets


class NumberInput(widgets.TextInput):
    input_type = 'number'
