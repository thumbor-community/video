#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from os.path import abspath, join, dirname

from unittest import TestCase
from preggy import expect
import imghdr

from thumbor.context import Context
from thumbor.config import Config
from tc_video.loaders.file_loader import load
from thumbor.loaders import LoaderResult

IMAGE_STORAGE_PATH = abspath(join(dirname(__file__), '../fixtures/images/'))
VIDEO_STORAGE_PATH = abspath(join(dirname(__file__), '../fixtures/videos/'))


class FileLoaderImageTestCase(TestCase):
    def setUp(self):
        config = Config(
            FILE_LOADER_ROOT_PATH=IMAGE_STORAGE_PATH
        )
        self.ctx = Context(config=config)

    def load_file(self, file_name):
        return load(self.ctx, file_name, lambda x: x).result()

    def test_should_load_file(self):
        result = self.load_file('image.jpg')
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal(open(join(IMAGE_STORAGE_PATH, 'image.jpg')).read())
        expect(result.successful).to_be_true()

    def test_should_fail_when_inexistent_file(self):
        result = self.load_file('image_NOT.jpg')
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal(None)
        expect(result.successful).to_be_false()

    def test_should_fail_when_outside_root_path(self):
        result = self.load_file('../__init__.py')
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal(None)
        expect(result.successful).to_be_false()


class FileLoaderVideoTestCase(TestCase):
    def setUp(self):
        config = Config(
            FILE_LOADER_ROOT_PATH=VIDEO_STORAGE_PATH,
            FFMPEG_PATH = '/usr/bin/ffmpeg'
        )
        self.ctx = Context(config=config)

    def load_file(self, file_name):
        return load(self.ctx, file_name, lambda x: x).result()

    def test_should_load_jpeg(self):
        for filename in ('small.mp4', 'small.flv', 'small.3gp', 'small.ogv', 'small.webm'):
            result = self.load_file(filename)
            expect(result).to_be_instance_of(LoaderResult)
            expect(result.buffer[:2]).to_equal('\xFF\xD8') # look for jpeg header
            expect(result.successful).to_be_true()

    def test_should_fail_when_invalid_file(self):
        result = self.load_file('empty.mp4')
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal(None)
        expect(result.successful).to_be_false()

    def test_should_fail_when_ffmpeg_missing(self):
        config = Config(
            FILE_LOADER_ROOT_PATH=VIDEO_STORAGE_PATH,
            FFMPEG_PATH = '/tmp/not_there'
        )
        self.ctx = Context(config=config)
        result = self.load_file('small.mp4')
        expect(result).to_be_instance_of(LoaderResult)
        expect(result.buffer).to_equal(None)
        expect(result.successful).to_be_false()
