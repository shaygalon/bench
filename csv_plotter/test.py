import unittest
from src import Plotter
from runme import get_csv_list, get_arguments


class TestCSVPlotter(unittest.TestCase):

    # Check that get_arguments works with necessary arguments
    def test_min_args(self):
        args = get_arguments(['-d', 'foo', '-c', 'bar'])
        self.assertTrue(args.dir and args.cols)

    # Check that "cat" csv is parsed correctly, even with imperfections
    def test_csv_parsing_cat(self):
        args = get_arguments(['-f', 'ex*/my*/cat*', '-c', 'hunger', '-n', 'pet_hunger', '--xaxis', 'timestamp'])
        csv = get_csv_list(args)[0]
        self.assertEqual(csv.numrows, 14)
        self.assertEqual(len(csv.data), 2)

    # Check that "dog" csv is parsed correctly, even with imperfections
    def test_csv_parsing_dog(self):
        args = get_arguments(['-f', 'ex*/my*/dog*', '-c', 'hunger', '-n', 'pet_hunger', '--xaxis', 'timestamp'])
        csv = get_csv_list(args)[0]
        self.assertEqual(csv.numrows, 12)
        self.assertEqual(len(csv.data), 2)

    # Check that single conditional column filtering works
    def test_csv_parsing_dog_col_filter_equals_single(self):
        args = get_arguments(['-f', 'ex*/my*/dog*', '-c', 'hunger', '-n', 'pet_hunger', '--xaxis', 'timestamp',
                              '--col_eq_val', 'name=buttons'])
        csv = get_csv_list(args)[0]
        self.assertEqual(csv.data['hunger'][0], 4.0)

    # Check that chained conditional column filtering works
    def test_csv_parsing_dog_col_filter_equals_multiple(self):
        args = get_arguments(['-f', 'ex*/my*/dog*', '-c', 'hunger', '-n', 'pet_hunger', '--xaxis', 'timestamp',
                              '--col_eq_val', 'name=buttons&timestamp=8'])
        csv = get_csv_list(args)[0]
        self.assertEqual(len(csv.data['timestamp']), 1)
        self.assertEqual(csv.data['timestamp'][0], 8.0)

    # Check that the default name generated for a directory is correct
    def test_plotter_default_name_dir(self):
        args = get_arguments(['-d', 'ex*/my*', '-c', 'hunger', '-n', 'pet_hunger'])
        csv_list = get_csv_list(args)
        plot = Plotter(args, csv_list)
        self.assertEqual(plot.arg['name'], 'pet_hunger.html')

    # Check that the default name generated for a file is correct
    def test_plotter_arg_filename(self):
        args = get_arguments(['-d', 'ex*/my*', '-c', 'hunger', '-I'])
        csv_list = get_csv_list(args)
        plot = Plotter(args, csv_list)
        self.assertEqual(plot.arg['name'], 'my_examples.png')


if __name__ == '__main__':
    unittest.main()
