import os
import re
import sys
import fnmatch


class CSV:
    """
    Represents a SINGLE csv file as a dictionary of values for each column.
    EXAMPLE USAGE: test_csv.data["core-0"]
    """
    def __init__(self, fname, args):
        print("Parsing {}...".format(fname))
        self.fname = fname
        self.data = self.parse_csv(fname, args)
        # Get the number of rows for first arbitrary value
        self.numrows = len(next(iter(self.data.values())))
        self.handle_col_ops(args)
        self.apply_modifiers(args)
        print("Done.\n")

    def parse_csv(self, fname, args):
        """
        Parses relevant and unique columns into data structure. Does NOT account for column operations.
        EXAMPLE: In "-c core.* --sum," this would store all cols beginning with "core," NOT a single col of their sum.
        """
        def valid_row(split_row):
            return split_row[0] and not split_row[0].startswith('#')
        if not os.path.exists(fname) or not os.path.isfile(fname):
            print("{} does not exist or is not a file. Aborting.".format(fname))
            sys.exit(0)
        data, limits = dict(), dict()
        with open(fname) as file:
            # Get header. Skip comments and whitespace.
            line_num = 1
            header = [x.strip() for x in file.readline().split(',')]
            while not valid_row(header):
                # print("[SKIP] Not a header (line {})".format(line_num))
                header = [x.strip() for x in file.readline().split(',')]
                line_num += 1
            print("[HEADER] Header found! (line {})".format(line_num))
            fields_to_use = self.parse_arg_cols_list(args.cols, header)
            if args.xaxis:
                fields_to_use.append(args.xaxis)
            for field in fields_to_use:
                data[field] = []
            # Get indices of conditional limits. limits[idx] = val
            if args.col_eq_val:
                for limit in args.col_eq_val.split('&'):
                    lim = limit.split("=")
                    if len(list(filter(None, lim))) != 2:  # Get rid of empty strings
                        print("You didn't use --col_eq_val correctly. Format must be COL=VAL.")
                        sys.exit(0)
                    col, val = limit.split("=")[0], limit.split("=")[1]
                    idx = header.index(col) if col in header else None
                    if idx is not None:
                        limits[idx] = val
                    else:
                        print("The column specified in --col_eq_val was not in headers. Aborting.")
                        sys.exit(0)
            # Parse data into dictionary. Only parse columns that were specified.
            for row in file:
                line_num += 1
                split = row.split(',')
                # Skip rows that don't match with header, or are blank/comments
                if (len(split) != len(header)) or (not valid_row(split)):
                    print("[SKIP] Bad row (line {})".format(line_num))
                    continue
                # Skip rows that don't meet --col_eq_val condition
                if args.col_eq_val:
                    if False in [(split[idx].strip() == val) for idx, val in limits.items()]:
                        # print("[SKIP] Condition not met (line {})".format(line_num))
                        continue
                row_data = [x.strip() for x in split]
                for num, value in enumerate(row_data):
                    if header[num] in fields_to_use:
                        if self.is_float(value):
                            data[header[num]].append(float(value))
                        # If the value isn't a float, it probably has units...try to handle intelligently
                        else:
                            modified_value = re.search('[-+]?[0-9]*\.?[0-9]+', value).group(0)
                            # Try applying units (K or M) and convert to float
                            modified_value = self.convert_si(modified_value, value.replace(modified_value, ''))
                            print("[NOTE] Interpreting '{}' as '{}' (line {})"
                                  .format(value, modified_value, line_num))
                            data[header[num]].append(modified_value)
            return data

    @staticmethod
    def parse_arg_cols_list(cols, search_list):
        """
        Looks at "--cols" argument to determine what cols to save.
        Supports both Unix-style and regex matching.
        """
        fields = re.split('[;,]', cols)
        fields_to_use = []
        for field in fields:
            regex = fnmatch.translate(field)
            matching_fields = list(filter(re.compile(regex).match, search_list))
            # If Unix-style matching doesn't work, try regex
            if len(matching_fields) == 0:
                matching_fields = list(filter(re.compile("^{}$".format(field)).match, search_list))
            if len(matching_fields) == 0:
                print("\"{}\" not found in CSV headers. Check the first line of the CSV -- aborting.".format(field))
                sys.exit(0)
            fields_to_use += matching_fields
        # Make sure no duplicate entries, and in order for idempotency
        return sorted(list(set(fields_to_use)))

    def handle_col_ops(self, args):
        """
        Converts saved columns to "combined" columns based on col operations (sum, avg, min, max).
        EXAMPLE: In "-c core.* -s," this would take existing cols and combine them into a single col of their sums.
        """
        # Returns a dictionary key for operated columns
        def name(operation, fields):
            return "{}_{}".format(operation, "/".join(fields))
        # If there are no operations, then data is already good to go. Semicolons don't matter.
        if not args.sum and not args.avg and not args.min and not args.max:
            return
        stored_field_names = [name for name, vals in self.data.items()]
        # For each colgroup (separated by semicolon);
        colgroups = args.cols.split(';')
        for colgroup in colgroups:
            cols = []
            raw_cols = colgroup.split(',')
            matching_fields = self.parse_arg_cols_list(colgroup, stored_field_names)
            cols += [self.data[x] for x in matching_fields]
            # No need to operate on single columns
            if len(cols) == 1:
                continue
            # Now, perform operation on cols
            for i in range(0, len(cols[0])):
                row_vals = [x[i] for x in cols]
                if args.sum:
                    if name('sum', raw_cols) not in self.data:
                        self.data[name('sum', raw_cols)] = []
                    self.data[name('sum', raw_cols)].append(sum(row_vals))
                if args.avg:
                    if name('avg', raw_cols) not in self.data:
                        self.data[name('avg', raw_cols)] = []
                    self.data[name('avg', raw_cols)].append(sum(row_vals) / float(len(row_vals)))
                if args.min:
                    if name('min', raw_cols) not in self.data:
                        self.data[name('min', raw_cols)] = []
                    self.data[name('min', raw_cols)].append(min(row_vals))
                if args.max:
                    if name('max', raw_cols) not in self.data:
                        self.data[name('max', raw_cols)] = []
                    self.data[name('max', raw_cols)].append(max(row_vals))
        # Update data - add operated columns, remove individual columns
        filtered_data = dict()
        for key, value in self.data.items():
            used_individually = (len([x for x in args.cols.split(';') if x == key]) != 0) or key == args.xaxis
            if used_individually or key.startswith(("sum", "avg", "min", "max")):
                filtered_data[key] = value
        self.data = filtered_data

    def apply_modifiers(self, args):
        """
        Applies scaling and offset modifications to all values (after col operations)
        """
        for colname, values in self.data.items():
            if colname != args.xaxis:
                self.data[colname] = [self.modify(args, val) for val in values]

    @staticmethod
    def modify(args, value):
        """
        Applies scaling and offset modifications to a single value
        """
        offset, scale = int(args.offset), float(args.scale)
        value = value * scale if scale else value
        value = value + offset if offset else value
        return value

    @staticmethod
    def convert_si(value, unit):
        """
        Tries to convert to SI units if applicable
        """
        si = {'k': 1000, 'm': 1000000}
        unit = unit.lower()
        value = float(value)
        if unit in si:
            value = value * si[unit]
        return value

    @staticmethod
    def is_float(value):
        try:
            float(value)
            return True
        except ValueError:
            return False
