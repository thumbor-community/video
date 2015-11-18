# coding: utf-8

# Copyright (c) 2015, thumbor-community
# Use of this source code is governed by the MIT license that can be
# found in the LICENSE file.

from thumbor.loaders import LoaderResult
from datetime import datetime
from os import fstat
from os.path import join, exists, abspath
from urllib import unquote
from tornado.concurrent import return_future


@return_future
def load(context, path, callback):
    """
    Loads a file. In case the requested file is a video, instead of loading
    its contents this method extracts a frame from the video using ffmpeg,
    and returns the image.
    :param Context context: Thumbor's context
    :param string url: Path to load
    :param callable callback: Callback method once done
    """
    file_path = join(context.config.FILE_LOADER_ROOT_PATH.rstrip('/'), unquote(path).lstrip('/'))
    file_path = abspath(file_path)
    inside_root_path = file_path.startswith(context.config.FILE_LOADER_ROOT_PATH)

    result = LoaderResult()

    if inside_root_path and exists(file_path):

        # If this is a video, extract a frame and load it instead
        if is_video(file_path):
            file_path = get_video_frame(context, file_path)

        with open(file_path, 'r') as f:
            stats = fstat(f.fileno())

            result.successful = True
            result.buffer = f.read()

            result.metadata.update(
                size=stats.st_size,
                updated_at=datetime.utcfromtimestamp(stats.st_mtime)
            )
    else:
        result.error = LoaderResult.ERROR_NOT_FOUND
        result.successful = False

    callback(result)


def is_video(file_path):
    """
    Checks whether the file is a video.
    """
    import mimetypes
    type = mimetypes.guess_type(file_path)[0]
    return type and type.startswith('video')


def get_video_frame(context, file_path):
    """
    Extracts a single frame out of a video file and stores it
    in a temporary file. Returns the path of the temporary file.
    Depends on FFMPEG_PATH from Thumbor's configuration.
    """
    import subprocess, tempfile, os
    f, image_path = tempfile.mkstemp('.jpg')
    os.close(f)
    cmd = [
        context.config.FFMPEG_PATH,
        '-i', file_path,
        '-ss', '00:00:01.000',
        '-vframes', '1',
        '-y', 
        '-nostats', 
        '-loglevel', 'error',
        image_path
    ]
    subprocess.call(cmd)
    print image_path
    return image_path
