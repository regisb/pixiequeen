import os
import jinja2
import shutil


class Pixifier(object):
    BLOG_POSTS_PER_PAGE = 5

    def __init__(self, src_dir, dst_dir):
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        self.base_template = None # useful ?
        self.home_template = None
        self.blog_post_template = None
        self.blog_posts = []
        self.static_directories = []
        self.jinja2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.src_dir)
        )

    def set_base_template(self, path):
        self.base_template = path

    def set_home_template(self, path):
        self.home_template = path

    def set_blog_post_template(self, path):
        self.blog_post_template = path

    def add_blog_post(self, path, title, date):
        self.blog_posts.append(BlogPost(self.src_dir, path, title, date))

    def add_static_directory(self, path):
        self.static_directories.append(path)

    def generate(self):
        self.generate_blog_posts()
        self.generate_static_directories()

    def generate_blog_posts(self):
        for page in range(0, len(self.blog_posts), self.BLOG_POSTS_PER_PAGE):
            blog_posts = self.blog_posts[page:page + self.BLOG_POSTS_PER_PAGE]
            self.render_blog_post_page(blog_posts, page)
            for blog_post in blog_posts:
                self.render_blog_post(blog_post)

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
        with open(dst_path, 'w') as dst_file:
            dst_file.write(template.render(**params))


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
        return open(os.path.join(self.root_directory, self.path)).read()

def ensure_dirname_exists(path):
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
