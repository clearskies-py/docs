import re
import pathlib
from typing import Any
import tokenize
from collections import OrderedDict

import clearskies
from app import models
from .prepare_doc_space import prepare_doc_space

class DefaultBuilder:
    _attribute_cache: dict[str, str] = {}

    def __init__(self, branch, modules, classes, doc_root):
        self.modules = modules
        self.classes = classes
        self.doc_root = pathlib.Path(doc_root)
        self.title = branch["title"]
        self.source = branch["source"]
        self.nav_order = branch["nav_order"]
        self.class_list = branch["classes"]
        self._attribute_cache = {}

    def build(self):
        title_snake_case = clearskies.functional.string.title_case_to_snake_case(self.title).replace("_", "-")
        section_folder = self.doc_root / title_snake_case
        filename = "index"
        section_folder.mkdir(exist_ok=True)

        source_class = self.classes.find(f"import_path={self.source}")
        doc = self.build_header(self.title, filename, title_snake_case, None, self.nav_order, bool(self.class_list))
        doc += self.raw_docblock_to_md(source_class.doc)

        output_file = section_folder / f"{filename}.md"
        with output_file.open(mode="w") as doc_file:
            doc_file.write(doc)

        nav_order = 0
        for class_name in self.class_list:
            nav_order += 1
            source_class = self.classes.find(f"import_path={class_name}")
            title = source_class.name
            filename = clearskies.functional.string.title_case_to_snake_case(source_class.name).replace("_", "-")
            doc = self.build_header(source_class.name, filename, title_snake_case, self.title, nav_order, False)
            doc += self.raw_docblock_to_md(source_class.doc)

            # Find the documentation for all of our init args.
            arguments: dict[str, Any] = OrderedDict()
            for arg in source_class.init.args:
                if arg == "self":
                    continue
                arguments[arg] = {
                    "reqiured": arg not in source_class.init.kwargs,
                    "doc": "",
                }

            # for various reasons, it's easier to extract docs for all the arguments at once:
            docs = self.extract_attribute_docs(source_class, list(arguments.keys()))
            for (arg, doc) in docs.items():
                arguments[arg]["doc"] = doc

            for (arg, arg_data) in arguments.items():
                doc += "## " + clearskies.functional.string.snake_case_to_nice(arg) + "\n\n"
                doc += self.raw_docblock_to_md(arg_data["doc"].replace('"""', '')) + "\n\n"

            output_file = section_folder / f"{filename}.md"
            with output_file.open(mode="w") as doc_file:
                doc_file.write(doc)

            break

    def extract_attribute_docs(self, source_class, argument_names):
        """
        Fetch the docblocks for class arguments.

        Sadly, python doesn't support docblocks on class arguments.  I only discovered this after writing all
        the docblocs this way.  Still, I don't want to move my docblocs, because puttig them on arguments is
        legitimately the place where they make the most sense.  So, we have to use the python parsing capabilities
        built into python in order to extract them ourselves.  Very exciting... :cry:

        We substantially simplify this process (in a way that hopefully works) by setting stringent requirements
        for how our docblocks need to be defined.  The docblock must come before the argument and they must be
        at the top of the class.  In addition, when we are called, we are provided with a list of all argument
        names so that we are looking for a specific list of things rather than searching more generically for
        a series of documented arguments.  So, we're looking for a pattern of:

         1. tokenize.STRING
         2. tokenize.NEWLINE
         3. tokenize.NAME

        This will probably match a bunch of things, which is where our list of argument names comes in.
        Also, we'll only use the first combination of these things we find, which menas that attribute definitions
        must be at the top of the file. This will help us avoid getting confused by variable definitions with
        matching names later in the class.
        """
        # built in classes (which we will reach with our iterative approach) don't have a source file.
        if not source_class.source_file:
            return {}

        # we will iterate over base classes, and these often get re-used, so let's keep a cache
        if source_class.source_file in self._attribute_cache:
            return self._attribute_cache[source_class.source_file]

        doc_strings = {}
        with open(source_class.source_file, "r") as fp:
            # so this is both very simple and, hopefully, not prone to failure. The tokenization information that comes back from the
            # parser is surprisingly generic and vague.  However, we are looking for something
            last_string = ""
            for token_type, token_string, (srow, scol), (erow, ecol), line_content in tokenize.generate_tokens(fp.readline):
                if token_type == tokenize.STRING:
                    last_string = token_string
                    continue
                if token_type == tokenize.NEWLINE:
                    continue
                if token_type != tokenize.NAME:
                    last_string = ""
                    continue
                if not last_string or token_string not in argument_names:
                    continue
                doc_strings[token_string] = last_string

        # and let's repeat this for any base classes just to make sure we don't miss anything.  Often attributes are defined in
        # bases and we want to use those docs if we don't have them.
        for base_class in source_class.base_classes:
            doc_strings = {
                **self.extract_attribute_docs(base_class, argument_names),
                **doc_strings,
            }

        self._attribute_cache[source_class.source_file] = doc_strings
        return doc_strings

    def build_header(self, title, filename, section_name, parent, nav_order, has_children):
        permalink = "/docs/" + (f"{section_name}/" if section_name else "") + f"{filename}.html"
        header = f"""
---
layout: default
title: {title}
permalink: {permalink}
nav_order: {nav_order}
"""
        if parent:
            header += f"parent: {parent}\n"
        if has_children:
            header += "has_children: true\n"
        header += f"---\n\n# {title}\n\n"
        return header

    def raw_docblock_to_md(self, docblock):
        return re.sub(r"\n    ", "\n", docblock)

def build(modules: models.Module, classes: models.Class, config: str, project_root: str):
    doc_root = prepare_doc_space(project_root)

    for branch in config["tree"]:
        builder = DefaultBuilder(branch, modules, classes, doc_root)
        builder.build()
