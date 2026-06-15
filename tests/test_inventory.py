"""Tests for the dependency-free PE inventory tool."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = (
    REPOSITORY_ROOT / "tools" / "symbol-manifest" / "inventory.py"
)
SPEC = importlib.util.spec_from_file_location(
    "symbol_manifest_inventory", INVENTORY_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load inventory tool from {INVENTORY_PATH}")
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)


def synthetic_pe(machine: int = inventory.AMD64_MACHINE) -> bytes:
    """Build the smallest PE image needed by the parser tests."""
    pe_offset = 0x80
    optional_header_size = 120
    section_table_offset = pe_offset + 4 + 20 + optional_header_size
    data = bytearray(section_table_offset + 40)

    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, pe_offset)
    data[pe_offset : pe_offset + 4] = b"PE\0\0"
    struct.pack_into(
        "<HHIIIHH",
        data,
        pe_offset + 4,
        machine,
        1,
        0x12345678,
        0,
        0,
        optional_header_size,
        0,
    )

    optional_offset = pe_offset + 24
    struct.pack_into("<H", data, optional_offset, 0x20B)
    struct.pack_into("<I", data, optional_offset + 56, 0x2000)
    struct.pack_into("<I", data, optional_offset + 60, 0x200)
    struct.pack_into("<I", data, optional_offset + 108, 0)

    data[section_table_offset : section_table_offset + 8] = b".text\0\0\0"
    struct.pack_into(
        "<IIII",
        data,
        section_table_offset + 8,
        0x100,
        0x1000,
        0,
        0,
    )
    return bytes(data)


class InspectFileFailureTests(unittest.TestCase):
    def test_missing_file_fails_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing_path = Path(temporary_directory) / "missing.dll"

            with self.assertRaisesRegex(
                inventory.InventoryError, "file does not exist"
            ):
                inventory.inspect_file(str(missing_path))

    def test_directory_path_fails_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaisesRegex(
                inventory.InventoryError, "path is a directory, not a file"
            ):
                inventory.inspect_file(temporary_directory)

    def test_non_pe_file_fails_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            input_path = Path(temporary_directory) / "not-a-pe.bin"
            input_path.write_bytes(b"plain test data")

            with self.assertRaisesRegex(
                inventory.InventoryError, "input is not a PE file"
            ):
                inventory.inspect_file(str(input_path))

    def test_direct_unc_path_is_rejected_before_resolution(self) -> None:
        unc_path = r"\\inventory-test.invalid\share\missing.dll"

        with mock.patch.object(
            inventory.Path,
            "resolve",
            side_effect=AssertionError("UNC path was resolved"),
        ) as resolve:
            with self.assertRaisesRegex(
                inventory.InventoryError,
                "network-backed input path is not allowed",
            ):
                inventory.inspect_file(unc_path)

        resolve.assert_not_called()


class PeImageParserTests(unittest.TestCase):
    def test_malformed_pe_fails_clearly(self) -> None:
        data = bytearray(synthetic_pe())
        struct.pack_into("<H", data, 0x80 + 4 + 16, 119)

        with self.assertRaisesRegex(inventory.InventoryError, "malformed PE"):
            inventory.PeImage(bytes(data))

    def test_x86_pe_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            inventory.InventoryError,
            r"unsupported architecture: PE machine 0x014c",
        ):
            inventory.PeImage(synthetic_pe(machine=0x014C))

    def test_absent_codeview_record_is_non_fatal(self) -> None:
        image = inventory.PeImage(synthetic_pe())

        self.assertEqual(
            image.codeview_record(),
            {
                "present": False,
                "format": None,
                "pdb_name": None,
                "guid": None,
                "age": None,
            },
        )


if __name__ == "__main__":
    unittest.main()
