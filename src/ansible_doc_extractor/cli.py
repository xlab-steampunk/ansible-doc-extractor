import argparse
import os.path
import re
import sys

from ansible.plugins.loader import fragment_loader
from ansible.utils import plugin_docs

from jinja2 import Environment, PackageLoader

import yaml


_supported_templates = ["rst", "md"]

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


def md_ify(text):
    t = _ITALIC.sub(r"*\1*", text)
    t = _BOLD.sub(r"**\1**", t)
    t = _MODULE.sub(r"[\1](\1_module)", t)
    t = _LINK.sub(r"[\1](\2)", t)
    t = _URL.sub(r"\1", t)
    t = _CONST.sub(r"`\1`", t)
    t = _RULER.sub(r"------------", t)
    return t


def ensure_list(value):
    if isinstance(value, list):
        return value
    return [value]


def convert_descriptions(data):
    for definition in data.values():
        if "description" in definition:
            definition["description"] = ensure_list(definition["description"])
        if "suboptions" in definition:
            convert_descriptions(definition["suboptions"])
        if "contains" in definition:
            convert_descriptions(definition["contains"])


def render_module_docs(output_folder, module, template, extension):
    print("Rendering {}".format(module))
    doc, examples, returndocs, metadata = plugin_docs.get_docstring(
        module, fragment_loader,
    )

    doc.update(
        examples=examples,
        returndocs=yaml.safe_load(returndocs) if returndocs else {},
        metadata=metadata,
    )

    doc["author"] = ensure_list(doc["author"])
    doc["description"] = ensure_list(doc["description"])
    convert_descriptions(doc["options"])
    convert_descriptions(doc["returndocs"])

    if "module" in doc:
        name = doc["module"]
        doc["plugin_type"] = "module"
    else:
        name = doc["name"].split(".")[-1]
        doc["module"] = name

    output_path = os.path.join(
        output_folder, doc["module"] + "." + extension
    )
    with open(output_path, "w") as fd:
        fd.write(template.render(doc))


def get_template(custom_template, markdown):
    env = Environment(loader=PackageLoader(__name__), trim_blocks=True)
    if custom_template:
        template = env.from_string(custom_template.read())
        custom_template.close()
        extension = "rst"
    elif markdown:
        env.filters["md_ify"] = md_ify
        template = env.get_template("module.md.j2")
        extension = "md"
    else:
        env.filters["rst_ify"] = rst_ify
        template = env.get_template("module.rst.j2")
        extension = "rst"
    return template, extension


def render_docs(output, modules, custom_template, markdown):
    template, extension = get_template(custom_template, markdown)
    for module in modules:
        render_module_docs(output, module, template, markdown)


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
        description="Ansible documentation extractor"
    )
    parser.add_argument(
        "output", help="Output folder",
    )
    parser.add_argument(
        "module", nargs="+",
        help="Module to extract documentation from",
    )
    parser.add_argument(
        "--template", type=argparse.FileType('r'),
        help="Custom Jinja2 template used to generate documentation."
    )
    parser.add_argument(
        "--markdown",
        help="Generate markdown output files instead of rst."
    )
    return parser


def main():
    args = create_argument_parser().parse_args()
    render_docs(args.output, args.module, args.template, args.markdown)