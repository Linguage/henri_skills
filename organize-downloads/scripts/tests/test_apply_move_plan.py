import tempfile
import unittest
from pathlib import Path
import importlib.util

SCRIPT = Path(__file__).resolve().parents[1] / "apply_move_plan.py"
if not SCRIPT.exists():
    SCRIPT = Path("/tmp/apply_move_plan.py")
spec = importlib.util.spec_from_file_location("apply_move_plan", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ApplyMovePlanTests(unittest.TestCase):
    def test_dry_run_and_execute(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            (root / "a.txt").write_text("x")
            checked = module.preflight(
                root, root, [{"source": "a.txt", "target": "sub/b.txt"}]
            )
            self.assertTrue((root / "a.txt").exists())
            result = module.execute(checked, root / "log.json", root, root)
            self.assertEqual(result["status"], "complete")
            self.assertEqual((root / "sub/b.txt").read_text(), "x")

    def test_cross_root_move(self):
        with tempfile.TemporaryDirectory() as value:
            base = Path(value)
            source_root = base / "Downloads"
            target_root = base / "Documents"
            source_root.mkdir()
            (source_root / "book.pdf").write_text("book")
            checked = module.preflight(
                source_root,
                target_root,
                [{"source": "book.pdf", "target": "书籍/数学与物理/book.pdf"}],
            )
            result = module.execute(
                checked, base / "log.json", source_root, target_root
            )
            self.assertEqual(result["source_root"], str(source_root))
            self.assertEqual(result["target_root"], str(target_root))
            self.assertFalse((source_root / "book.pdf").exists())
            self.assertEqual(
                (target_root / "书籍/数学与物理/book.pdf").read_text(), "book"
            )

    def test_rejects_escape_and_overwrite(self):
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            (root / "a.txt").write_text("a")
            (root / "b.txt").write_text("b")
            with self.assertRaises(ValueError):
                module.preflight(
                    root, root, [{"source": "a.txt", "target": "../x.txt"}]
                )
            with self.assertRaises(FileExistsError):
                module.preflight(
                    root, root, [{"source": "a.txt", "target": "b.txt"}]
                )


if __name__ == "__main__":
    unittest.main()
