import argparse
import json
import os
import subprocess
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

def main():
    parser = argparse.ArgumentParser(description="Generate LaTeX reports from JSON.")
    parser.add_argument("-j", "--json", required=True, help="Path to the input JSON file")
    parser.add_argument("-o", "--output", required=True, help="Path for the output PDF file")
    parser.add_argument("-t", "--template", default="main.tex", help="Path to the Jinja LaTeX template")
    args = parser.parse_args()

    # Resolve paths
    json_path = Path(args.json).resolve()
    output_pdf_path = Path(args.output).resolve()
    output_dir = output_pdf_path.parent
    output_tex_path = output_dir / f"{output_pdf_path.stem}.tex"
    script_dir = Path(args.template).parent

    # Load JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Setup Jinja environment
    env = Environment(
        loader=FileSystemLoader(os.path.dirname(os.path.abspath(args.template))),
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = env.get_template(os.path.basename(args.template))

    # Render LaTeX content
    latex_content = template.render(data)

    # Write the .tex file
    with open(output_tex_path, 'w', encoding='utf-8') as f:
        f.write(latex_content)

    print(f"[*] Generated LaTeX source at {output_tex_path}")

    # Compile with pdflatex
    print("[*] Compiling PDF...")
    compile_cmd = [
        "pdflatex",
        "-interaction=nonstopmode",
        f"-output-directory={output_dir}",
        str(output_tex_path)
    ]
    
    # Run pdflatex (often requires two passes for TOC and references)
    subprocess.run(compile_cmd, cwd=script_dir, check=False)
    subprocess.run(compile_cmd, cwd=script_dir, check=False)

    print(f"[+] Success! Report generated at {output_pdf_path}")

if __name__ == "__main__":
    main()
