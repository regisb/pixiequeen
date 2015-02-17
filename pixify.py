#! /usr/bin/env python
import argparse
import os
from pixiequeen import Pixifier

if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    parser = argparse.ArgumentParser(description="Generate a static website")
    parser.add_argument("src_dir", metavar="SOURCE",
                        help="Source directory")
    parser.add_argument("dst_dir", metavar="DESTINATION",
                        help="Destination directory (will be created if necessary)")
    args = parser.parse_args()

    pixifier = Pixifier(args.src_dir, args.dst_dir)

    pixifier.set_base_template("_base.html")
    pixifier.set_home_template("index.html")
    pixifier.set_blog_post_template("blog/_post.html")
    pixifier.add_static_directory("static")

    pixifier.add_blog_post("blog/20150130/hello-world.html", "Hello World!", "2015-01-30")

    pixifier.generate()
