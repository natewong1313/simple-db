import subprocess
import os
from typing import override
import unittest


def run_script(cmds: list[str]):
    p = subprocess.Popen(
        ["./main", "test.db"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    stdout, _ = p.communicate("\n".join(cmds) + "\n")
    return stdout.strip().splitlines()


class TestDatabase(unittest.TestCase):
    @override
    def setUp(self):
        os.remove("./test.db")

    def compare(self, results: list[str], expected: list[str]):
        for i, result in enumerate(results):
            self.assertEqual(result, expected[i])

    def test_insert_retrieve(self):
        results = run_script(["insert 1 user1 test@gmail.com", "select", ".exit"])
        self.compare(
            results,
            [
                "db > Executed.",
                "db > (1, user1, test@gmail.com)",
                "Executed.",
                "db >",
            ],
        )

    def test_table_full(self):
        # 100 pages * 14 rows
        cmds = [f"insert {i} user{i} user{i}@gmail.com" for i in range(1401)]
        results = run_script(cmds)
        self.assertEqual(results[-2], "db > Error: Table full.")

    def test_inserting_max_len_strings(self):
        username, email = "a" * 32, "a" * 255
        results = run_script([f"insert 1 {username} {email}", "select", ".exit"])
        self.compare(
            results,
            ["db > Executed.", f"db > (1, {username}, {email})", "Executed.", "db >"],
        )

    def test_long_strings(self):
        username, email = "a" * 33, "a" * 256
        results = run_script([f"insert 1 {username} {email}", "select", ".exit"])
        self.compare(results, ["db > String is too long.", "db > Executed.", "db >"])

    def test_negative_id(self):
        results = run_script(["insert -1 cstack foo@bar.com", "select", ".exit"])
        self.compare(results, ["db > ID must be positive.", "db > Executed.", "db >"])

    def test_persistance(self):
        results = run_script(["insert 1 user1 person@example.com", ".exit"])
        self.compare(results, ["db > Executed.", "db >"])
        results = run_script(["select", ".exit"])
        self.compare(
            results, ["db > (1, user1, person@example.com)", "Executed.", "db >"]
        )

    def test_constants(self):
        results = run_script([".constants", ".exit"])
        self.compare(
            results,
            [
                "db > Constants:",
                "ROW_SIZE: 293",
                "COMMON_NODE_HEADER_SIZE: 6",
                "LEAF_NODE_HEADER_SIZE: 10",
                "LEAF_NODE_CELL_SIZE: 297",
                "LEAF_NODE_SPACE_FOR_CELLS: 4086",
                "LEAF_NODE_MAX_CELLS: 13",
                "db >",
            ],
        )

    def test_btree(self):
        inserts = [f"insert {i} user{i} person{i}@example.com" for i in range(1, 4)]
        inserts.reverse()
        inserts.append(".btree")
        inserts.append(".exit")
        results = run_script(inserts)
        self.compare(
            results,
            [
                "db > Executed.",
                "db > Executed.",
                "db > Executed.",
                "db > Tree:",
                "leaf(size 3)",
                " - 0 : 1",
                " - 1 : 2",
                " - 2 : 3",
                "db >",
            ],
        )


if __name__ == "__main__":
    unittest.main()
