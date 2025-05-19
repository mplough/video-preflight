# video-preflight

## Prereqs

Handbrake CLI, ExifTool
```
brew install handbrake exiftool
```

## Install

Installation requires [uv](https://docs.astral.sh/uv/).  On macOS, install it with:
```bash
brew install uv
```

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

### notes

QuickTime Player Version 10.5 (1216.2)

The inspector (Cmd+I) shows GPS information for .mov files but not .mp4 files.


ExifTool only reads QuickTime-formatted metadata.

HoudahGeo writes `quicktime.location.ISO6709`, which QuickTime and Apple Photos can read.

May 3, 2019 - per Phil Harvey - 
[New ability to create QuickTime tags in MOV/MP4 videos!](https://exiftool.org/forum/index.php?topic=10091.0)
ExifTool 11.39 has the ability to add new QuickTime ItemList and UserData tags in MOV/MP4 videos!


This will tag in a way that QuickTime Player can read:

```
exiftool -Keys:GPSCoordinates="50 deg 50' 50.50\" N, 80 deg 10' 10.10\" W" out-exiftool-tagged.mp4
```


More info about writing Keys tags: https://exiftool.org/forum/index.php?topic=16678.msg89630#msg89630

documentation: https://exiftool.org/exiftool_pod.html

The `-config` argument can be used to specify a configuration file.
And we can write in a configuration file that we'd prefer to write to Keys first.

Do that:
```
# Change default location for writing QuickTime tags so Keys is preferred
# (by default, the PREFERRED levels are: ItemList=2, UserData=1, Keys=0)
use Image::ExifTool::QuickTime;
$Image::ExifTool::QuickTime::Keys{PREFERRED} = 3;
```

And then run like this
```
exiftool -config exiftool.config -all= -tagsfromfile=IMG_7952.MOV out.mp4
```
