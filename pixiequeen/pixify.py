#! /usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import mako.lookup
import mako.template

class Paths(object):

    _instance = None

    def __init__(self, source_path, dst_path):
        self._source_path = source_path
        self._dst_path = dst_path

    @classmethod
    def init(cls, source_path, dst_path):
        cls._instance = cls(source_path, dst_path)

    @classmethod
    def source_path(cls):
        return cls._instance._source_path

    @classmethod
    def dst_path(cls):
        return cls._instance._dst_path

def main():
    parser = argparse.ArgumentParser(description="Static website creator")
    parser.add_argument("source", help="Path to source files")
    parser.add_argument("dst", help="Destination folder; it will be created if it does not exist.")
    args = parser.parse_args()

    Paths.init(args.source, args.dst)
    template_lookup = mako.lookup.TemplateLookup(directories=[Paths.source_path()])
    for file_path in iter_renderable_files(Paths.source_path()):
        template = mako.template.Template(filename=file_path, lookup=template_lookup)
        dst_file_path = render_path(file_path, Paths.source_path(), Paths.dst_path())
        ensure_directory_exists(dst_file_path)
        with open(dst_file_path, 'w') as dst_file:
            dst_file.write(template.render())

def iter_renderable_files(root_dir):
    for (dirpath, _dirnames, filenames) in os.walk(root_dir):
        for filename in filenames:
            if filename.startswith('_'):
                continue
            extension = os.path.splitext(filename)[1]
            if extension == '.swp':
                continue
            yield os.path.join(dirpath, filename)

def render_path(file_path, source_path, dst_path):
    return os.path.join(dst_path, os.path.relpath(file_path, source_path))

def ensure_directory_exists(path):
    dir_path = os.path.dirname(path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def iter_blog_posts(posts_sub_directory):
    root_dir = os.path.join(Paths.source_path(), posts_sub_directory)
    for post_path in iter_renderable_files(root_dir):
        post_relative_path = os.path.relpath(post_path, Paths.source_path())
        post_relative_path = "/" + post_relative_path
        print post_relative_path
        yield post_relative_path

def custom_module(context):
    import ipdb; ipdb.set_trace()
    return ''

if __name__ == "__main__":
    main()
