"""Small generated-media smoke tests that never require user/client assets."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from fix.media.ffmpeg import export_frame, trim_video
from fix.media.ffprobe import probe_media
from fix.media.validation import validate_output


@pytest.fixture()
def short_video(tmp_path):
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        pytest.skip("FFmpeg/FFprobe are required for media integration tests")
    source = tmp_path / "sample video.mp4"
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=24",
        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000",
        "-t", "3.0", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", str(source),
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode:
        pytest.skip("FFmpeg build lacks required encoders: " + result.stderr[-350:])
    return source


def test_export_frame_with_real_ffmpeg(short_video, tmp_path):
    output = tmp_path / "exported 1.25s.png"
    messages = []
    export_frame(short_video, output, 1.25, lambda v, t: messages.append((v, t)))
    validate_output(output)
    info = probe_media(output)
    assert info.width == 160 and info.height == 90
    assert output.stat().st_size > 300
    assert messages[-1][0] == 1.0


def test_trim_non_keyframe_interval_with_real_ffmpeg(short_video, tmp_path):
    output = tmp_path / "trimmed.mp4"
    trim_video(short_video, output, 0.54, 1.74, probe_media(short_video), lambda *_: None)
    validate_output(output)
    info = probe_media(output)
    assert 1.1 <= info.duration <= 1.4
    assert info.width == 160 and info.height == 90
    assert short_video.exists()


def test_overlay_failed_image_preserves_original(short_video, tmp_path):
    import hashlib
    from fix.core.errors import MediaProcessingError
    from fix.core.models import Selection
    from fix.media.ffmpeg import overlay_watermark_local

    invalid_image = tmp_path / "not_an_image.png"
    invalid_image.write_text("not a real PNG", encoding="utf-8")
    before = hashlib.sha256(short_video.read_bytes()).digest()
    with pytest.raises(MediaProcessingError):
        overlay_watermark_local(
            short_video, invalid_image, (Selection(10, 10, 30, 20),),
            probe_media(short_video), 1.0, 0.5, lambda *_: None,
        )
    assert hashlib.sha256(short_video.read_bytes()).digest() == before


def test_overlay_succeeds_and_retains_duration(short_video, tmp_path):
    import hashlib
    from fix.core.models import Selection
    from fix.media.ffmpeg import overlay_watermark_local

    logo = tmp_path / "logo.png"
    export_frame(short_video, logo, 0.1, lambda *_: None)
    source_hash = hashlib.sha256(short_video.read_bytes()).digest()
    media = probe_media(short_video)
    overlay_watermark_local(
        short_video, logo, (Selection(8, 8, 32, 24),),
        media, 1.0, 0.5, lambda *_: None,
    )
    assert hashlib.sha256(short_video.read_bytes()).digest() != source_hash
    result = probe_media(short_video)
    assert abs(result.duration - media.duration) < 0.3
    assert result.width == media.width and result.height == media.height
