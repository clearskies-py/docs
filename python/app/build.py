import re
import pathlib

import clearskies
from app import models
from .prepare_doc_space import prepare_doc_space

class DefaultBuilder:
    def __init__(self, branch, modules, classes, doc_root):
        self.modules = modules
        self.classes = classes
        self.doc_root = pathlib.Path(doc_root)
        self.title = branch["title"]
        self.source = branch["source"]
        self.nav_order = branch["nav_order"]
        self.class_list = branch["classes"]

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
        return re.sub(r"\n +", "\n", docblock)

def build(modules: models.Module, classes: models.Class, config: str, project_root: str):
    doc_root = prepare_doc_space(project_root)

    for branch in config["tree"]:
        builder = DefaultBuilder(branch, modules, classes, doc_root)
        builder.build()
