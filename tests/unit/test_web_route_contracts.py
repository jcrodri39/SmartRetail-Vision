"""Static regression checks, NOT HTTP integration tests."""
import ast
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2] / 'app/web/routes/pages.py'
TREE = ast.parse(SOURCE.read_text(encoding='utf-8'))


def test_route_dependencies_are_explicitly_imported():
    imports = {alias.name for node in TREE.body if isinstance(node, ast.ImportFrom)
               for alias in node.names}
    assert {'live', 'report_data', 'make_csv', 'make_xlsx', 'MIME_XLSX'} <= imports


def test_upload_uses_bounded_chunked_reads():
    src = ast.get_source_segment(SOURCE.read_text(encoding='utf-8'),
                                 next(n for n in TREE.body if isinstance(n, ast.AsyncFunctionDef)
                                      and n.name == 'video_upload'))
    assert 'video.read(1024 * 1024)' in src
    assert 'HTTPException(413' in src
    assert 'path.unlink(missing_ok=True)' in src


def test_mutation_routes_handle_missing_records():
    text = SOURCE.read_text(encoding='utf-8')
    for name in ('video_toggle', 'zone_toggle', 'zone_delete', 'user_toggle', 'user_role'):
        node = next(n for n in TREE.body if isinstance(n, ast.FunctionDef) and n.name == name)
        src = ast.get_source_segment(text, node)
        assert 'HTTPException(404' in src, name
