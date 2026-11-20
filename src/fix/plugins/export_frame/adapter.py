from __future__ import annotations

import math

from fix.core.errors import PluginValidationError
from fix.core.models import OperationContext, OperationPlan
from fix.core.plugin import PluginAdapter
from fix.media.ffmpeg import export_frame
from fix.media.validation import validate_output


class ExportFrameAdapter(PluginAdapter):
    def validate(self, context: OperationContext) -> None:
        if not context.source.is_file():
            raise PluginValidationError("Source video does not exist.")
        if context.output is None:
            raise PluginValidationError("Choose a PNG output path.")
        if context.output.resolve() == context.source.resolve():
            raise PluginValidationError("Cannot overwrite the source video.")
        if context.output.suffix.lower() != ".png":
            raise PluginValidationError("Frame output must be a .png file.")
        if (
            not math.isfinite(context.start_seconds)
            or context.start_seconds < 0
            or context.start_seconds >= context.media.duration
        ):
            raise PluginValidationError("Choose a time inside the video.")

    def build_plan(self, context: OperationContext) -> OperationPlan:
        self.validate(context)
        output = context.output

        def runner(progress):
            result = export_frame(
                context.source,
                output,
                context.start_seconds,
                progress,
            )
            validate_output(result)
            return result

        return OperationPlan(label="Export PNG Frame", runner=runner, output=output)
