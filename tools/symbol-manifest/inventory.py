#!/usr/bin/env python3
"""Produce an inventory-only identity record for one local AMD64 PE file."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import ntpath
import os
from pathlib import Path
import struct
import sys
import uuid


TOOL_VERSION = "0.1.0"
MAX_FILE_SIZE = 1024 * 1024 * 1024
MAX_SECTIONS = 96
MAX_DEBUG_ENTRIES = 256
MAX_CODEVIEW_SIZE = 1024 * 1024
AMD64_MACHINE = 0x8664


class InventoryError(Exception):
    """An expected input or local file inspection failure."""


class PeImage:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.sections: list[tuple[int, int, int, int]] = []
        self.machine = 0
        self.timestamp = 0
        self.size_of_image = 0
        self.size_of_headers = 0
        self.debug_rva = 0
        self.debug_size = 0
        self._parse_headers()

    def _require_range(self, offset: int, size: int, description: str) -> None:
        if offset < 0 or size < 0 or offset > len(self.data) - size:
            raise InventoryError(f"malformed PE: {description} is outside the file")

    def _unpack_from(self, format_string: str, offset: int, description: str):
        size = struct.calcsize(format_string)
        self._require_range(offset, size, description)
        return struct.unpack_from(format_string, self.data, offset)

    def _parse_headers(self) -> None:
        if len(self.data) < 64 or self.data[:2] != b"MZ":
            raise InventoryError("input is not a PE file: missing DOS MZ signature")

        (pe_offset,) = self._unpack_from("<I", 0x3C, "PE header offset")
        self._require_range(pe_offset, 24, "PE signature and COFF header")
        if self.data[pe_offset : pe_offset + 4] != b"PE\0\0":
            raise InventoryError("input is not a PE file: missing PE signature")

        coff_offset = pe_offset + 4
        (
            self.machine,
            section_count,
            self.timestamp,
            _,
            _,
            optional_header_size,
            _,
        ) = self._unpack_from("<HHIIIHH", coff_offset, "COFF header")

        if self.machine != AMD64_MACHINE:
            raise InventoryError(
                "unsupported architecture: "
                f"PE machine 0x{self.machine:04x}; only amd64 (0x8664) is accepted"
            )
        if section_count == 0 or section_count > MAX_SECTIONS:
            raise InventoryError(
                f"malformed PE: unreasonable section count {section_count}"
            )

        optional_offset = coff_offset + 20
        if optional_header_size < 120 or optional_header_size > 4096:
            raise InventoryError(
                "malformed PE: invalid PE32+ optional-header size "
                f"{optional_header_size}"
            )
        self._require_range(
            optional_offset, optional_header_size, "PE32+ optional header"
        )

        (optional_magic,) = self._unpack_from(
            "<H", optional_offset, "optional-header magic"
        )
        if optional_magic != 0x20B:
            raise InventoryError(
                f"malformed PE: amd64 image has optional-header magic "
                f"0x{optional_magic:04x}, expected PE32+ (0x020b)"
            )

        (self.size_of_image,) = self._unpack_from(
            "<I", optional_offset + 56, "SizeOfImage"
        )
        (self.size_of_headers,) = self._unpack_from(
            "<I", optional_offset + 60, "SizeOfHeaders"
        )
        (directory_count,) = self._unpack_from(
            "<I", optional_offset + 108, "data-directory count"
        )
        if self.size_of_image == 0:
            raise InventoryError("malformed PE: SizeOfImage is zero")

        debug_directory_end = 112 + (7 * 8)
        if directory_count > 6 and optional_header_size >= debug_directory_end:
            self.debug_rva, self.debug_size = self._unpack_from(
                "<II", optional_offset + 112 + (6 * 8), "debug data directory"
            )

        section_table_offset = optional_offset + optional_header_size
        self._require_range(
            section_table_offset, section_count * 40, "section table"
        )
        for index in range(section_count):
            section_offset = section_table_offset + (index * 40)
            virtual_size, virtual_address, raw_size, raw_offset = self._unpack_from(
                "<IIII", section_offset + 8, f"section {index + 1}"
            )
            self.sections.append(
                (virtual_address, virtual_size, raw_offset, raw_size)
            )

    def rva_to_offset(self, rva: int, size: int, description: str) -> int:
        if rva < self.size_of_headers:
            self._require_range(rva, size, description)
            return rva

        for virtual_address, virtual_size, raw_offset, raw_size in self.sections:
            mapped_size = max(virtual_size, raw_size)
            if virtual_address <= rva < virtual_address + mapped_size:
                relative_offset = rva - virtual_address
                if relative_offset > raw_size or size > raw_size - relative_offset:
                    break
                file_offset = raw_offset + relative_offset
                self._require_range(file_offset, size, description)
                return file_offset

        raise InventoryError(f"malformed PE: {description} has an unmapped RVA")

    def codeview_record(self) -> dict[str, object]:
        absent = {
            "present": False,
            "format": None,
            "pdb_name": None,
            "guid": None,
            "age": None,
        }
        if self.debug_rva == 0 or self.debug_size == 0:
            return absent
        if self.debug_size < 28:
            raise InventoryError("malformed PE: debug directory is too small")
        if self.debug_size % 28 != 0:
            raise InventoryError(
                "malformed PE: debug directory size is not a whole number "
                "of entries"
            )

        entry_count = self.debug_size // 28
        if entry_count > MAX_DEBUG_ENTRIES:
            raise InventoryError(
                f"malformed PE: unreasonable debug-directory count {entry_count}"
            )
        debug_offset = self.rva_to_offset(
            self.debug_rva, entry_count * 28, "debug directory"
        )

        records: list[dict[str, object]] = []
        for index in range(entry_count):
            entry_offset = debug_offset + (index * 28)
            (
                _,
                _,
                _,
                _,
                debug_type,
                data_size,
                data_rva,
                data_offset,
            ) = self._unpack_from(
                "<IIHHIIII", entry_offset, f"debug-directory entry {index + 1}"
            )
            if debug_type != 2:
                continue
            if data_size < 4 or data_size > MAX_CODEVIEW_SIZE:
                raise InventoryError(
                    "malformed PE: invalid CodeView record size "
                    f"{data_size}"
                )
            if data_offset:
                self._require_range(
                    data_offset, data_size, f"CodeView record {index + 1}"
                )
                record_offset = data_offset
            elif data_rva:
                record_offset = self.rva_to_offset(
                    data_rva, data_size, f"CodeView record {index + 1}"
                )
            else:
                raise InventoryError(
                    "malformed PE: CodeView entry has no file offset or RVA"
                )
            records.append(
                self._decode_codeview(
                    self.data[record_offset : record_offset + data_size]
                )
            )

        if not records:
            return absent

        format_order = {"RSDS": 0, "NB10": 1}
        records.sort(key=lambda item: format_order.get(str(item["format"]), 2))
        return records[0]

    @staticmethod
    def _pdb_name(raw_path: bytes) -> str | None:
        path_bytes = raw_path.split(b"\0", 1)[0]
        if not path_bytes:
            return None
        decoded = path_bytes.decode("utf-8", errors="replace")
        return ntpath.basename(decoded) or None

    def _decode_codeview(self, record: bytes) -> dict[str, object]:
        signature = record[:4]
        if signature == b"RSDS":
            if len(record) < 24:
                raise InventoryError("malformed PE: truncated RSDS CodeView record")
            guid = str(uuid.UUID(bytes_le=record[4:20]))
            (age,) = struct.unpack_from("<I", record, 20)
            return {
                "present": True,
                "format": "RSDS",
                "pdb_name": self._pdb_name(record[24:]),
                "guid": guid,
                "age": age,
            }
        if signature == b"NB10":
            if len(record) < 16:
                raise InventoryError("malformed PE: truncated NB10 CodeView record")
            (age,) = struct.unpack_from("<I", record, 12)
            return {
                "present": True,
                "format": "NB10",
                "pdb_name": self._pdb_name(record[16:]),
                "guid": None,
                "age": age,
            }
        return {
            "present": True,
            "format": f"unknown-{signature.hex()}",
            "pdb_name": None,
            "guid": None,
            "age": None,
        }


class VsFixedFileInfo(ctypes.Structure):
    _fields_ = [
        ("signature", ctypes.c_uint32),
        ("structure_version", ctypes.c_uint32),
        ("file_version_ms", ctypes.c_uint32),
        ("file_version_ls", ctypes.c_uint32),
        ("product_version_ms", ctypes.c_uint32),
        ("product_version_ls", ctypes.c_uint32),
        ("file_flags_mask", ctypes.c_uint32),
        ("file_flags", ctypes.c_uint32),
        ("file_os", ctypes.c_uint32),
        ("file_type", ctypes.c_uint32),
        ("file_subtype", ctypes.c_uint32),
        ("file_date_ms", ctypes.c_uint32),
        ("file_date_ls", ctypes.c_uint32),
    ]


def _format_version(ms: int, ls: int) -> str:
    return f"{ms >> 16}.{ms & 0xffff}.{ls >> 16}.{ls & 0xffff}"


def read_versions(path: Path) -> tuple[str, str]:
    if os.name != "nt":
        raise InventoryError(
            "version metadata inspection is currently supported only on Windows"
        )

    version = ctypes.WinDLL("version", use_last_error=True)
    version.GetFileVersionInfoSizeW.argtypes = [
        ctypes.c_wchar_p,
        ctypes.POINTER(ctypes.c_uint32),
    ]
    version.GetFileVersionInfoSizeW.restype = ctypes.c_uint32
    version.GetFileVersionInfoW.argtypes = [
        ctypes.c_wchar_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
    ]
    version.GetFileVersionInfoW.restype = ctypes.c_int
    version.VerQueryValueW.argtypes = [
        ctypes.c_void_p,
        ctypes.c_wchar_p,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_uint32),
    ]
    version.VerQueryValueW.restype = ctypes.c_int

    ignored = ctypes.c_uint32()
    ctypes.set_last_error(0)
    info_size = version.GetFileVersionInfoSizeW(str(path), ctypes.byref(ignored))
    if info_size == 0:
        error_code = ctypes.get_last_error()
        if error_code:
            raise InventoryError(
                "required file and product version metadata is unavailable: "
                f"{ctypes.WinError(error_code)}"
            )
        raise InventoryError(
            "required file and product version metadata is absent"
        )

    buffer = ctypes.create_string_buffer(info_size)
    if not version.GetFileVersionInfoW(str(path), 0, info_size, buffer):
        raise InventoryError("could not read the local file version resource")

    value_pointer = ctypes.c_void_p()
    value_size = ctypes.c_uint32()
    ctypes.set_last_error(0)
    if not version.VerQueryValueW(
        buffer, "\\", ctypes.byref(value_pointer), ctypes.byref(value_size)
    ):
        error_code = ctypes.get_last_error()
        if error_code:
            raise InventoryError(
                "required fixed file and product version metadata could not "
                f"be read: {ctypes.WinError(error_code)}"
            )
        raise InventoryError(
            "required fixed file and product version metadata is absent"
        )
    if value_size.value < ctypes.sizeof(VsFixedFileInfo):
        raise InventoryError("malformed PE: truncated fixed file version resource")

    fixed_info = ctypes.cast(
        value_pointer, ctypes.POINTER(VsFixedFileInfo)
    ).contents
    if fixed_info.signature != 0xFEEF04BD:
        raise InventoryError("malformed PE: invalid fixed file version signature")

    return (
        _format_version(fixed_info.file_version_ms, fixed_info.file_version_ls),
        _format_version(
            fixed_info.product_version_ms, fixed_info.product_version_ls
        ),
    )


def inspect_file(input_path: str) -> dict[str, object]:
    path = Path(input_path).expanduser()
    if not path.exists():
        raise InventoryError(f"file does not exist: {path}")
    if path.is_dir():
        raise InventoryError(f"path is a directory, not a file: {path}")
    if not path.is_file():
        raise InventoryError(f"path is not a regular file: {path}")

    try:
        resolved_path = path.resolve(strict=True)
        file_size = resolved_path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise InventoryError(
                f"input is too large: {file_size} bytes; limit is {MAX_FILE_SIZE}"
            )
        data = resolved_path.read_bytes()
    except OSError as error:
        raise InventoryError(f"could not read local file: {error}") from error

    pe = PeImage(data)
    file_version, product_version = read_versions(resolved_path)

    return {
        "schema_version": 1,
        "record_type": "module-identity-draft",
        "support_state": "inventory-only",
        "support_note": (
            "Local file identity only; no Windows build support is established."
        ),
        "generator": {
            "name": "taskbar-listview-module-inventory",
            "version": TOOL_VERSION,
        },
        "module": {
            "module_name": resolved_path.name.lower(),
            "input_path": str(resolved_path),
            "architecture": "amd64",
            "pe_machine": "0x8664",
            "file_version": file_version,
            "product_version": product_version,
            "pe_timestamp": f"0x{pe.timestamp:08x}",
            "size_of_image": pe.size_of_image,
            "sha256": hashlib.sha256(data).hexdigest(),
            "codeview": pe.codeview_record(),
        },
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect one copied local AMD64 PE file and emit an inventory-only "
            "draft module identity record."
        )
    )
    parser.add_argument("path", help="path to a local copied PE file")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        record = inspect_file(args.path)
    except InventoryError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    json.dump(record, sys.stdout, indent=2, ensure_ascii=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
