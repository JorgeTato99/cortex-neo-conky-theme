"""Application grouping must precede the top-five cutoff."""

import unittest
from types import SimpleNamespace

from cortex_neo.processes import read_processes


class ProcessTest(unittest.TestCase):
    def test_group_before_ranking_and_keep_cpu_independent(self):
        def process(pid, name, rss, cpu):
            return SimpleNamespace(
                info={
                    "pid": pid,
                    "name": name,
                    "cpu_percent": cpu,
                    "memory_info": SimpleNamespace(rss=rss),
                }
            )

        values = [process(1, "code", 400, 1), process(2, "code", 400, 2)]
        values += [process(n + 3, "app" + str(n), 700 - n, 10 + n) for n in range(6)]
        cpu, memory = read_processes(values)
        self.assertEqual(memory[0], {"name": "code", "rss": 800, "processes": 2})
        self.assertEqual(len(memory), 5)
        self.assertEqual(cpu[0]["name"], "app5")
        self.assertEqual(len(cpu), 5)


if __name__ == "__main__":
    unittest.main()
