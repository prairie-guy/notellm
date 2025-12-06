"""Jupyter notebook cell identification utilities."""
import json
from pathlib import Path
from typing import Optional

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

def get_cell_name(cell: dict) -> Optional[str]:
    """Get cell name from metadata."""
    return cell.get('metadata', {}).get('name')

def get_cell_tags(cell: dict) -> list[str]:
    """Get cell tags from metadata."""
    return cell.get('metadata', {}).get('tags', [])

def list_cells(nb_path: str|Path, show_empty: bool = False) -> None:
    """Display all cells with enhanced context."""
    nb = read_notebook(nb_path)
    print(f"\nNotebook: {Path(nb_path).name}")
    print("=" * 80)
    for i, cell in enumerate(nb['cells']):
        ctype = cell['cell_type']
        first = get_cell_first_line(cell)
        name = get_cell_name(cell)
        tags = get_cell_tags(cell)

        if not show_empty and not first and ctype == 'code': continue

        name_str = f" ({name})" if name else ""
        tags_str = f" [tags: {', '.join(tags)}]" if tags else ""
        print(f"[{i:>2}] {ctype:8} \"{first}\"{name_str}{tags_str}")

def find_cell(nb_path: str|Path, query: str, field: str = 'all') -> list[int]:
    """Search cells by name, content, or tags. Returns list of indices."""
    nb = read_notebook(nb_path)
    matches = []
    q = query.lower()

    for i, cell in enumerate(nb['cells']):
        if field in ('all', 'name'):
            name = get_cell_name(cell)
            if name and q in name.lower():
                matches.append(i)
                continue

        if field in ('all', 'content'):
            src = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if q in src.lower():
                matches.append(i)
                continue

        if field in ('all', 'tags'):
            tags = get_cell_tags(cell)
            if any(q in t.lower() for t in tags):
                matches.append(i)

    return matches

def name_cell(nb_path: str|Path, index: int, name: str) -> None:
    """Add/update cell name in metadata."""
    nb = read_notebook(nb_path)
    if index < 0 or index >= len(nb['cells']):
        raise ValueError(f"Cell index {index} out of range (0-{len(nb['cells'])-1})")

    cell = nb['cells'][index]
    if 'metadata' not in cell: cell['metadata'] = {}
    cell['metadata']['name'] = name

    write_notebook(nb_path, nb)
    print(f"✓ Named cell [{index}] as '{name}'")

def tag_cell(nb_path: str|Path, index: int, tags: list[str]) -> None:
    """Add/update cell tags in metadata."""
    nb = read_notebook(nb_path)
    if index < 0 or index >= len(nb['cells']):
        raise ValueError(f"Cell index {index} out of range (0-{len(nb['cells'])-1})")

    cell = nb['cells'][index]
    if 'metadata' not in cell: cell['metadata'] = {}
    cell['metadata']['tags'] = tags

    write_notebook(nb_path, nb)
    print(f"✓ Tagged cell [{index}] with: {', '.join(tags)}")

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
