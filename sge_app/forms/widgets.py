import json

from django.forms.widgets import (
    ClearableFileInput, Input, NumberInput, Select, Textarea,
    DateInput, URLInput, PasswordInput, EmailInput, HiddenInput)
from django.utils.translation import gettext_lazy


class UserClearableFileInput(ClearableFileInput):
    """Custom clearable file input class."""

    input_text = gettext_lazy('Choose File')
    template_name = 'admin_customer/bootstrap/user_clearable_file_input.html'


class UserClearableImageInput(UserClearableFileInput):
    """Custom clearable image input class."""

    input_text = gettext_lazy('Choose Image')
    template_name = 'admin_customer/bootstrap/user_clearable_image_input.html'


def merge_html_attrs(old_value, new_value):
    """Merge two values of a HTML attribute into a single value."""
    attr_value = old_value.split(" ")
    attr_value += new_value.split(" ")
    return " ".join(filter(None, attr_value))


def update_widget_context_attr(context, attr, value):
    """Update attributes in a widget's context."""
    context['widget']['attrs'][attr] = merge_html_attrs(
        context['widget']['attrs'].get(attr, ''),
        value
    )
    return context


class FormControlMixin(object):
    """Generic mixin for bootstrap-based widgets."""

    bs_classes = 'form-control'

    def get_context(self, name, value, attrs):
        """Add bootstrap classes to the default context."""
        context = super(FormControlMixin, self).get_context(name, value, attrs)
        return update_widget_context_attr(context, 'class', self.bs_classes)


class BootstrapTextInput(FormControlMixin, Input):
    """Bootstrap-based Input."""

    input_type = 'text'


class BootstrapNumberInput(FormControlMixin, NumberInput):
    """Bootstrap-based NumberInput."""

    pass


class BootstrapURLInput(FormControlMixin, URLInput):
    """Bootstrap-based URLInput."""

    pass


class BootstrapEmailInput(FormControlMixin, EmailInput):
    """Bootstrap-based EmailInput."""

    pass


class BootstrapPasswordInput(FormControlMixin, PasswordInput):
    """Bootstrap-based PasswordInput."""

    pass


class BootstrapDateInput(FormControlMixin, DateInput):
    """Bootstrap-based DateInput."""

    pass


class BootstrapSelect(FormControlMixin, Select):
    """A basic <select> widget with added class attrs."""

    bs_classes = "{} c-select".format(FormControlMixin.bs_classes)


class BootstrapTextarea(FormControlMixin, Textarea):
    """A basic <textarea> widget with added class attrs."""

    pass
