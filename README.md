# video-preflight

I store my processed photos and videos in Apple Photos so I can view them from
anywhere on my phone or computer.

With video files, Apple Photos only parses metadata that's stored in QuickTime
tags.  Since video files straight out of my cameras don't store metadata in
that format, the location, camera, and lens metadata doesn't show up if I
put those files directly into Apple Photos.  The files are also much too large
to be reasonably portable or shareable.

This tool allows me to take a video file from my camera, make minor edits to
it, compress it, and re-format the metadata -- a whole preflight pipeline for
bringing video into Apple Photos.

It's a work in progress and is a big step forward in my knowledge of video
metadata since my March 17, 2024 blog post entitled [Working notes on EXIF tags
for video
files](https://mplough.github.io/2024/03/17/video-exif-tags-notes.html).

# Setup
## Prerequisites

As my primary use case is import into Apple Photos, this tool runs on macOS.  I
use [Homebrew](https://brew.sh/) to install tools used by this utility.

It requires:

* [Handbrake](https://handbrake.fr/) command-line interface for video compression
* [ExifTool](https://exiftool.org/) for metadata processing
* [ffmpeg](https://ffmpeg.org/) for remuxing, and in the future, audio
  replacement
* [uv](https://docs.astral.sh/uv/) for installation

Install prerequisites.

1. Install Homebrew.
1. Install tools: `brew install handbrake exiftool ffmpeg uv`

## Installation

Install the tool:
```bash
uv tool install --editable .
```

Ensure that the tool is on the `PATH`:

```bash
uv tool update-shell
```

## Update

```bash
uv tool upgrade video-preflight
```

# Use

Run any command with `--help` to see usage information.

Run the main pipeline via `video-preflight run`.

See `video-preflight --help` for other commands.
