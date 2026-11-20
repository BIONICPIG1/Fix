from pathlib import Path
import sys
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from fix.core.errors import PluginValidationError
from fix.core.models import MediaInfo, OperationContext
from fix.plugins.export_frame.adapter import ExportFrameAdapter
from fix.plugins import build_registry


def make_context(tmp_path, time=1.25, output_name="saved frame.png"):
    source = tmp_path / "source video.mp4"
    source.write_bytes(b"example")
    media = MediaInfo(
        path=source, duration=5.0, width=160, height=90,
        fps=24.0, video_codec="h264", video_bitrate=100_000, size_bytes=7,
    )
    return OperationContext(
        source=source, media=media, start_seconds=time,
        output=tmp_path / output_name,
    )


def test_registry_includes_export_frame():
    assert build_registry().get("export_frame").metadata.name == "Export PNG Frame"


@pytest.mark.parametrize("time", [-1, 5.0, float("nan"), float("inf")])
def test_export_frame_rejects_out_of_range_times(tmp_path, time):
    with pytest.raises(PluginValidationError, match="inside the video"):
        ExportFrameAdapter().validate(make_context(tmp_path, time=time))


def test_export_frame_rejects_wrong_extension(tmp_path):
    with pytest.raises(PluginValidationError, match=".png"):
        ExportFrameAdapter().build_plan(make_context(tmp_path, output_name="frame.txt"))


def test_export_frame_requires_new_output(tmp_path):
    ctx = make_context(tmp_path)
    ctx.output = ctx.source
    with pytest.raises(PluginValidationError, match="Cannot overwrite"):
        ExportFrameAdapter().build_plan(ctx)


def test_export_frame_builds_and_runs_plan(tmp_path):
    context = make_context(tmp_path)
    with (
        patch("fix.plugins.export_frame.adapter.export_frame", return_value=context.output) as f,
        patch("fix.plugins.export_frame.adapter.validate_output") as validate,
    ):
        plan = ExportFrameAdapter().build_plan(context)
        assert plan.output == context.output
        assert plan.replace_source is False
        result = plan.runner(lambda *_: None)
        assert result == context.output
        f.assert_called_once_with(context.source, context.output, 1.25, f.call_args.args[-1])
        validate.assert_called_once_with(context.output)
