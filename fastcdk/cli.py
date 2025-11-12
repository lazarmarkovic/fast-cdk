# fastcdk/cli.py
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
import typer
from rich.console import Console
from rich.theme import Theme
from textx import TextXError

from fastcdk.fastcdk_error import FcdkError

console = Console(theme=Theme({"ok":"green","warn":"yellow","err":"bold red","info":"cyan"}))
app = typer.Typer(
  pretty_exceptions_enable=False,
  help="fastcdk — args-only CLI that reads input and hands it to your pipeline.",
)

def _print_textx_error(e: TextXError | FcdkError) -> None:
  # e.__str__ already formats as: "<file>:<line>:<col>: <msg> => '<fragment>'"
  # now that we pass file_name, it won't be "None" anymore.
  console.print(str(e), style="err")

@app.command("build")
def build(
  instances: List[Path] = typer.Argument(..., help=".fcdk instance files (allow many)"),
  defs_dir: List[Path] = typer.Option(
    [], "--defs-dir", metavar="DIR",
    help="Folders with custom .fcdk_def and .j2 files (repeatable)"
  ),
  out: Path = typer.Option(Path("./generated"), "--out", help="Output folder for generated code"),
  make_graph: bool = typer.Option(False, "--make-graph", help="Makes dependancy graph if flag is present"),
  dry_run: bool = typer.Option(False, "--dry-run", help="Only show parsed arguments as JSON"),
  debug: bool = typer.Option(False, "--debug", help="Enable Typer debug mode"),
):
  payload: Dict[str, Any] = {
    "instances": [str(p.resolve()) for p in instances],
    "defs_dir": [str(p.resolve()) for p in defs_dir],
    "out": str(out.resolve()),
    "make_graph": str(make_graph),
    "debug": debug,
  }

  if dry_run:
    console.print_json(data=payload)
    raise typer.Exit(0)

  from fastcdk import runner
  try:
      runner.run(instance_files=instances, custom_defs_dirs=defs_dir, out_dir=out, make_graph=make_graph)
  except TextXError as e:
      if debug:
          raise  # let you see the full stack when you want it
      _print_textx_error(e)
      raise typer.Exit(code=2)


if __name__ == "__main__":  # pragma: no cover
  app()
