# Windows contributor setup (native, MSYS2 UCRT64)

FIX can be launched on Windows from the **same Python/GTK source tree** using
MSYS2 UCRT64 packages. This is a contributor setup path, **not a validated
Windows release** or installer. Test on an actual Windows 10/11 machine before
claiming full platform support. The project roadmap reserves release support
for milestone M5.

## Install

1. Install [MSYS2](https://www.msys2.org/) (normally `C:\msys64`).
2. Open the **MSYS2 UCRT64** terminal, not MSYS, MINGW64 or Windows Python.
3. Update the package database and packages:

   ```bash
   pacman -Syu
   ```

   Close/reopen the UCRT64 terminal if MSYS2 asks, and run `pacman -Syu` again
   until up to date.

4. Install the matching UCRT64 runtime packages:

   ```bash
   pacman -S --needed mingw-w64-ucrt-x86_64-python mingw-w64-ucrt-x86_64-gtk4 mingw-w64-ucrt-x86_64-python-gobject mingw-w64-ucrt-x86_64-python-cairo mingw-w64-ucrt-x86_64-python-opencv mingw-w64-ucrt-x86_64-ffmpeg mingw-w64-ucrt-x86_64-python-pytest
   ```

   The packages include `ffmpeg` and `ffprobe`; do not combine them with a
   different FFmpeg or Python installation on your PATH. Do **not** run ordinary
   `pip install -r requirements.txt` in Windows CPython to set up GTK.

## Run

Extract the repository to a normal writable folder. In Windows Explorer,
double-click `run-windows.cmd` (or from Command Prompt run it directly):

```cmd
run-windows.cmd --check
run-windows.cmd --test
run-windows.cmd
```

`--check` checks every runtime dependency. `--test` also runs the Python unit
suite; neither starts the GUI. Without options, the launcher starts the GUI.

The launcher defaults to `C:\msys64`. If MSYS2 is elsewhere, in Command
Prompt set `MSYS2_ROOT` first, for example:

```cmd
set "MSYS2_ROOT=D:\Tools\msys64"
run-windows.cmd
```

The launcher intentionally uses `MSYS2_ROOT\ucrt64\bin\python.exe` and prepends
its binary directory to PATH so GI typelibs, GTK DLLs, OpenCV and FFmpeg all
come from the same runtime. Do not use WSL, duplicate FIX's media engine, or
run the app with a Windows Store/Anaconda Python installation.

## Verify on a Windows machine

1. Run dependency check and unit tests.
2. Start GUI; open a short **self-owned/sample** MP4 with sound.
3. Preview and seek; export a PNG frame; trim a non-keyframe interval.
4. Test remove-watermark, add-overlay, and cover-art operations separately.
5. Verify the outputs with `ffprobe`, including streams/metadata and durations.
6. Check paths containing spaces and Unicode characters.
7. Test failure and source integrity (including an invalid watermark input).

If the application does not start, run `run-windows.cmd --check` from an open
Command Prompt to see the missing package message. Report actual Windows OS,
MSYS2 environment, program output and FFmpeg version in the issue.

## Runtime limitations

The current project has no self-contained `.exe` installer; an MSYS2 runtime is
required. Windows UI and codecs have not been independently validated here.
Only claim native Windows support after runtime and real-media validation.

Sources: [PyGObject Windows getting started](https://pygobject.gnome.org/getting_started.html),
[GTK on Windows](https://www.gtk.org/docs/installations/windows/),
[MSYS2](https://www.msys2.org/).
