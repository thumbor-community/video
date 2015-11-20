# Thumbor Video

This package provides a file loader that loads both images and videos.
When asked to load a video file, it uses `ffmpeg` to extract a single frame
from the video, and returns it instead of the original video.

This allows Thumbor to create thumbnails from video files.


## Installing

    $ pip install tc_video

## Configuration

```
# Use the custom file loader
LOADER = 'tc_video.loaders.file_loader'
# Full path to ffmpeg
FFMPEG = '/usr/bin/ffmpeg'
```
