from __future__ import annotations

from fix.core.plugin import FixPlugin, PluginMetadata
from .adapter import ExportFrameAdapter


class ExportFramePlugin(FixPlugin):
    metadata = PluginMetadata(
        plugin_id="export_frame",
        name="Export PNG Frame",
        version="1.0.0",
        description="Save the current video frame as a PNG image.",
    )

    def create_adapter(self) -> ExportFrameAdapter:
        return ExportFrameAdapter()
