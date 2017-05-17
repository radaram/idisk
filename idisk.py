import argparse
import sys
import subprocess

from abc import ABCMeta, abstractmethod

from exceptions import (
    MeasureException, PlatformSupportException
)

from serializers import (
    LinuxPhysicalListDiskSerializer, LinuxLogicalDiskListSerializer,
    WindowsPhysicalListDiskSerializer, WindowsLogicalDiskListSerializer
)


class InfoOfDisks(metaclass=ABCMeta):

    @abstractmethod
    def physical_disks(self):
        pass

    @abstractmethod
    def logical_disks(self, device_number):
        pass

    def run_command(self, command, encoding):
        return subprocess.run(
            command, stdout=subprocess.PIPE, encoding=encoding
        )


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
        sys.stdout.write('{:<20} {:>20} {:>20}\n'.format('Device', 'Size', 'Number'))
        for number, disk in enumerate(self.info_of_disks.physical_disks()):
            sys.stdout.write('{:<20} {:>20} {:>20}\n'.format(
                disk.name, self.bytes_to_str(disk.size, self.measure), number + 1
            ))

    def show_info_logical_disks(self, device_number):
        sys.stdout.write('{:<20} {:>20}\n'.format('Device', 'Total'))
        for disk in self.info_of_disks.logical_disks(device_number):
            sys.stdout.write('{:<20} {:>20}\n'.format(
                disk.name, self.bytes_to_str(disk.size, self.measure)
            ))

    def bytes_to_str(self, bytes, measure='M'):
        if measure not in self.SIZES:
            raise MeasureException(
                'Conversion in format {} is not possible!'.format(measure)
            )
        number = round(bytes / self.SIZES[measure], 1)
        return '{}{}'.format(number, measure)


class LinuxInfoOfDisks(InfoOfDisks):
    # http://man7.org/linux/man-pages/man8/lsblk.8.html
    command = ['lsblk', '-b', '-J', '-o', 'NAME,SIZE,TYPE']

    def physical_disks(self):
        self.command.append('-d')
        result = self.run_command(self.command, 'utf-8')
        return LinuxPhysicalListDiskSerializer(result.stdout.strip()).data

    def logical_disks(self, device_number):
        result = self.run_command(self.command, 'utf-8')
        devices = LinuxLogicalDiskListSerializer(result.stdout.strip()).data
        device_number -= 1
        if device_number < 0 or device_number >= len(devices):
            return []
        return devices[device_number]


class WindowsInfoOfDisks(InfoOfDisks):
    command_for_physical = ['wmic', 'diskdrive', 'get', 'Name,Size', '/translate:nocomma', '/format:csv']
    command_for_logical = ['wmic', 'partition', 'get', 'DiskIndex,Name,Size', '/translate:nocomma', '/format:csv']

    def physical_disks(self):
        result = self.run_command(self.command_for_physical, 'cp866')
        return WindowsPhysicalListDiskSerializer(result.stdout.strip()).data

    def logical_disks(self, device_number):
        result = self.run_command(self.command_for_logical, 'cp866')
        devices = WindowsLogicalDiskListSerializer(result.stdout.strip()).data
        device_number -= 1
        return filter(lambda device: device.diskindex == device_number, devices)


def get_info_of_disks_class():
    if sys.platform == 'linux':
        return LinuxInfoOfDisks
    elif sys.platform == 'win32':
        return WindowsInfoOfDisks
    raise PlatformSupportException(
        '{} platform is not supported'.format(sys.platform)
    )


def display(measure, device_number=None):
    printer = Printer(get_info_of_disks_class(), measure=measure)
    if isinstance(device_number, int):
        printer.show_info_logical_disks(device_number)
    else:
        printer.show_info_physical_disks()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', default='G', type=str,
                        help='unit of measurement', required=False)
    parser.add_argument('d', type=int, nargs='?',
                        help='device number')
    args = parser.parse_args()

    display(args.u, args.d)
