import argparse
import sys

from abc import ABCMeta, abstractmethod
from collections import OrderedDict

import psutil

if sys.platform == 'linux':
    import pyudev
elif sys.platform == 'win32':
    import wmi
else:
    raise Exception('The platform is not supported')


class InfoOfDisks(metaclass=ABCMeta):

    @abstractmethod
    def physical_disks(self):
        pass

    @abstractmethod
    def logical_disks(self, device_number):
        pass

    @property
    def partitions(self):
        return psutil.disk_partitions()

    def get_size(self, path):
        return psutil.disk_usage(path).total


class MeasureException(Exception):
    pass


class Printer(object):
    _info_of_disks = None

    SIZES = {
        'B': 1, 'K': 1024, 'M': 1024 ** 2, 'G': 1024 ** 3, 'T': 1024 ** 4
    }

    def __init__(self, info_of_disks_class,  measure):
        self.measure = measure
        self._info_of_disks = info_of_disks_class

    @property
    def info_of_disks(self):
        if not self._info_of_disks:
            raise NotImplementedError
        return self._info_of_disks()

    def show_info_physical_disks(self):
        sys.stdout.write('{:<10} {:>10}\n'.format('Device', 'Size'))
        for disk, size in self.info_of_disks.physical_disks():
            sys.stdout.write('{:<10} {:>10}\n'.format(
                disk, self.bytes_to_str(size, self.measure)
            ))

    def show_info_logical_disks(self, device_number):
        sys.stdout.write('{:<10} {:>10}\n'.format('Device', 'Total'))
        for disk, size in self.info_of_disks.logical_disks(device_number):
            sys.stdout.write('{:<10} {:>10}\n'.format(
                disk, self.bytes_to_str(size, self.measure)
            ))

    def bytes_to_str(self, bytes, measure='M'):
        if measure not in self.SIZES:
            raise MeasureException(
                'Conversion in format {} is not possible!'.format(measure)
            )
        number = round(bytes / self.SIZES[measure], 1)
        return '{}{}'.format(number, measure)


class DiskExistsException(Exception):
    pass


class LinuxInfoOfDisks(InfoOfDisks):
    def physical_disks(self):
        devices = self._get_devices()
        for parent, children in devices.items():
            buf = []
            bytes = 0
            for partition in self.partitions:
                if partition.device in children and partition.device not in buf:
                    buf.append(partition.device)
                    bytes += self.get_size(partition.mountpoint)
            yield parent, bytes

    def logical_disks(self, device_number):
        device_number -= 1
        devices = list(self._get_devices().values())
        if device_number < 0 or device_number >= len(devices):
            raise DiskExistsException(
                'Disk {} does not exist!'.format(device_number)
            )
        children = devices[device_number]

        buf = []
        for partition in self.partitions:
            if partition.device in children and partition.device not in buf:
                buf.append(partition.device)
                yield partition.device, self.get_size(partition.mountpoint)

    def _get_devices(self):
        disks = OrderedDict()
        context = pyudev.Context()
        for device in context.list_devices(subsystem='block', DEVTYPE='partition'):
            if device.parent.device_node not in disks:
                disks[device.parent.device_node] = [device.device_node]
            else:
                disks[device.parent.device_node].append(device.device_node)
        return disks


class WindowsInfoOfDisks(LinuxInfoOfDisks):
    @property
    def partitions(self):
        return filter(lambda device: device.opts != 'cdrom', psutil.disk_partitions())

    def _get_devices(self):
        disks = OrderedDict()
        for device in wmi.WMI().Win32_DiskDrive():
            for partition in device.associators("Win32_DiskDriveToDiskPartition"):
                for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                    if device.Caption not in disks:
                        disks[device.Caption] = [logical_disk.Caption + '\\']
                    else:
                        disks[device.Caption].append(logical_disk.Caption + '\\')
        return disks


def get_info_of_disks_class():
    if sys.platform == 'linux':
        return LinuxInfoOfDisks
    elif sys.platform == 'win32':
        return WindowsInfoOfDisks
    raise Exception('The platform is not supported')


def display(measure, device_number=None):
    printer = Printer(get_info_of_disks_class(), measure=measure)
    if device_number:
        printer.show_info_logical_disks(device_number)
    else:
        printer.show_info_physical_disks()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', default='G', type=str,
                        help='unit of measurement', required=False)
    parser.add_argument('-d', type=int,
                        help='device number', required=False)
    args = parser.parse_args()

    display(args.u, args.d)
