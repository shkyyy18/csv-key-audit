import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import unittest
import tempfile
import json
from csv_key_audit import core


class KeyTests(unittest.TestCase):
    def test_composite(self):
        r = core.audit("a,b\nx,1\ny,1\nx,1\n", ["a", "b"])
        self.assertEqual(r["duplicate_groups"][0]["records"], [1, 3])
        self.assertEqual(r["distinct_keys"], 2)

    def test_values_not_exported(self):
        r = core.audit("id,name\nPRIVATE_MARKER,one\nPRIVATE_MARKER,two\n", ["id"])
        self.assertNotIn("PRIVATE_MARKER", json.dumps(r))

    def test_unicode(self):
        self.assertEqual(core.audit("编号\n中\n中\n", ["编号"])["finding_count"], 1)

    def test_exact_no_coercion(self):
        self.assertEqual(core.audit("id\n01\n1\n", ["id"])["distinct_keys"], 2)

    def test_empty_and_spaces(self):
        r = core.audit("id,label\n,x\n  ,y\n a ,z\n", ["id"])
        self.assertEqual(len(r["empty_key_records"]), 2)
        self.assertEqual(len(r["edge_whitespace"]), 2)

    def test_quoted_multiline(self):
        r = core.audit('id,note\na,"line1\nline2"\na,z\n', ["id"])
        self.assertEqual(r["duplicate_groups"][0]["records"], [1, 2])

    def test_invalid(self):
        for data, keys in [
            ("", ["a"]),
            ("a,a\n1,2", ["a"]),
            ("a\n1,2", ["a"]),
            ('a\n"bad', ["a"]),
            ("a\n1", ["b"]),
            ("a\n1", []),
            ("a\n1", ["a", "a"]),
        ]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                core.audit(data, keys)

    def test_header_only(self):
        self.assertEqual(core.audit("a\n", ["a"])["records"], 0)

    def test_run_utf8_bom(self):
        import argparse

        with tempfile.TemporaryDirectory() as t:
            p = Path(t, "input.csv")
            p.write_bytes(b"\xef\xbb\xbfid\r\na\r\na\r\n")
            self.assertEqual(
                core.run(argparse.Namespace(csv=str(p), key=["id"]))["finding_count"], 1
            )
