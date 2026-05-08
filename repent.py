import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


_LATEX_ESCAPE_TABLE = str.maketrans({
    "\\": "\\textbackslash{}",
    "{": "\\{",
    "}": "\\}",
    "$": "\\$",
    "&": "\\&",
    "#": "\\#",
    "^": "\\^{}",
    "_": "\\_",
    "~": "\\textasciitilde{}",
    "%": "\\%",
})


def latex_escape(text):
    """Escape LaTeX special characters in a plain-text string."""
    if not isinstance(text, str):
        return text
    return text.translate(_LATEX_ESCAPE_TABLE)


def dump_structure(template_path, output_file=None):
    """Print the template structure.json to stdout or write to output_file."""
    structure_path = template_path.parent / "structure.json"
    if not structure_path.exists():
        print(f"Error: structure.json not found at {structure_path}", file=sys.stderr)
        sys.exit(1)

    with open(structure_path, "r", encoding="utf-8") as f:
        content = f.read()

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[*] Structure written to {output_file}")
    else:
        print(content)


def validate_data(data):
    """Basic validation of the input JSON structure."""
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")

    if "title" not in data:
        print("Warning: 'title' field is missing from input JSON", file=sys.stderr)

    if "chapter_list" not in data:
        raise ValueError("JSON must contain a 'chapter_list' array")

    if not isinstance(data["chapter_list"], list):
        raise ValueError("'chapter_list' must be an array")


def main():
    parser = argparse.ArgumentParser(description="Generate LaTeX reports from JSON.")
    parser.add_argument("-j", "--json", help="Path to the input JSON file")
    parser.add_argument("-o", "--output", help="Path for the output PDF file")
    parser.add_argument("-t", "--template", default="main.tex", help="Path to the Jinja LaTeX template")
    parser.add_argument(
        "--dump-structure",
        action="store_true",
        help="Dump the template structure.json to stdout (use -o to write to file instead)",
    )
    args = parser.parse_args()

    # Resolve template path early so --dump-structure can use it
    template_path = Path(args.template).resolve()
    script_dir = template_path.parent

    # --dump-structure: print the structure skeleton and exit
    if args.dump_structure:
        dump_structure(template_path, args.output)
        return

    # Normal operation: both -j and -o are required
    if not args.json:
        parser.error("-j/--json is required (unless --dump-structure is used)")
    if not args.output:
        parser.error("-o/--output is required (unless --dump-structure is used)")

    # Check that pdflatex is available
    if not shutil.which("pdflatex"):
        print("Error: pdflatex not found in PATH. Please install a LaTeX distribution.", file=sys.stderr)
        sys.exit(1)

    json_path = Path(args.json).resolve()
    output_pdf_path = Path(args.output).resolve()
    output_dir = output_pdf_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    output_tex_path = output_dir / f"{output_pdf_path.stem}.tex"

    # Load and validate JSON
    if not json_path.exists():
        print(f"Error: JSON file not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {json_path}: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        validate_data(data)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Render Jinja2 template
    env = Environment(
        loader=FileSystemLoader(str(script_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["latex_escape"] = latex_escape
    template = env.get_template(template_path.name)

    try:
        latex_content = template.render(data)
    except Exception as e:
        print(f"Error: template rendering failed: {e}", file=sys.stderr)
        sys.exit(1)

    with open(output_tex_path, "w", encoding="utf-8") as f:
        f.write(latex_content)

    print(f"[*] Generated LaTeX source at {output_tex_path}")

    # Set up TEXINPUTS so LaTeX can find files in both the output and template dirs
    envv = os.environ.copy()
    texinputs = f"{output_dir}:{script_dir}"
    if "TEXINPUTS" in envv:
        texinputs += ":" + envv["TEXINPUTS"]
    envv["TEXINPUTS"] = texinputs + ":"

    # Compile with pdflatex (two passes for TOC and cross-references)
    compile_cmd = [
        "pdflatex",
        "-interaction=nonstopmode",
        f"-output-directory={output_dir}",
        str(output_tex_path),
    ]

    print("[*] Compiling PDF...")
    for i in range(2):
        print(f"[*] pdflatex pass {i + 1}/2...")
        result = subprocess.run(compile_cmd, cwd=str(script_dir), capture_output=True, text=True, env=envv)
        if result.returncode != 0:
            print(f"[!] pdflatex pass {i + 1} exited with code {result.returncode}", file=sys.stderr)
            # Surface the first few LaTeX errors from stderr
            for line in result.stderr.splitlines():
                if line.startswith("!"):
                    print(f"    {line}", file=sys.stderr)

    if output_pdf_path.exists():
        print(f"[+] Success! Report generated at {output_pdf_path}")
    else:
        print(f"[!] Error: PDF was not generated at {output_pdf_path}.", file=sys.stderr)
        print(f"[!] Check the LaTeX log at {output_dir / f'{output_pdf_path.stem}.log'}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
