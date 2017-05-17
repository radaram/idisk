import json

from unittest import mock

import pytest

from serializers import (
    DiskSerializer, LinuxPhysicalListDiskSerializer,
    LinuxLogicalDiskListSerializer
)


@pytest.fixture
def disk():
    return {"name": "sdb", "size": "16013942784"}


@pytest.fixture
def disks():
    return json.dumps({
        "blockdevices": [
            {"name": "sda", "size": "1000204886016"},
            {"name": "sdb", "size": "16013942784"}
        ]
    })


@pytest.fixture
def logical_disks():
    return json.dumps({
        "blockdevices": [
            {"name": "sda1", "size": "1000203837440",
             "children": [
                 {"name": "sda", "size": "1000204886016"}
             ]},
            {"name": "sdb1", "size": "16012894208",
             "children": [
                 {"name": "sdb", "size": "16013942784"}
             ]}
        ]
    })


def test_serizliser(disk):
    ds = DiskSerializer(disk)
    _ = ds.data
    assert ds.name == 'sdb'
    assert isinstance(ds.size, int)
    assert ds.size == 16013942784


def test_list_serizliser(disks):
    ds = LinuxPhysicalListDiskSerializer(disks)
    assert isinstance(ds.data, list)
    assert len(ds.data) == 2


def test_logical_disks_serizliser(logical_disks):
    ds = LinuxLogicalDiskListSerializer(logical_disks)
    assert isinstance(ds.data, list)
    assert len(ds.data) == 2
    assert isinstance(ds.data[0], list)