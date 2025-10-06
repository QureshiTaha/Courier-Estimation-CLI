import io
import sys
from pathlib import Path
from src import cli

def test_cli_end_to_end_with_file(tmp_path: Path):
    # Valid full input (with vehicles)
    content = """100 3
PKG1 10 100 OFR003
PKG2 5 10 NA
PKG3 50 30 OFR001
1 70 200
"""
    f = tmp_path / "in.txt"
    f.write_text(content, encoding="utf-8")

    sys.argv = ["src.cli", str(f)]
    buf = io.StringIO()
    old_stdout = sys.stdout
    try:
        sys.stdout = buf
        rc = cli.main(sys.argv)
    finally:
        sys.stdout = old_stdout
    out = buf.getvalue().strip().splitlines()

    assert rc == 0
    assert len(out) == 3
    # Basic sanity: package ids present, 4 space-separated columns
    assert all(line.split()[0].startswith("PKG") and len(line.split()) == 4 for line in out)

def test_cli_reads_from_stdin(monkeypatch):
    content = """100 1
PKG1 50 30 OFR001
1 70 200
"""
    monkeypatch.setattr("sys.stdin", io.StringIO(content))
    sys.argv = ["src.cli", "-"]

    buf = io.StringIO()
    old_stdout = sys.stdout
    try:
        sys.stdout = buf
        rc = cli.main(sys.argv)
    finally:
        sys.stdout = old_stdout

    assert rc == 0
    assert "PKG1" in buf.getvalue()

def test_cli_input_error_header(monkeypatch):
    # Triggers parse error -> main returns 3
    monkeypatch.setattr("sys.stdin", io.StringIO("oops"))
    sys.argv = ["src.cli", "-"]
    rc = cli.main(sys.argv)
    assert rc == 3

def test_cli_validation_error_too_heavy(monkeypatch):
    # Package heavier than any vehicle -> validation error -> returns 4
    content = """100 1
PKG1 999 10 NA
1 70 200
"""
    monkeypatch.setattr("sys.stdin", io.StringIO(content))
    sys.argv = ["src.cli", "-"]
    rc = cli.main(sys.argv)
    assert rc == 4

def test_cli_shows_usage_when_no_args(monkeypatch):
    sys.argv = ["src.cli"]  # no input arg
    buf = io.StringIO()
    old_stdout = sys.stdout
    try:
        sys.stdout = buf
        rc = cli.main(sys.argv)
    finally:
        sys.stdout = old_stdout
    assert rc == 1
    assert "Usage:" in buf.getvalue()
    
def test_cli_file_not_found(monkeypatch, tmp_path: Path):
    missing = tmp_path / "nope.txt"
    sys.argv = ["src.cli", str(missing)]
    buf = io.StringIO()
    old_stdout = sys.stdout
    try:
        sys.stdout = buf
        rc = cli.main(sys.argv)
    finally:
        sys.stdout = old_stdout
    assert rc == 2
    assert "not found" in buf.getvalue()