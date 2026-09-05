from __future__ import annotations

import unittest

from maxwell_lab.characterize import render_public_markdown
from maxwell_lab.sanitize import (
    UnsafePublicOutput,
    assert_public_safe,
    build_public_snapshot,
)


class SanitizerTests(unittest.TestCase):
    def sample_inventory(self) -> dict:
        return {
            "platform": {
                "release": "6.17.0-test",
                "machine": "x86_64",
                "hostname": "secret-host",
            },
            "os_release": {"PRETTY_NAME": "Fedora Linux 44"},
            "hardware": {
                "system_vendor": "ExampleVendor",
                "product_name": "Example Laptop",
                "product_version": "1.0",
                "bios_vendor": "ExampleBIOS",
                "bios_version": "2.3",
                "bios_date": "01/02/2026",
                "cpu_model": "Intel Test CPU",
                "memory_total_kib": 16 * 1024 * 1024,
                "serial_number": "SHOULD-NOT-LEAK",
            },
            "session": {"type": "wayland", "desktop": "GNOME"},
            "graphics": {
                "lspci": {
                    "stdout": (
                        "01:00.0 3D controller [0302]: NVIDIA Corporation GM107M "
                        "[GeForce GTX 960M] [10de:139b] (rev a2)\n"
                        "\tSubsystem: Example Device [1234:5678]\n"
                        "\tKernel driver in use: nouveau\n"
                        "02:00.0 Network controller [0280]: Secret Wi-Fi [9999:0001]"
                    )
                },
                "vulkan_summary": {
                    "stdout": (
                        "Vulkan Instance Version: 1.4.0\n"
                        "deviceName = GM107\n"
                        "deviceUUID = 123e4567-e89b-12d3-a456-426614174000\n"
                        "driverName = NVK"
                    )
                },
                "opengl_summary": {"stdout": "OpenGL renderer string: NV117\n"},
                "drm_devices": [
                    {
                        "node": "card1",
                        "vendor": "0x10de",
                        "device": "0x139b",
                        "driver": "nouveau",
                    }
                ],
                "drm_connectors": [
                    {"name": "card1-HDMI-A-1", "status": "disconnected"}
                ],
                "nvidia_smi": {"stdout": ""},
                "nouveau_pstates": [],
                "nvidia_pci_runtime_pm": [],
                "prime_providers": {"stdout": ""},
            },
        }

    def test_public_snapshot_is_allowlist_based(self) -> None:
        raw = self.sample_inventory()
        public = build_public_snapshot(raw)
        text = render_public_markdown(public)

        self.assertIn("GeForce GTX 960M", text)
        self.assertIn("10de:139b", text)
        self.assertIn("Fedora Linux 44", text)
        self.assertNotIn("Secret Wi-Fi", text)
        self.assertNotIn("SHOULD-NOT-LEAK", text)
        self.assertNotIn("secret-host", text)
        self.assertNotIn("deviceUUID", text)

        assert_public_safe(text, inventory=raw)

    def test_safety_gate_rejects_identifiers(self) -> None:
        for value in (
            "00:11:22:33:44:55",
            "123e4567-e89b-12d3-a456-426614174000",
            "/home/alice/result.txt",
            "Serial Number: ABC",
        ):
            with self.subTest(value=value):
                with self.assertRaises(UnsafePublicOutput):
                    assert_public_safe(value)

    def test_safety_gate_rejects_hostname_from_inventory(self) -> None:
        raw = self.sample_inventory()
        with self.assertRaises(UnsafePublicOutput):
            assert_public_safe("machine secret-host", inventory=raw)


if __name__ == "__main__":
    unittest.main()
