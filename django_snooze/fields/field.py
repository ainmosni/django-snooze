# -*- coding: utf-8 -*-
"""
These are all adaptors for Django fields, not overly documented as that would
just be duplicating Django's excellent documentation.
"""

from collections import OrderedDict


class Field(object):
    """
    Generic field object.

    This will the parent object of all specific field subclasses
    """

    def __init__(self, field):
        """
        This processes a field and extract all needed information from it.

        Arguments:
            - field (required): The field to process.
        """
        self.field = field
        self.name = field.name
        self.null = field.null
        self.blank = field.blank
        self.validators = field.validators
        self.editable = field.editable
        self.help_text = field.help_text
        self.primary_key = field.primary_key
        self.unique = field.unique
        self.default = field.default
        self.model = field.model

    def schema_info(self):
        """Returns the field metadata in a dictionary.
        This is to fill in the schema resource.

        :returns: An OrderedDict with metadata.

        """
        schema = OrderedDict()
        schema['name'] = self.name
        schema['null'] = self.null
        schema['blank'] = self.blank
        schema['editable'] = self.editable
        schema['help_text'] = self.help_text
        schema['primary_key'] = self.primary_key
        schema['unique'] = self.unique
        schema['default'] = str(self.default)
        return schema

    def to_json(self, field_value):
        """Convert the value of the field to its serialisable value.
        As this is the base class it does a very naive coercion to string, this
        is often not what you want.

        :param field_value: The value of the field of the matching type.
        :returns: Serialisable object representing field_value.

        """
        return str(field_value)


# Integer fields
class IntegerField(Field):
    """
    An integer field.
    """

    def to_json(self, field_value):
        """Convert the value to an integer.

        :param field_value: The field of the integer value.
        :returns: An integer.

        """
        return int(field_value)


class PositiveIntegerField(IntegerField):
    """
    A positive integer field.
    """
    pass


class PositiveSmallIntegerField(IntegerField):
    """
    A positive small integer field.
    """
    pass


class BigIntegerField(IntegerField):
    """
    A big integer field.
    """
    pass


class AutoField(IntegerField):
    """
    An automatically incrementing integer field.
    """
    pass


# Other number fields
class DecimalField(Field):
    """
    A decimal number field.
    """

    def __init__(self, field):
        """
        This process a DecimalField and extract all needed information from it.
        The only extra functionality here is that max_digits and decimal_places
        are taken into consideration.

        Arguments:
            - field (required): The field to process.
        """
        self.max_digits = field.max_digitgs
        self.decimal_places = field.decimal_places
        super(DecimalField, self).__init__(field)

    def to_json(self, field_value):
        """Convert the field value to a float.

        :param field_value: The value of the DecimalField
        :returns: A float.

        """
        return float(field_value)


class FloatField(Field):
    """
    A floating point field.
    """

    def to_json(self, field_value):
        """Convert field value to float.

        :param field_value: The value of the FloatField.
        :returns: A float.

        """
        return float(field_value)


# Boolean fields
class BooleanField(Field):
    """
    A boolean field.
    """

    def to_json(self, field_value):
        """Convert field value to bool.

        :param field_value: The value of the BooleanField
        :returns: A bool.

        """
        return bool(field_value)


class NullBooleanField(BooleanField):
    """
    A boolean field with a NULL option.
    """

    def to_json(self, field_value):
        """Convert field value to bool or None.

        :param field_value: The value of the NullBooleanField
        :returns: A bool if defined, else None.

        """
        return bool(field_value) if field_value else None


# Character/Text fields
class CharField(Field):
    """
    A character field.
    """

    def __init__(self, field):
        """
        This process a CharField and extract all needed information from it.
        The only extra functionality here is that the max_length is taken into
        consideration.

        Arguments:
            - field (required): The field to process.
        """
        self.max_length = field.max_length
        super(CharField, self).__init__(field)


class SlugField(CharField):
    """
    A slug field.
    """
    pass


class CommaSeperatedIntegerField(CharField):
    """
    A character field with comma seperated ints.
    """
    pass


class EmailField(CharField):
    """
    A character field with e-mail validation.
    """
    pass


class URLField(CharField):
    """
    A CharField with URL features.
    """
    pass


class TextField(Field):
    """
    A text field.
    """
    pass


# File fields
class FileField(CharField):
    """
    A file upload field.
    """
    pass


class FilePathField(CharField):
    """
    A file path field.
    """

    def __init__(self, field):
        """
        This process a CharField and extract all needed information from it.
        The only extra functionality here is that the max_length is taken into
        consideration.

        Arguments:
            - field (required): The field to process.
        """
        self.match = field.match
        self.recursive = field.recursive


class ImageField(FileField):
    """
    An image upload field.
    """
    pass


# Date and DateTime fields
class DateField(Field):
    """
    A date field.
    """

    def __init__(self, field):
        """
        This process a DateField and extract all needed information from it.
        The only extra functionality here is that the auto_now and auto_now_add
        are taken into consideration.

        Arguments:
            - field (required): The field to process.
        """
        self.auto_now = field.auto_now
        self.auto_now_add = field.auto_now_add
        super(DateField, self).__init__(field)


class DateTimeField(DateField):
    """
    A date time field.
    """
    pass


class TimeField(DateField):
    """
    A time field.
    """
    pass


# IP address fields
class IPAddressField(Field):
    """
    An IPv4 address field.
    """
    pass


class GenericIPAddressField(Field):
    """
    A generic IP address field with v4 and v6 support.
    """

    def __init__(self, field):
        """
        This processes a GenericIPAddressField and extract all needed
        information from it.  The only extra functionality here is that
        protocol and unpack_ipv4 are taken into consideration.

        Arguments:
            - field (required): The field to process.
        """
        self.protocol = field.protocol
        self.unpack_ipv4 = field.unpack_ipv4
        super(GenericIPAddressField, self).__init__(field)


# Relationship fields.
class ForeignKey(Field):
    """
    A Foreign Key field.
    """

    def __init__(self, field):
        """This processes foreign key fields.

        :param field: The foreign key field to process.
        :returns: A ForeignKey object

        """
        self.related_model = field.related.parent_model
        self.related_name = field.related.get_accessor_name()
        self.to_fields = field.to_fields
        super(ForeignKey, self).__init__(field)

    def schema_info(self):
        """Adds foreign key specific data to the schema.

        :returns: A dictionary with schema metadata.

        """
        schema = super(ForeignKey, self).schema_info()
        schema.update({
            'related_model': self.related_model.__name__,
            'related_name': self.related_name,
            'to_fields': self.to_fields
        })
        return schema


class ManyToManyField(ForeignKey):
    """
    A many to many field.
    """
    pass


# Misc fields
class BinaryField(Field):
    """
    A binary field.
    """
    pass
