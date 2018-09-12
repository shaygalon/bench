import os
import sys
import math
import json
import random
import plotly
import plotly.exceptions
import plotly.graph_objs as go


class Plotter:
    """
    Converts a CSV list into plottable data.
    """
    def __init__(self, args, csv_list, xmin=None, xmax=None, ymin=None, ymax=None):
        self.csv_list = csv_list
        self.common_name = self.get_longest_common_name(self.csv_list)
        # NOTE: Max rows are required to be passed if generating individual files.
        self.arg = self.process_args(self.csv_list, args, xmin, xmax, ymin, ymax)
        self.print_args()

    def process_args(self, csv_list, args, xmin, xmax, ymin, ymax):
        """
        Saves and sets default values for args.
        """
        # Store basic args
        arg = dict()
        arg['data'] = args.dir if args.dir else args.file
        arg['cols'], arg['sum'], arg['avg'], arg['min'], arg['max'] = args.cols, args.sum, args.avg, args.min, args.max
        # Set output names. If --indiv is used, ignore --name.
        arg['out_dir'], arg['prefix'] = args.out_dir, "{}_".format(args.prefix) if args.prefix else None
        if arg['data'] is args.dir:
            default_name = os.path.basename(os.path.dirname(csv_list[0].fname))
        else:
            if len(csv_list) > 1:
                default_name = "_VS_".join([os.path.splitext(os.path.basename(x.fname))[0] for x in csv_list])
            else:
                default_name = os.path.splitext(os.path.basename(csv_list[0].fname))[0]
        extension = ".png" if args.image else ".html"
        if args.name and not args.indiv:
            arg['name'] = "{}{}".format(args.name, extension)
        else:
            arg['name'] = "{}{}".format(default_name, extension)
        # Set plot titles
        default_title = "{}*".format(self.common_name) if len(csv_list) > 1 else csv_list[0].fname
        if args.title:
            arg['title'] = "<b>{}</b><br><span style=\"font-size: 10pt\">{}</span>".format(args.title, default_title)
        else:
            arg['title'] = default_title
        arg['y_title'] = args.y_title if args.y_title else (arg['cols'] if ';' not in arg['cols'] else "Unknown Units")
        arg['x_title'] = args.x_title if args.x_title else (args.xaxis if args.xaxis else "Unknown Units")
        # Set broad plot / output information
        arg['img'] = 'png' if args.image else False
        arg['indiv'] = args.indiv
        arg['extend'] = not args.extend_disable
        arg['bar'], arg['autobar'] = args.bar, args.autobar
        arg['unique_colors'] = args.unique_colors
        # Set maxima for axes. Global values are required if individual mode is used, so axes are consistent.
        arg['xaxis'] = args.xaxis if args.xaxis else None
        arg['xmin'] = int(args.xmin) if args.xmin else (xmin if xmin else self.get_x_min(csv_list, args.xaxis))
        arg['xmax'] = int(args.xmax) if args.xmax else (xmax if xmax else self.get_x_max(csv_list, args.xaxis))
        arg['ymin'] = int(args.ymin) if args.ymin \
            else (ymin if ymin else self.get_y_min(csv_list, args.xaxis))
        arg['ymax'] = int(args.ymax) if args.ymax \
            else (ymax if ymax else self.get_y_max(csv_list, args.xaxis))
        arg['xnorm'] = args.xnorm
        if arg['xnorm']:
            arg['xmin'], arg['xmax'] = 0, 100
            arg['x_title'] = '% completed: {}'.format(arg['x_title'])
        return arg

    def generate_plot(self):
        """
        Generate either HTML or PNG. PNG requires internet access.
        """
        plot_data = self.create_plot_data(self.csv_list)
        plot_layout = self.create_plot_layout(self.arg['title'], self.arg['x_title'], self.arg['y_title'])
        plot_fig = go.Figure(data=plot_data, layout=plot_layout)
        if not os.path.exists(self.arg['out_dir']):
            os.makedirs(self.arg['out_dir'])
        filename = "{}{}".format(self.arg['prefix'], self.arg['name']) if self.arg['prefix'] else self.arg['name']
        file_path = os.path.join(self.arg['out_dir'], filename)
        if self.arg['img']:
            proj_dir = sys.path[0].split("/src")[0]
            logged_in = self.login_to_plotly("{}/config/config.json".format(proj_dir))
            if not logged_in:
                return
            print("Generating PNG plot...", end='')
            plotly.plotly.image.save_as(plot_fig, filename=file_path, width=1000, height=750)
            print("done.\n\nSee {}/{}.".format(self.arg['out_dir'], filename))
        else:
            print("Generating HTML plot...", end='')
            plotly.offline.plot(plot_fig, filename=file_path, auto_open=False)
            print("done.\n\nSee {}/{}.".format(self.arg['out_dir'], filename))

    @staticmethod
    def login_to_plotly(config_file):
        try:
            with open(config_file) as json_data_file:
                data = json.load(json_data_file)
                username = data['plotly']['username']
                password = data['plotly']['password']
            print("Logging into Plotly account to export as image...", end='')
            if username and password:
                plotly.plotly.sign_in(username, password)
                print("logged in.")
                return True
            else:
                print("\nYou need to specify a Plotly username and password to export images.\nAborting.")
                return False
        except FileNotFoundError:
            print("config.json does not exist - please rename config.json.dist to config.json and add your Plotly "
                  "account credentials. Aborting.")
            return False
        except plotly.exceptions.PlotlyError:
            print("login failed.\nTo export as image, internet connection and valid account are required.\nAborting.")
            return False

    def create_plot_data(self, csv_list):
        """
        Creates a line for each field, for each CSV.
        STYLE BEHAVIOR: Base colors are unique to CSV. Different lines for the same CSV have slightly different colors.
                        If there are more than 3 traces for a single CSV, start using unique colors.
        """
        print("Creating plot data...", end='')
        traces = []
        trace_id = 0
        for csv_it, csv in enumerate(csv_list):
            base_color = None if self.arg['unique_colors'] else self.choose_color(csv_it)  # Use same base color for CSV
            for trace_it, (field, values) in enumerate(csv.data.items()):
                if field == self.arg['xaxis']:
                    continue
                trace_name, trace_description = self.get_trace_info(csv, field)
                if self.arg['unique_colors'] or trace_it > 2:
                    trace_color = self.color_str(self.choose_color(trace_id))
                else:
                    trace_color = self.color_str(base_color, mod=trace_it)
                trace_type = 'bar' if ((self.arg['autobar'] and trace_id > 2) or self.arg['bar']) else 'line'
                traces.append(self.create_trace(trace_type, csv_it, trace_it, csv, values, trace_name,
                                                trace_description, trace_color))
                trace_id += 1
                if self.arg['extend']:  # If max number of rows in current CSV is less than max, extend horizontally
                    traces.append(self.create_extension(trace_type, csv_it, trace_it, csv, values, trace_name,
                                                        trace_description, trace_color))
        print("done.")
        return traces

    def get_trace_info(self, csv, field):
        """
        Given a csv and a field (e.g. "temperature"), return trace name and description.
        Note that if only graphing one CSV, the trace will have no name (depends on common_substr)
        """
        split = field.split("_")
        trace_name = "{}".format(csv.fname.split(self.common_name)[1].rsplit(".csv")[0])
        if len(split) > 1:
            trace_description = "<br>{} of {}".format(split[0].upper(), split[1])
            trace_name += (" ({})".format(split[0]) if trace_name else " {}".format(split[0].title()))
        else:
            trace_description = ""
            trace_name += (" ({})".format(field) if trace_name else " {}".format(field.title()))
        return trace_name, trace_description

    def create_trace(self, trace_type, csv_it, trace_it, csv, values, trace_name, trace_description, trace_color):
        """
        Create a line or bar trace.
        csv_it and trace_it are integers used to determine legend grouping (to group with extension lines).
        csv and "values" are the current csv and its data values for a field (e.g. "temperature").
        """
        x_vals = csv.data[self.arg['xaxis']] if self.arg['xaxis'] else list(range(0, csv.numrows))
        if self.arg['xnorm']:
            x_vals[:] = [float(x/x_vals[-1])*100 for x in x_vals]
        y_vals = values
        # If max number of x-values is 15 or less, also show an ASCII bar graph in console.
        if len(x_vals) <= 15:
            print("\nTrace:", trace_name)
            # Reformat long floats to single decimal precision
            # TODO: fix histogram function to format x-ticks properly, still has spacing issues
            print(self.get_histogram(15, y_vals, [str("{:.1f}".format(float(x))) for x in x_vals]))
        trace_info = dict(
            x=x_vals,
            y=y_vals,
            name=trace_name,
            legendgroup='group{}-{}'.format(csv_it, trace_it),
            text='{}{}'.format(os.path.basename(csv.fname), trace_description),
        )
        return self.return_trace(trace_type, trace_info, trace_color, bar_opacity=1.0)

    def create_extension(self, trace_type, csv_it, trace_it, csv, values, trace_name, trace_description, trace_color):
        """
        Create an extension trace. This means different styling, and hidden from legend.
        """
        ext_x, ext_y = self.get_extension_values(trace_type, self.get_x_max([csv], self.arg['xaxis']), values)
        trace_info = dict(
            x=ext_x,
            y=ext_y,
            name=trace_name,
            legendgroup='group{}-{}'.format(csv_it, trace_it),
            showlegend=False,
            text='EXTENSION<br>{}{}'.format(os.path.basename(csv.fname), trace_description),
        )
        return self.return_trace(trace_type, trace_info, trace_color, line_style='dot', bar_opacity=0.5)

    @staticmethod
    def return_trace(trace_type, trace_info, trace_color, line_fill=None, line_style=None, bar_opacity=1.0):
        """
        Return and modify the trace info based on trace type.
        """
        if trace_type is 'line':
            trace_info['mode'] = 'lines'
            trace_info['line'] = dict(color=trace_color, dash=line_style)
            trace_info['fill'] = line_fill
            return go.Scatter(trace_info)
        elif trace_type is 'bar':
            trace_info['marker'] = dict(color=trace_color)
            trace_info['opacity'] = bar_opacity
            return go.Bar(trace_info)
        else:
            print("Invalid trace type specified, skipping.")
            return

    def get_extension_values(self, trace_type, cur_max_x, values):
        """
        Return a list of x and y values to use for extensions.
        """
        extension_x, extension_y = [], []
        if cur_max_x == self.arg['xmax']:
            return extension_x, extension_y
        cur_max_y = values[-1]
        # Range doesn't support floats, so account for first val if float
        if not self.is_integer(cur_max_x) and trace_type is not 'bar':
            extension_x.append(cur_max_x)
        start_point = int(math.ceil(cur_max_x))
        extension_x += list(range(start_point, int(math.floor(self.arg['xmax']))))
        # Range doesn't include last int value
        extension_x.append(int(math.floor(self.arg['xmax'])))
        # Account for last val if float
        if not self.is_integer(self.arg['xmax']):
            extension_x.append(self.arg['xmax'])
        extension_y = [cur_max_y] * len(extension_x)
        return extension_x, extension_y

    def create_plot_layout(self, title, x_title, y_title):
        return go.Layout(
            title=title,
            xaxis=dict(title=x_title, range=[self.arg['xmin'], self.arg['xmax']], showline=True, showspikes=True),
            yaxis=dict(title=y_title,
                       range=[self.arg['ymin'], self.arg['ymax'] + (0.05 * (self.arg['ymax'] - self.arg['ymin']))],
                       showline=True, showspikes=True),
            legend=dict(font=dict(size=10), tracegroupgap=0),
            showlegend=True,
            hovermode='closest',
        )

    @staticmethod
    def get_histogram(precision, test_values, xticks):
        """
        Returns a text histogram given precision (# of yticks), list of distribution values, and list of xtick names.
        This can also be used to plot bars.
        """
        xtick_len = len(max(xticks, key=len)) + 2  # Round xticks up to nearest odd int
        if xtick_len % 2 == 0:
            xtick_len += 1
        bar_padding = " " * int(xtick_len / 2)

        def form_line(percentage):
            tick_line = ""
            for value in test_values:
                if percentage != 0 and value >= percentage:
                    tick_line += "{0}#{0}".format(bar_padding)
                elif percentage == 0 and value > percentage:
                    tick_line += "{0}#{0}".format(bar_padding)
                else:
                    tick_line += "{0} {0}".format(bar_padding)
            return tick_line

        lines = []
        tick_mark = float(max(test_values) / precision)
        tick_txt_width = len(str(precision * tick_mark))
        for i in range(1, precision + 1):
            current_tick = int(tick_mark * i)
            line = form_line(current_tick)
            lines.append("\n{0}{1}-|{2}".format(current_tick, " " * int(tick_txt_width - len(str(current_tick))), line))
        histogram = ""
        for line in reversed(lines):
            if not line.split("|")[1].isspace():
                histogram += line
        space = "\n" + ((" " * tick_txt_width) + (" " * 2))  # Space that y-axis takes up
        # Print x-axis
        histogram += space
        for i in range(0, len(xticks)):
            histogram += ("-" * int(xtick_len / 2))
            histogram += "+"
            histogram += ("-" * int(xtick_len / 2))
        # Print x-ticks
        histogram += space
        for i in range(0, len(xticks)):
            xtick_padding = " " * int((xtick_len - len(xticks[i])) / 2)
            histogram += "{0}{1}{0}".format(xtick_padding, xticks[i])
        return histogram

    def print_args(self):
        print("===== ARGS =====")
        for key, value in self.arg.items():
            print("{0:<8}: {1}".format(key, value))
        print("")

    @staticmethod
    def get_x_min(csv_list, xaxis):
        if xaxis:
            return min([min(x.data[xaxis]) for x in csv_list])
        else:
            return 0

    @staticmethod
    def get_x_max(csv_list, xaxis):
        if xaxis:
            return max([max(x.data[xaxis]) for x in csv_list])
        else:
            return max([x.numrows-1 for x in csv_list])  # Subtract 1 because x axis starts from 0.

    @staticmethod
    def get_y_min(csv_list, xaxis):
        """
        csv_list (list) => single csv (CSV object) => csv.data (dictionary) => field values (list)
        """
        return min([val for csv in csv_list
                    for field, csv_vals in csv.data.items() if field != xaxis
                    for val in csv_vals])

    @staticmethod
    def get_y_max(csv_list, xaxis):
        """
        csv_list (list) => single csv (CSV object) => csv.data (dictionary) => field values (list)
        """
        return max([val for csv in csv_list
                    for field, csv_vals in csv.data.items() if field != xaxis
                    for val in csv_vals])

    @staticmethod
    def get_longest_common_name(csv_list):
        """
        Returns the longest common substring (from left to right) of all CSV filenames.
        """
        longest = csv_list[0].fname
        for i in range(1, len(csv_list)):
            cur_fname = list(csv_list[i].fname)
            cur_longest = ""
            for j in range(0, min(len(cur_fname), len(longest))):
                if cur_fname[j] == longest[j]:
                    cur_longest += cur_fname[j]
                else:
                    break
            if len(cur_longest) < len(longest):
                longest = cur_longest
        return longest

    def choose_color(self, iterator):
        """
        Choose a color based on iterator value.
        If iterator is between 0-9, use default colors. Otherwise, use random colors.
        """
        rgb = [(31, 119, 180), (255, 127, 14), (44, 160, 44), (214, 39, 40), (148, 103, 189), (140, 86, 75),
               (227, 119, 194), (127, 127, 127), (188, 189, 34), (23, 190, 207)]
        return rgb[iterator] if iterator < len(rgb) else self.random_rgb()

    @staticmethod
    def random_rgb():
        """
        Not truly random, as it makes certain color is decently dark (excludes total RGB value >540).
        """
        r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        while r + g + b > 540:
            if r > 0:
                r -= 1
            if g > 0:
                g -= 1
            if b > 0:
                b -= 1
        return r, g, b

    @staticmethod
    def color_str(col_tup, mod=0):
        """
        Returns a color tuple (rgb) as a string. Optionally shift colors using a modifier value.
        If modifier value is used, lighten color a bit because base color is pretty dark.
        """
        def sub(val, m):
            return max(0, val-m)
        mod = mod * 100
        lighten = 150 if mod != 0 else 0
        r, g, b = sub(col_tup[0] + lighten, mod), sub(col_tup[1] + lighten, mod / 2), sub(col_tup[2] + lighten, mod / 4)
        return 'rgb({}, {}, {})'.format(r, g, b)

    @staticmethod
    def is_integer(value):
        return value == int(value)
