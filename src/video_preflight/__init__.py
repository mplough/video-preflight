import shutil
import subprocess
from pathlib import Path

import click

def _exiftool_config_path() -> Path:
    return (Path(__file__).parent / "exiftool.config").absolute()


def _handbrake_presets_base_path() -> Path:
    return (Path(__file__).parent / "handbrake_presets").absolute()


def _handbrake_preset_path(name: str) -> Path:
    return _handbrake_presets_base_path() / f"{name}.json"


def run_exiftool(*args):
    """Run exiftool (with our custom configuration) with the given arguments.

    Our custom configuration prefers writing QuickTime tags as that's the only
    kind of tags that Apple Photos currently supports.
    """
    command = [
        "exiftool",
        "-config",
        str(_exiftool_config_path()),
    ] + list(args)

    subprocess.run(command, check=True)


def run_handbrake(*args):
    """Run handbrake command-line interface with the given arguments."""
    command = ["HandBrakeCLI"] + list(args)
    subprocess.run(command, check=True)


def run_ffmpeg(*args):
    """Run ffmpeg with the given arguments."""
    command = ["ffmpeg"] + list(args)
    subprocess.run(command, check=True)


def _exit_if_path_exists(path: Path, path_description: str):
    if path.exists():
        click.echo("{path_description} {path} already exists, exiting...")
        ctx.exit(1)


@click.group
def cli() -> None:
    """Video preflight tools."""


@cli.command("replace-audio")
@click.pass_context
@click.argument("source_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path))
@click.argument("new_audio_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path))
@click.argument("destination_file", type=click.Path(exists=False, path_type=Path))
def click_replace_audio(ctx: click.Context, source_file: Path, new_audio_file: Path, destination_file: Path):
    click.echo("Replacing audio is not yet implemented.")
    ctx.exit(1)


@cli.command("copy-tags")
@click.pass_context
@click.argument("source_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path))
@click.argument("destination_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path))
def click_copy_tags(ctx: click.Context, source_file: Path, destination_file: Path):
    """Copy tags from source and write them to destination as QuickTime Keys.

    Uses ExifTool under the hood.

    Apple Photos doesn't recognize EXIF or XMP metadata.
    """
    if destination_file.suffix == ".MOV":
        click.echo(".MOV files come from a camera!")
        click.echo("Did you mean to specify the destination as the source?")
        click.echo("Not copying.")
        ctx.exit(1)

    click.echo("Copying tags ...")

    tags_to_skip = [
        # These tags bloat the video but don't help much
        "PreviewImage",
        "ThumbnailImage",
    ]

    args = (
        ["-all="]
        + [f"-tagsfromfile={source_file}"]
        + [f"-{tag}=" for tag in tags_to_skip]
        + [f"{destination_file}"]
    )
    run_exiftool(*args)

    copy_lens_model = [
        "-LensModel-eng-US<LensModel",
        f"{destination_file}",
    ]
    run_exiftool(*copy_lens_model)

    click.echo("Done copying tags.")


@cli.command("compress")
@click.pass_context
@click.argument("source_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path))
@click.argument("destination_file", type=click.Path(exists=False, path_type=Path))
@click.option("--quality", type=float, default=22)
@click.option("--copy-tags", is_flag=True, default=True)
def click_compress(ctx: click.Context, source_file: Path, destination_file: Path, quality: float, copy_tags: bool):
    """Compress video using my custom preset.

    Uses x265's constant quality setting; use the --quality option to adjust the quality.
    See HandBrake's recommended quality settings for x265 encoders:
    https://handbrake.fr/docs/en/latest/workflow/adjust-quality.html

    Uses HandBrake's CLI under the hood.
    """
    _exit_if_path_exists(destination_file, "Destination file")

    preset_name = "Matt HEVC HQ"
    click.echo("Compressing {source_file.name} ...")

    args = [
        "-i", str(source_file),
        "--preset-import-file", str(_handbrake_preset_path(preset_name)),
        "--preset", preset_name,
        "--quality", str(quality),
        "--input", str(source_file),
        "--output", str(destination_file),
    ]

    run_handbrake(*args)
    click.echo("Done compressing to {destination_file.name}")


@cli.command("write-mov-container")
@click.pass_context
@click.argument("source_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path))
@click.argument("destination_file", type=click.Path(exists=False, path_type=Path))
def click_write_mov_container(ctx: click.Context, source_file: Path):
    """Write video to a QuickTime .mov container.

    This is an auxiliary command and is not part of the preflight pipeline.

    There may be differences between how .mov and .mp4 files hold metadata; this command
    facilitates easy experimentation.

    Uses ffmpeg to write the contents of SOURCE_FILE to a .mov file without re-compressing.
    """
    _exit_if_path_exists(destination_file, "Destination file")

    args = ["-i", str(source_file), "-acodec", "copy", "-vcodec", "copy", "-f", "mov",
            str(destination_file)]
    run_ffmpeg(*args)


@cli.command("run")
@click.pass_context
@click.argument("source_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path))
@click.option("--replace-audio", type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path))
@click.option("--quality", type=float, default=22)
@click.option("--copy-tags", is_flag=True, default=True)
def click_run(ctx: click.Context, source_file: Path, replace_audio: Path | None, quality: float, copy_tags: bool):
    """Run the preflight pipeline on a source file.

    This tool is intended to preserve metadata from a (perhaps lightly edited) video clip straight
    from a camera.

    Prior to running the pipeline, geotag the source file.
    If you want to denoise or alter the audio, write out a new audio track as well.
    """
    click.echo("Running preflight pipeline ...")
    destination_file = source_file.with_suffix(".mp4")

    if replace_audio is not None:
        replaced_audio_source_file = source_file.with_name(f"{source_file.name}-replaced-audio")
        ctx.invoke(click_compress, source_file=source_file, new_audio_file=replace_audio, destination_file=replaced_audio_source_file)
        if copy_tags:
            ctx.invoke(click_copy_tags, source_file=source_file, destination_file=replaced_audio_source_file)
        source_file = replaced_audio_source_file

    ctx.invoke(click_compress, source_file=source_file, destination_file=destination_file, quality=quality)

    if copy_tags:
        ctx.invoke(click_copy_tags, source_file=source_file, destination_file=destination_file)


def main() -> None:
    cli()
