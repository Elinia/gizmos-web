import unittest

if True:
    import sys
    import os
    sys.path.append(os.path.realpath('..'))
    from env.find_build_solutions import find_build_solutions
    from env.gizmos_utils import init_energy_num
    from env.gizmos_pool import converter_any_level2, converter_level1, converter_double_level3, converter_any_level3, converter_double_level2


class TestStringMethods(unittest.TestCase):
    def test_basic_without_converter(self):
        solutions = find_build_solutions(
            'red', 1, init_energy_num({'red': 1}), [], False)
        self.assertEqual(len(solutions), 1)
        solutions = find_build_solutions(
            'red', 1, init_energy_num({'red': 2}), [], False)
        self.assertEqual(len(solutions), 1)

    def test_basic_double_converter(self):
        g1 = converter_double_level2('red', 'blue')
        solutions = find_build_solutions(
            'blue',
            3,
            init_energy_num({'blue': 2}),
            [g1],
            False
        )
        self.assertEqual(len(solutions), 1)

    def test_basic_double_and_any_converter(self):
        g1 = converter_any_level2('red', 'blue')
        g2 = converter_double_level2('red', 'blue')
        solutions = find_build_solutions(
            'yellow',
            2,
            init_energy_num({'blue': 1}),
            [g1, g2],
            False
        )
        self.assertEqual(len(solutions), 1)
        energy_num = solutions[0]['energy_num']
        gizmos = solutions[0]['gizmos']
        self.assertEqual(energy_num, init_energy_num({'blue': 1}))
        self.assertSetEqual(set(gizmos), set([g1, g2]))

    def test_double_level3_and_any_converter(self):
        g1 = converter_level1('red', 'yellow')
        g2 = converter_double_level3('red', ['blue', 'yellow'])
        solutions = find_build_solutions(
            'blue',
            6,
            init_energy_num({'blue': 4, 'yellow': 1}),
            [g1, g2],
            False
        )
        self.assertEqual(len(solutions), 1)
        energy_num = solutions[0]['energy_num']
        gizmos = solutions[0]['gizmos']
        self.assertEqual(energy_num, init_energy_num({'blue': 4, 'yellow': 1}))
        self.assertSetEqual(set(gizmos), set([g1, g2]))

    def test_any_to_any_and_formulae_length_over_than_1(self):
        g1 = converter_level1('red', 'blue')
        g2 = converter_any_level2('red', 'red')
        g3 = converter_any_level3('red')
        solutions = find_build_solutions(
            'black',
            6,
            init_energy_num({'red': 2, 'blue': 2, 'black': 2}),
            [g1, g2, g3],
            False
        )
        self.assertEqual(len(solutions), 1)
        energy_num = solutions[0]['energy_num']
        gizmos = solutions[0]['gizmos']
        self.assertEqual(energy_num, init_energy_num(
            {'red': 2, 'black': 2, 'blue': 2}))
        self.assertSetEqual(set(gizmos), set([g1, g2, g3]))

    def test_build_any_with_any(self):
        g1 = converter_level1('red', 'blue')
        g2 = converter_any_level2('red', 'red')
        g3 = converter_any_level3('red')
        solutions = find_build_solutions(
            'any',
            6,
            init_energy_num({'red': 2, 'blue': 2, 'black': 2}),
            [g1, g2, g3],
            False
        )
        self.assertEqual(len(solutions), 1)
        energy_num = solutions[0]['energy_num']
        gizmos = solutions[0]['gizmos']
        self.assertEqual(energy_num, init_energy_num(
            {'red': 2, 'black': 2, 'blue': 2}))
        self.assertSetEqual(set(gizmos), set([]))

    def test_build_any_with_double(self):
        g1 = converter_double_level2('red', 'red')
        g2 = converter_double_level3('red', ['blue', 'yellow'])
        solutions = find_build_solutions(
            'any',
            6,
            init_energy_num({'red': 1, 'blue': 1, 'yellow': 2}),
            [g1, g2],
            False
        )
        self.assertEqual(len(solutions), 2)
        solution = next(s for s in solutions if s['energy_num']['yellow'] == 1)
        energy_num = solution['energy_num']
        gizmos = solution['gizmos']
        self.assertEqual(energy_num, init_energy_num(
            {'red': 1, 'yellow': 1, 'blue': 1}))
        self.assertSetEqual(set(gizmos), set([g1, g2]))

    def test_complex(self):
        g1 = converter_any_level3('red')
        g2 = converter_double_level3('red', ['blue', 'yellow'])
        g3 = converter_any_level2('red', 'blue')
        g4 = converter_level1('red', 'yellow')
        g5 = converter_any_level2('red', 'black')

        solutions = find_build_solutions(
            'black',
            5,
            init_energy_num({'black': 3}),
            [g1, g2, g3, g4, g5],
            False
        )
        self.assertEqual(len(solutions), 1)

        solutions2 = find_build_solutions(
            'red',
            5,
            init_energy_num({'red': 1, 'black': 2}),
            [g1, g2, g3, g4, g5],
            False
        )
        self.assertEqual(len(solutions2), 1)

        solutions3 = find_build_solutions(
            'black',
            5,
            init_energy_num({'black': 2, 'red': 1}),
            [g1, g2, g3, g4, g5],
            False
        )
        self.assertEqual(len(solutions3), 0)

    def test_build_any(self):
        solutions = find_build_solutions(
            'any',
            7,
            init_energy_num({'red': 5, 'blue': 1, 'black': 1}),
            [],
            False
        )
        self.assertEqual(len(solutions), 1)

    def test_bug_case_1(self):
        g1 = converter_any_level2('yellow', 'red')
        solutions = find_build_solutions(
            'blue',
            2,
            init_energy_num({'red': 2, 'black': 1}),
            [g1],
            False
        )
        self.assertEqual(len(solutions), 1)

    def test_bug_case_2(self):
        g1 = converter_level1('yellow', 'blue')
        g2 = converter_level1('red', 'blue')
        g3 = converter_double_level2('red', 'blue')

        solutions = find_build_solutions(
            'yellow',
            2,
            init_energy_num({'red': 1, 'blue': 1, 'black': 1, 'yellow': 3}),
            [g1, g2, g3],
            False
        )
        self.assertEqual(len(solutions), 4)

        solution = next(s for s in solutions if s['energy_num']['yellow'] == 0)
        energy_num = solution['energy_num']
        gizmos = solution['gizmos']
        self.assertEqual(energy_num, init_energy_num({'blue': 1}))
        self.assertSetEqual(set(gizmos), set([g1, g2, g3]))


if __name__ == '__main__':
    unittest.main(verbosity=2)
