import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path

import markdown
import tomli
from bs4 import BeautifulSoup


def parse_args():
    parser = argparse.ArgumentParser(description="Tool to make capstone course from other formats")

    parser.add_argument("-f", "--format", help="The source format to convert from", required=True)
    parser.add_argument("-o", "--output", help="The output directory", default="capstone-course")
    parser.add_argument("directory", help="The directory to convert from")

    return parser.parse_args()


def from_mdbook(directory, output):
    book_conf = tomli.loads((Path(directory) / "book.toml").read_text())["book"]
    src = book_conf.get("src", "src")
    title = book_conf["title"]
    name = slugify(title)

    src_dir = Path(directory) / src
    output_dir = Path(output)

    if output_dir.is_dir() and not list(output_dir.iterdir()) == []:
        raise ValueError(f"Output directory exists and is not empty: {output_dir}")

    modules = []

    summary_md_text = (src_dir / "SUMMARY.md").read_text()
    summary_html = markdown.markdown(
        summary_md_text,
        tab_length=infer_tab_length(summary_md_text),
    )
    soup = BeautifulSoup(summary_html, "html.parser")
    module_soups = [li for module_group in soup.find_all("ul", recursive=False) for li in module_group.find_all("li", recursive=False)]

    for (i, module_soup) in enumerate(module_soups, start=1):
        if (module_with_link := module_soup.find("a")):
            module_title = module_with_link.contents[0].string
            assert module_title is not None  # sanity check
            module_link = module_with_link.attrs["href"]
            module = dict(
                name=slugify(module_title),
                title=module_title,
                lessons=[
                    dict(name=slugify(module_title), title=module_title, path=src_dir / module_link),
                ],
            )
        else:
            module_title = f"Module {i}"
            module = dict(name=slugify(module_title), title=module_title, lessons=[])

        # elements of sublists inside module soup, and their sublists, etc.
        for lesson_soup in module_soup.find_all("li"):
            # only add lessons with links
            if (lesson_with_link := lesson_soup.contents[0]).name == "a":
                lesson_title = lesson_with_link.contents[0].string
                assert lesson_title is not None
                lesson_link = lesson_with_link.attrs["href"]
                module["lessons"].append(
                    dict(name=slugify(lesson_title), title=lesson_title, path=src_dir / lesson_link)
                )

        modules.append(module)

    # write to tempdir first. then rename it to output_dir if that succeeds
    with tempfile.TemporaryDirectory() as tmp:
        course_path = Path(tmp)

        package_metadata = dict(kind="course", version="0.1", name=name, title=title)
        (course_path / "metadata.json").write_text(json.dumps(package_metadata))

        contents_path = course_path / "contents"
        contents_path.mkdir()

        lessons_path = contents_path / "lessons"
        lessons_path.mkdir()

        for module in modules:
            new_module_path = lessons_path / module["name"]
            new_module_path.mkdir()
            for lesson in module["lessons"]:
                new_lesson_path = new_module_path / f"{lesson['name']}.html"
                new_lesson_path.write_text(md_to_html(lesson["path"].read_text()))
                lesson["path"] = str(new_lesson_path.relative_to(contents_path))

        course_metadata = dict(name=name, title=title, description=title, modules=modules)
        (contents_path / "course.json").write_text(json.dumps(course_metadata))

        shutil.move(course_path, output_dir)

    print(json.dumps(course_metadata, indent=4))

def slugify(s):
    not_allowed_chars = re.compile(r"[^a-zA-Z0-9-]")
    return not_allowed_chars.sub("", s.lower().replace(" ", "-"))


def md_to_html(text):
    return markdown.markdown(text, tab_length=4, extensions=["extra", "codehilite"])


def infer_tab_length(text):
    """infer tab length, either 2 or 4 (default fallback: 2)"""
    for line in text.splitlines():
        if line.startswith("    "):
            return 4
    return 2


def main():
    args = parse_args()
    match args.format:
        case "mdbook":
            from_mdbook(args.directory, args.output)
        case _:
            raise ValueError(f"Unknown format: {args.format}")


if __name__ == "__main__":
    main()
