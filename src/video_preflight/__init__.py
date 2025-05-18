import subprocess
from pathlib import Path

import click

@click.group
def cli() -> None:
    """Video preflight tools."""


def _exiftool_config_path() -> Path:
    return (Path(__file__).parent / "exiftool.config").absolute()

def _handbrake_presets_base_path() -> Path:
    return (Path(__file__).parent / "handbrake_presets").absolute()

def _handbrake_preset_path(name: str) -> Path:
    return _handbrake_presets_base_path() / f"{name}.json"

def run_exiftool(*args):
    command = [
        "exiftool",
        "-config",
        str(_exiftool_config_path()),
    ] + list(args)

    subprocess.run(command, check=True)


def run_handbrake(*args):
    command = ["HandBrakeCLI"] + list(args)
    subprocess.run(command, check=True)


def run_ffmpeg(*args):
    command = ["ffmpeg"] + list(args)
    subprocess.run(command, check=True)


@cli.command("copy-tags")
@click.pass_context
@click.argument("source_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path))
@click.argument("destination_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path))
def click_copy_tags(ctx: click.Context, source_file: Path, destination_file: Path):
    if destination_file.suffix == ".MOV":
        click.echo(".MOV files come from a camera!")
        click.echo("Did you mean to specify the destination as the source?")
        click.echo("Not copying.")
        ctx.exit(1)

    tags_to_skip = ["PreviewImage", "ThumbnailImage"]
    args = ["-all="] + [f"-tagsfromfile={source_file}"] + [f"-{tag}=" for tag in tags_to_skip] + [f"{destination_file}"]
    run_exiftool(*args)

    click.echo("Done copying tags.")


@cli.command("write-mov-container")
@click.pass_context
@click.argument("source_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path))
def click_write_mov_container(ctx: click.Context, source_file: Path):
    destination_file = source_file.with_suffix(".mov")
    if destination_file.exists():
        click.echo("Destination file {destination_file} already exists, exiting...")
        ctx.exit(1)

    args = ["-i", str(source_file), "-acodec", "copy", "-vcodec", "copy", "-f", "mov",
            str(destination_file)]
    run_ffmpeg(*args)


@cli.command("compress")
@click.pass_context
@click.argument("source_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path))
@click.option("--quality", type=float, default=22)
@click.option("--copy-tags", is_flag=True, default=True)
def click_compress(ctx: click.Context, source_file: Path, quality: float, copy_tags: bool):
    destination_file = source_file.with_suffix(".mp4")

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

    if copy_tags:
        ctx.invoke(click_copy_tags, source_file=source_file,
                   destination_file=destination_file)

def main() -> None:
    cli()
