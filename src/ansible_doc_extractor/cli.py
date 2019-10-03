import argparse
import collections
import functools
import os.path
import re
import sys

from ansible.plugins.loader import fragment_loader
from ansible.utils import plugin_docs

from jinja2 import Environment, PackageLoader
from jinja2.runtime import Undefined

import yaml


# The rst_ify filter has been shamelessly stolen from the Ansible helpers in
# hacking subfolder. So all of the credit goes to the Ansible authors.

_ITALIC = re.compile(r"I\(([^)]+)\)")
_BOLD = re.compile(r"B\(([^)]+)\)")
_MODULE = re.compile(r"M\(([^)]+)\)")
_URL = re.compile(r"U\(([^)]+)\)")
_LINK = re.compile(r"L\(([^)]+), *([^)]+)\)")
_CONST = re.compile(r"C\(([^)]+)\)")
_RULER = re.compile(r"HORIZONTALLINE")


def rst_ify(text):
    t = _ITALIC.sub(r"*\1*", text)
    t = _BOLD.sub(r"**\1**", t)
    t = _MODULE.sub(r":ref:`\1 <\1_module>`", t)
    t = _LINK.sub(r"`\1 <\2>`_", t)
    t = _URL.sub(r"\1", t)
    t = _CONST.sub(r"``\1``", t)
    t = _RULER.sub(r"------------", t)

    return t


def sort_options(options):
    options = collections.OrderedDict(sorted(
        options.items(), key=lambda x: (not x[1].get("required", False), x[0])
    ))
    for v in options.values():
        if "suboptions" in v:
            v["suboptions"] = sort_options(v["suboptions"])
    return options


def render_module_docs(output_folder, module, template):
    print("Rendering {}".format(module))
    doc, examples, returndocs, metadata = plugin_docs.get_docstring(
        module, fragment_loader,
    )
    doc["options"] = sort_options(doc["options"])
    doc.update(
        examples=examples,
        returndocs=yaml.safe_load(returndocs),
        metadata=metadata,
    )

    module_rst_path = os.path.join(output_folder, doc["module"] + ".rst")
    with open(module_rst_path, "w") as fd:
        fd.write(template.render(doc))


def render_docs(output, modules):
    env = Environment(loader=PackageLoader(__name__), trim_blocks=True)
    env.filters["rst_ify"] = rst_ify
    template = env.get_template("module.rst.j2")

    for module in modules:
        render_module_docs(output, module, template)


class ArgParser(argparse.ArgumentParser):
    """
    Argument parser that displays help on error
    """

    def error(self, message):
        sys.stderr.write("error: {}\n".format(message))
        self.print_help()
        sys.exit(2)


def create_argument_parser():
    parser = ArgParser(
        description="Ansible documentation extractor",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "output", help="Output folder",
    )
    parser.add_argument(
        "module", nargs="+",
        help="Module to extract documentation from",
    )
    return parser


def main():
    args = create_argument_parser().parse_args()
    render_docs(args.output, args.module)
