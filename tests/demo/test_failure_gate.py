"""A deliberately failing pytest used only for manual gate demonstrations."""


def test_release_gate_blocks_failed_tests():
    assert False, "Intentional test failure: release jobs must be skipped"
