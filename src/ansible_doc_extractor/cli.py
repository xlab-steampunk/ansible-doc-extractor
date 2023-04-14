import argparse
import os.path
import re
import sys

try:
    from ansible.plugins.filter.core import to_yaml
    from ansible.plugins.loader import fragment_loader
    from ansible.utils import plugin_docs
    HAS_ANSIBLE = True
except ImportError:
    HAS_ANSIBLE = False

from jinja2 import Environment, PackageLoader
from jinja2.utils import pass_context

from antsibull_docs_parser import dom
from antsibull_docs_parser.parser import parse, Context
from antsibull_docs_parser.rst import to_rst_plain
from antsibull_docs_parser.md import to_md

import yaml


_supported_templates = ["rst", "md"]


def get_context(j2_context):
    params = {}
    plugin_collection = j2_context.get('collection')
    plugin_name = j2_context.get('module')
    plugin_type = j2_context.get('plugin_type')
    if plugin_collection is not None and plugin_name is not None and plugin_type is not None:
        params['current_plugin'] = dom.PluginIdentifier(fqcn=f"{plugin_collection}.{plugin_name}", type=plugin_type)
    return Context(**params)


@pass_context
def rst_ify(j2_context, text):
    return to_rst_plain(parse(text, get_context(j2_context)))


@pass_context
def md_ify(j2_context, text):
    return to_md(parse(text, get_context(j2_context)))


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

    returndocs = returndocs or {}
    if isinstance(returndocs, str):
        returndocs = yaml.safe_load(returndocs)

    doc.update(
        examples=examples,
        returndocs=returndocs,
        metadata=metadata,
    )

    doc["author"] = ensure_list(doc["author"])
    doc["description"] = ensure_list(doc["description"])
    convert_descriptions(doc.get("options", {}))
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


def get_default_template(env, markdown):
    if markdown:
        return env.get_template("module.md.j2")
    return env.get_template("module.rst.j2")


def get_template(custom_template, markdown):
    env = Environment(loader=PackageLoader("ansible_doc_extractor"), trim_blocks=True)
    env.filters["rst_ify"] = rst_ify
    env.filters["md_ify"] = md_ify
    env.filters["to_yaml"] = to_yaml

    if custom_template:
        template = env.from_string(custom_template.read())
        custom_template.close()
    else:
        template = get_default_template(env, markdown)

    if markdown:
        extension = "md"
    else:
        extension = "rst"

    return template, extension


def render_docs(output, modules, custom_template, markdown):
    template, extension = get_template(custom_template, markdown)
    for module in modules:
        render_module_docs(output, module, template, extension)


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
        help="""Custom Jinja2 template used to generate documentation.
        If option --markdown" is also listed, template must be md specific.
        """
    )
    parser.add_argument(
        "--markdown", action='store_true',
        help="""Generate markdown output files instead of rst (default)."""
    )
    return parser


def main():
    if not HAS_ANSIBLE:
        print(
            "Please install 'ansible' or 'ansible-base' or 'ansible-core'.",
            file=sys.stderr
        )
        sys.exit(1)

    args = create_argument_parser().parse_args()
    render_docs(args.output, args.module, args.template, args.markdown)
