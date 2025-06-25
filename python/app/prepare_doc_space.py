import shutil
import pathlib

def prepare_doc_space(project_root):
    project_path = pathlib.Path(project_root)
    build_path = project_path / "build"
    doc_path = build_path / "docs"
    doc_path.mkdir(parents=True, exist_ok=True)

    jekyll_path = project_path / "jekyll"
    for file in jekyll_path.glob("*"):
        if not file.is_file():
            continue

        shutil.copy2(str(file), str(build_path / file.name))

    return str(doc_path)
