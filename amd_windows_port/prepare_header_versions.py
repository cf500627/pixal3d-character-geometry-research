"""Generate ROCm version headers from independently obtained original templates.

Packaging only: retain each template's original copyright/license and replace
the four CMake version placeholders using its recorded component version.
Neither source checkout is modified; choose a new output directory.
"""
import argparse
from pathlib import Path
import re


def render(component, source):
    cmake = (source / "CMakeLists.txt").read_text(encoding="utf-8-sig")
    found = re.search(r'set\(VERSION_STRING\s+"(\d+)\.(\d+)\.(\d+)"\)', cmake)
    if found is None or tuple(map(int, found.groups())) != (4, 2, 0):
        raise RuntimeError("Use the recorded ROCm header component release")
    major, minor, patch = map(int, found.groups())
    if component == "rocthrust":
        template = source / "thrust" / "rocthrust_version.hpp.in"
        relative = Path("thrust") / "rocthrust_version.hpp"
    else:
        template = source / "rocprim" / "include" / "rocprim" / "rocprim_version.hpp.in"
        relative = Path("rocprim") / "rocprim_version.hpp"
    text = template.read_text(encoding="utf-8-sig")
    replacements = {"NUMBER": major * 100000 + minor * 100 + patch,
                    "MAJOR": major, "MINOR": minor, "PATCH": patch}
    for suffix, value in replacements.items():
        token = "@" + component + "_VERSION_" + suffix + "@"
        if text.count(token) != 1:
            raise RuntimeError("Unexpected original version-header template")
        text = text.replace(token, str(value))
    if re.search(r"@[A-Za-z0-9_]+@", text):
        raise RuntimeError("Unresolved CMake template placeholder")
    if "Copyright" not in text:
        raise RuntimeError("Original copyright notice is required")
    return relative, text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rocthrust", required=True, type=Path)
    parser.add_argument("--rocprim", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source_a, source_b, output = args.rocthrust.resolve(), args.rocprim.resolve(), args.output.resolve()
    if output.exists() or output.is_relative_to(source_a) or output.is_relative_to(source_b):
        raise RuntimeError("Use a new output directory outside either source checkout")
    rendered = [render("rocthrust", source_a), render("rocprim", source_b)]
    for relative, text in rendered:
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
    print("Original ROCm version-header templates rendered; no compilation or GPU work.")


if __name__ == "__main__":
    main()
