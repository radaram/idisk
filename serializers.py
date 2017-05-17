import csv
import io
import json
from collections import OrderedDict
from exceptions import ValidateError


class Field(object):
    __field_type = None

    def __init__(self, value=None):
        self.__value = value

    def __get__(self, instance, owner):
        return self.__value

    def __set__(self, instance, value):
        if not isinstance(value, self.field_type):
            try:
                self.__value = self.field_type(value)
            except TypeError:
                raise
        else:
            self.__value = value

    @property
    def field_type(self):
        if not self.__field_type:
            raise ValidateError('Field type is not specified!')
        return self.__field_type

    @field_type.setter
    def field_type(self, value):
        self.__field_type = value


class CharField(Field):
    field_type = str


class IntegerField(Field):
    field_type = int


class Disk(OrderedDict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError


class Serializer(object):

    def __init__(self, data):
        self.raw_data = data

    def to_representation(self, data):
        if not isinstance(data, dict):
            raise ValidateError('Not a valid data type!')
        res = Disk()
        for field_name, value in data.items():
            field_name = field_name.lower()
            if not hasattr(self, field_name):
                raise ValidateError(
                    'Does not exist field {}!'.format(field_name)
                )
            setattr(self, field_name, value)
            res[field_name] = getattr(self, field_name)
        return res

    @property
    def data(self):
        if not hasattr(self, '__data'):
            self.__data = self.to_representation(self.raw_data)
        return self.__data


class ListSerializer(Serializer):
    child = None

    def to_representation(self, data):
        if not isinstance(data, (list, tuple)):
            raise ValidateError('Not a valid data type!')

        return [
            self.child(item).data for item in data
        ]

    def __str__(self):
        pass

    def __repr__(self):
        return self


class DiskSerializer(Serializer):
    name = CharField()
    size = IntegerField()


class LinuxPhysicalListDiskSerializer(ListSerializer):
    child = DiskSerializer

    def to_representation(self, data):
        devices = json.loads(data)['blockdevices']
        return super().to_representation(devices)


class LinuxLogicalDiskDiskSerializer(ListSerializer):
    child = DiskSerializer


class LinuxLogicalDiskListSerializer(ListSerializer):
    child = LinuxLogicalDiskDiskSerializer

    def to_representation(self, data):
        devices = json.loads(data)['blockdevices']
        if not isinstance(devices, (list, tuple)):
            raise ValidateError('Not a valid data type!')

        return [
            self.child(item['children']).data for item in devices
        ]


class WindowsPhysicalListDiskSerializer(ListSerializer):
    child = DiskSerializer

    def to_representation(self, data):
        with io.StringIO(data) as f:
            devices = list(csv.DictReader(f))
        for device in devices:
            if 'Node' in device:
                del device['Node']
        return super().to_representation(devices)


class WindowsDiskSerializer(DiskSerializer):
    diskindex = IntegerField()


class WindowsLogicalDiskListSerializer(WindowsPhysicalListDiskSerializer):
    child = WindowsDiskSerializer