from __future__ import print_function
import argparse
import codecs
import importlib
import os
import jinja2
import shutil
import sys

import BaseHTTPServer
import SimpleHTTPServer


def generate():
    parser = argparse.ArgumentParser(description="Generate a static website")
    parser.add_argument("src_dir", metavar="SOURCE",
                        help="Source directory")
    parser.add_argument("dst_dir", metavar="DESTINATION",
                        help="Destination directory (will be created if necessary)")
    parser.add_argument("--serve", action="store_true",
                        help="Create an HTTP server to serve the content your website")
    parser.add_argument("--address", default="0.0.0.0:8000", help="Address on which the server should run")
    args = parser.parse_args()

    src_dir = os.path.abspath(args.src_dir)
    dst_dir = os.path.abspath(args.dst_dir)
    generator = Generator(src_dir, dst_dir)
    if args.serve:
        server = get_http_server(generator, args.address)
        ensure_path_exists(dst_dir)
        os.chdir(dst_dir)
        print("Serving {0} on http://{1}".format(dst_dir, args.address))
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    else:
        generator.run()

def get_http_server(generator, address):
    """
    Return an HTTP server that is ready to serve content.
    """
    HTTPRequestHandler.GENERATOR = generator
    host, port = address.split(":")
    return BaseHTTPServer.HTTPServer((host, int(port)), HTTPRequestHandler)


class HTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """
    HTTP request handler that re-generates the static website at every GET request.
    """

    GENERATOR = None

    def do_GET(self):
        if self.GENERATOR:
            self.GENERATOR.configure()
            self.GENERATOR.run()
        return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)


class Generator(object):
    """
    Static site generator.
    """
    BLOG_POSTS_PER_PAGE = 5

    def __init__(self, src_dir, dst_dir):
        """
        Arguments:
            src_dir (str): path to the source files of the website. This points
            to the directory that should contain pq.py.
            dst_dir (str): path to the destination directory. Content from this
            directory might be overwritten.
        """
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        self.home_template = None
        self.blog_post_template = None
        self.blog_posts = []
        self.pages = []
        self.static_directories = []
        self.jinja2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.src_dir)
        )
        self.configure()

    def configure(self):
        """
        Configure the generator using variables from the pq module in the
        source directory.
        """
        sys.path[:0] = [self.src_dir]
        pq = importlib.import_module("pq")
        sys.path.pop(0)

        self.home_template = getattr(pq, "HOME_TEMPLATE", "index.html")
        self.blog_post_template = getattr(pq, "BLOG_POST_TEMPLATE", "blog/post.html")

        self.static_directories = getattr(pq, "STATIC_DIRECTORIES", [])
        self.pages = getattr(pq, "PAGES", [])
        self.blog_posts = [
            BlogPost(self.src_dir, path, title, date)
            for path, title, date in getattr(pq, "BLOG_POSTS", [])
        ]

    def run(self):
        """
        Generate the static website.
        """
        self.generate_blog_posts()
        self.generate_pages()
        self.generate_static_directories()

    def generate_blog_posts(self):
        for start_index in range(0, len(self.blog_posts), self.BLOG_POSTS_PER_PAGE):
            page_index = start_index / self.BLOG_POSTS_PER_PAGE
            blog_posts = self.blog_posts[start_index:start_index + self.BLOG_POSTS_PER_PAGE]
            self.render_blog_post_page(blog_posts, page_index)
            for blog_post in blog_posts:
                self.render_blog_post(blog_post)

    def generate_pages(self):
        for page in self.pages:
            self.render(page, page)

    def generate_static_directories(self):
        for static_directory in self.static_directories:
            src_directory = os.path.join(self.src_dir, static_directory)
            dst_directory = os.path.join(self.dst_dir, static_directory)
            if os.path.exists(dst_directory):
                shutil.rmtree(dst_directory)
            shutil.copytree(src_directory, dst_directory)

    def render_blog_post(self, blog_post):
        self.render(self.blog_post_template, blog_post.url, blog_post=blog_post)

    def render_blog_post_page(self, blog_posts, page):
        url = "index.html" if page == 0 else "?page=%d" % (page + 1)
        self.render(self.home_template, url, blog_posts=blog_posts)

    def render(self, template_path, url, **params):
        if url.startswith("/"):
            url = url[1:]
        dst_path = os.path.join(self.dst_dir, url)
        ensure_dirname_exists(dst_path)
        template = self.jinja2_env.get_template(template_path)
        with codecs.open(dst_path, 'w', 'utf-8') as dst_file:
            dst_file.write(template.render(generator=self, **params))


class BlogPost(object):

    def __init__(self, root_directory, path, title, date):
        self.root_directory = root_directory
        self.path = path
        self.title = title
        self.date = date

    @property
    def url(self):
        return "/" + self.path

    @property
    def content(self):
        content_path = os.path.join(self.root_directory, self.path)
        return codecs.open(content_path, 'r', 'utf-8').read()

def ensure_dirname_exists(path):
    ensure_path_exists(os.path.dirname(path))

def ensure_path_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
