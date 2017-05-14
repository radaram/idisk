from unittest import mock

import pytest

from idisk import (Printer, LinuxInfoOfDisks, WindowsInfoOfDisks,
                   display, get_info_of_disks_class)


def test_bytes_to_str():
    printer = Printer(mock.Mock(), mock.Mock())
    assert printer.bytes_to_str(1024, 'B') == '1024.0B'
    assert printer.bytes_to_str(1024 ** 2, 'M') == '1.0M'
    assert printer.bytes_to_str(1024 ** 3, 'G') == '1.0G'


@mock.patch('idisk.Printer.show_info_logical_disks')
@mock.patch('idisk.Printer.show_info_physical_disks')
def test_display(mock_physical_disks, mock_logical_disks):
    display(mock.Mock())
    assert mock_physical_disks.called

    display(mock.Mock(), 1)
    mock_logical_disks.assert_called_with(1)


@mock.patch('sys.platform', 'linux')
def test_get_info_of_disks_class_linux():
    cls = get_info_of_disks_class()
    assert issubclass(cls, LinuxInfoOfDisks)


@mock.patch('sys.platform', 'win32')
def test_get_info_of_disks_class_win():
    cls = get_info_of_disks_class()
    assert issubclass(cls, WindowsInfoOfDisks)


@mock.patch('sys.platform', 'osx')
def test_get_info_of_disks_class_other():
    with pytest.raises(Exception):
        get_info_of_disks_class()
