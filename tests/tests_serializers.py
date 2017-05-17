import json

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
            {"name": "sda", "size": "1000204886016", "type": "disk"},
            {"name": "sdb", "size": "16013942784", "type": "disk"},
            {"name": "sr0", "size": "1048576", "type": "rom"}
        ]
    })


@pytest.fixture
def logical_disks():
    return json.dumps({
        "blockdevices": [
            {"name": "sda", "size": "1000203837440", "type": "disk",
             "children": [
                 {"name": "sda1", "size": "1000204886016", "type": "part"}
             ]},
            {"name": "sdb", "size": "16012894208", "type": "disk",
             "children": [
                 {"name": "sdb1", "size": "16013942784", "type": "part"}
             ]},
            {"name": "sr0", "size": "1048576", "type": "rom"}
        ]
    })


def test_serizliser(disk):
    ds = DiskSerializer(disk).data
    assert ds.name == 'sdb'
    assert isinstance(ds.size, int)
    assert ds.size == 16013942784


def test_list_serizliser(disks):
    data = LinuxPhysicalListDiskSerializer(disks).data
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0].name == 'sda'
    assert data[1].name == 'sdb'


def test_logical_disks_serizliser(logical_disks):
    data = LinuxLogicalDiskListSerializer(logical_disks).data
    assert isinstance(data, list)
    assert len(data) == 2
    assert isinstance(data[0], list)
    assert isinstance(data[1], list)
    assert data[0][0].name == 'sda1'
    assert data[1][0].name == 'sdb1'
