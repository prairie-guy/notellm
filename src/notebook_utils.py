"""Jupyter notebook cell utilities."""
import json
from pathlib import Path

def read_notebook(nb_path: str|Path) -> dict:
    """Read notebook JSON."""
    with open(nb_path, 'r') as f: return json.load(f)

def write_notebook(nb_path: str|Path, nb: dict) -> None:
    """Write notebook JSON."""
    with open(nb_path, 'w') as f: json.dump(nb, f, indent=1, ensure_ascii=False)

def get_cell_first_line(cell: dict, max_len: int = 60) -> str:
    """Extract first line of cell source."""
    src = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
    first = src.split('\n')[0].strip()
    return first[:max_len] + '...' if len(first) > max_len else first

def list_cells(nb_path: str|Path, show_empty: bool = False) -> None:
    """Display all cells."""
    nb = read_notebook(nb_path)
    print(f"\nNotebook: {Path(nb_path).name}")
    print("=" * 80)
    for i, cell in enumerate(nb['cells']):
        ctype = cell['cell_type']
        first = get_cell_first_line(cell)

        if not show_empty and not first and ctype == 'code': continue

        print(f"[{i:>2}] {ctype:8} \"{first}\"")

def find_cell(nb_path: str|Path, query: str, field: str = 'content') -> list[int]:
    """Search cells by content. Returns list of indices."""
    nb = read_notebook(nb_path)
    matches = []
    q = query.lower()

    for i, cell in enumerate(nb['cells']):
        src = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        if q in src.lower():
            matches.append(i)

    return matches

def get_section_cells(nb_path: str|Path, header: str) -> list[int]:
    """Find all cells under a markdown header until next same-level header.

    Header can be specified with or without # marks:
    - '### My Code' - Match exact level
    - 'My Code' - Match any level with this text
    """
    nb = read_notebook(nb_path)
    matches = []
    in_section = False
    section_level = None

    # Normalize header query
    header_stripped = header.lstrip('#').strip().lower()
    query_level = header.count('#') if header.startswith('#') else None  # None = any level

    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'markdown':
            src = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            first = src.split('\n')[0].strip()

            if first.startswith('#'):
                curr_level = len(first) - len(first.lstrip('#'))
                curr_text = first.lstrip('#').strip().lower()

                # Check if this is the target header
                if curr_text == header_stripped:
                    if query_level is None or curr_level == query_level:
                        in_section = True
                        section_level = curr_level  # Store the actual level for end-of-section detection
                        continue

                # Check if we've reached end of section
                if in_section and section_level is not None and curr_level <= section_level:
                    break

        if in_section:
            matches.append(i)

    return matches
