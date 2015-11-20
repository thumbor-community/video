# coding: utf-8

# Copyright (c) 2015, thumbor-community
# Use of this source code is governed by the MIT license that can be
# found in the LICENSE file.

from thumbor.loaders import LoaderResult
from thumbor.utils import logger
from datetime import datetime
from os import fstat
from os.path import join, exists, abspath
from urllib import unquote
from tornado.concurrent import return_future
from contextlib import contextmanager


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

    if inside_root_path and exists(file_path):

        if is_video(file_path):
            # Extract a frame from the video and load it instead of the original path
            with get_video_frame(context, file_path) as image_path:
                if image_path:
                    callback(read_file(image_path))
                    return
        else:
            callback(read_file(file_path))
            return

    # If we got here, there was a failure
    result = LoaderResult()
    result.error = LoaderResult.ERROR_NOT_FOUND
    result.successful = False
    callback(result)


def read_file(file_path):
    """
    Read the given file path and its metadata. Returns a LoaderResult.
    """
    with open(file_path, 'r') as f:
        stats = fstat(f.fileno())
        return LoaderResult(
            buffer = f.read(),
            successful = True,
            metadata = dict(size=stats.st_size, updated_at=datetime.utcfromtimestamp(stats.st_mtime))
        )


def is_video(file_path):
    """
    Checks whether the file is a video.
    """
    import mimetypes
    type = mimetypes.guess_type(file_path)[0]
    return type and type.startswith('video')


@contextmanager
def get_video_frame(context, file_path):
    """
    A context manager that extracts a single frame out of a video file and 
    stores it in a temporary file. Returns the path of the temporary file
    or None in case of failure.
    Depends on FFMPEG_PATH from Thumbor's configuration.
    """
    import subprocess, tempfile, os
    # Fail nicely when ffmpeg cannot be found
    if not os.path.exists(context.config.FFMPEG_PATH):
        logger.error('%s does not exist, please configure FFMPEG_PATH', context.config.FFMPEG_PATH)
        yield None
        return
    # Prepare temporary file
    f, image_path = tempfile.mkstemp('.jpg')
    os.close(f)
    # Extract image
    try:
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
        subprocess.check_call(cmd)
        yield image_path
    except:
        logger.exception('Cannot extract image frame from %s', file_path)
        yield None
    finally:
        # Cleanup
        try_to_delete(image_path)


def try_to_delete(file_path):
    """
    Delete the given file path but do not raise any exception.
    """
    try:
        os.remove(file_path)
    except:
        pass
