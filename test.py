import subprocess
import unittest


def run_script(cmds: list[str]):
    p = subprocess.Popen(
        "./main",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    stdout, _ = p.communicate("\n".join(cmds) + "\n")
    return stdout.strip().splitlines()


class TestDatabase(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
