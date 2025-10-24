# fastcdk/cli.py
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
import typer
from rich.console import Console
from rich.theme import Theme

console = Console(theme=Theme({"ok":"green","warn":"yellow","err":"bold red","info":"cyan"}))
app = typer.Typer(add_completion=False, help="fastcdk — args-only CLI that reads input and hands it to your pipeline.")

@app.command("build")
def build(
  instances: List[Path] = typer.Argument(..., help=".fcdk instance files (allow many)"),
  defs_dir: List[Path] = typer.Option(
    [], "--defs-dir", metavar="DIR",
    help="Folders with custom .fcdk_def and .j2 files (repeatable)"
  ),
  out: Path = typer.Option(Path("./generated"), "--out", help="Output folder for generated code"),
  dry_run: bool = typer.Option(False, "--dry-run", help="Only show parsed arguments as JSON"),
):
  payload: Dict[str, Any] = {
    "instances": [str(p.resolve()) for p in instances],
    "defs_dir": [str(p.resolve()) for p in defs_dir],
    "out": str(out.resolve()),
  }

  if dry_run:
    console.print_json(data=payload)
    raise typer.Exit(0)

  try:
    from fastcdk import runner
    runner.run(instance_files=instances, custom_defs_dirs=defs_dir, out_dir=out)  
  except ImportError:
    console.print("Error while running DSL with those args: ")
    console.print_json(data=payload)

if __name__ == "__main__":  # pragma: no cover
  app()
