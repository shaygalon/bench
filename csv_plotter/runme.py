import os
import sys
import glob
import argparse
from src import CSV
from src import Plotter


def get_csv_list(args):
    csv_list = []
    if args.dir:
        for directory in parse_arg_dirfile_list(args.dir):
            for fname in os.listdir(directory):
                if fname.endswith(".csv"):
                    fpath = os.path.join(directory, fname)
                    csv = CSV(fpath, args)
                    if True not in [len(row) > 0 for col, row in csv.data.items()]:
                        print("{} doesn't contain data. Skipping.".format(fpath))
                    else:
                        csv_list.append(csv)
    else:
        for fname in parse_arg_dirfile_list(args.file):
            if fname.endswith(".csv"):
                csv = CSV(fname, args)
                if True not in [len(row) > 0 for col, row in csv.data.items()]:
                    print("{} doesn't contain data. Skipping.".format(fname))
                else:
                    csv_list.append(csv)
    if len(csv_list) == 0:
        print("CSV list is empty. Check that -d/-f are valid, and make sure you aren't filtering everything.")
        print("Aborting.")
        sys.exit(0)
    return csv_list


def parse_arg_dirfile_list(dirfile_list):
    """
    Looks at either "--dir" or "--file" and determines what to use.
    Uses Unix-style matching (* instead of .*), thanks to glob.
    """
    dirfiles = []
    for dirfile in dirfile_list.split(','):
        found_files = glob.glob(dirfile)
        if not found_files:
            print("{} was not found. Please make certain that this is an existing file. Aborting.".format(dirfile))
            sys.exit(0)
        dirfiles += found_files
    # Make sure no duplicate entries, and in order for idempotency
    return sorted(list(set(dirfiles)))


def get_arguments(args):
    """
    Set up all options here.
    """
    parser = argparse.ArgumentParser()
    data = parser.add_mutually_exclusive_group(required=True)
    data.add_argument("-d", "--dir", help="directory containing .csv files (accepts Unix-style wildcards)")
    data.add_argument("-f", "--file", help="comma-separated list of .csv files (accepts Unix-style wildcards)")
    parser.add_argument("-c", "--cols", help="comma-separated list of columns to plot. Use semicolons to group "
                                             "columns. Operations will be performed per group. EXAMPLE: "
                                             "\"-c core-[0-9]+;*power -a -m\" will plot 4 lines per CSV: min/avg of "
                                             "all \"core\" columns, and min/avg of all \"power\" columns. Unix-style "
                                             "wildcards and regular expressions are supported (precedence given to "
                                             "Unix-style wildcards)", required=True)
    parser.add_argument("-s", "--sum", help="plot sum of comma-separated fields as one line", action="store_true")
    parser.add_argument("-a", "--avg", help="plot avg of comma-separated fields as one line", action="store_true")
    parser.add_argument("-m", "--min", help="plot min of comma-separated fields as one line", action="store_true")
    parser.add_argument("-M", "--max", help="plot max of comma-separated fields as one line", action="store_true")
    parser.add_argument("-i", "--indiv", help="generate individual plot for each .csv", action="store_true")
    parser.add_argument("-o", "--offset", help="shift y-values vertically by integer value", default=0)
    parser.add_argument("-S", "--scale", help="multiplies all y-values by float value", default=1)
    parser.add_argument("-D", "--out_dir", help="output directory for plots (default is \"plots\")", default="plots")
    parser.add_argument("-p", "--prefix", help="prefix string used for all generated files, e.g. PREFIX_test.html")
    parser.add_argument("-n", "--name", help="filename of generated plot (does not work with -i)")
    parser.add_argument("-t", "--title", help="title of plot")
    parser.add_argument("-y", "--y_title", help="title of y-axis")
    parser.add_argument("-x", "--x_title", help="title of x-axis")
    parser.add_argument("-e", "--extend_disable", help="disable extension of shorter lines", action="store_true")
    parser.add_argument("-b", "--autobar", help="display fourth and subsequent lines as bars to increase visibility "
                                                "with many lines", action="store_true")
    parser.add_argument("-B", "--bar", help="plot using bars instead of lines", action="store_true")
    parser.add_argument("-u", "--unique_colors", help="use unique colors for each line, even within the same CSV",
                        action="store_true")
    parser.add_argument("-I", "--image", help="export as PNG (requires internet access). You may also manually export "
                                              "as PNG from the HTML plot, but legend will be cut off if there are too "
                                              "many lines", action="store_true")
    parser.add_argument("--xmin", help="minimum x-axis value")
    parser.add_argument("--xmax", help="maximum x-axis value")
    parser.add_argument("--ymin", help="minimum y-axis value")
    parser.add_argument("--ymax", help="maximum y-axis value")
    parser.add_argument("--xaxis", help="use a column for x-axis values")
    parser.add_argument("--xnorm", help="normalize x-axis to 'percent completion' for all lines", action="store_true")
    parser.add_argument("--col_eq_val", help="filter rows where 'COL1=VAL1&COL2=val2...', e.g. 'name=Bob&day=Sunday'")
    return parser.parse_args(args)


def generate_individual_plots(args, csv_list):
    args.dir = None
    xaxis = args.xaxis if args.xaxis else None
    xmin = Plotter.get_x_min(csv_list, xaxis)
    xmax = Plotter.get_x_max(csv_list, xaxis)
    ymin = Plotter.get_y_min(csv_list, xaxis) + args.offset
    ymax = Plotter.get_y_max(csv_list, xaxis) + args.offset
    for csv in csv_list:
        args.file = csv.fname
        plot = Plotter(args, [csv], xmin, xmax, ymin, ymax)
        plot.generate_plot()


def main():
    # STEP 1: Parse args
    args = get_arguments(sys.argv[1:])

    # STEP 2: Get a list of CSV objects.
    csv_list = get_csv_list(args)

    # STEP 3: Create a Plotter and generate plot(s)
    if args.indiv:
        generate_individual_plots(args, csv_list)
    else:
        plot = Plotter(args, csv_list)
        plot.generate_plot()


if __name__ == "__main__":
    main()
