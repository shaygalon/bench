# csv-plotter
## Prerequisites

This program is intended to be used as a command line tool. First, you need to install Plotly.
```
sudo apt install python3-pip
sudo pip3 install plotly
```
If you want to generate plots as .png directly, rename `config/config.json.dist` to `config/config.json` and add credentials for your Plotly account. Plotly currently does not support offline image export.
```
{
    "plotly": {
        "username": "TheSecurityExpert",
        "password": "password123"
    }
}
```
Now, let's get plotting! To see a list of options, try the following.
```
python3 runme.py -h
```

## Example Commands

Below are example commands. Directories (-d) are specified using wildcards to shorten the path.

Plot the "hunger" column for each file on the same graph and export as PNG: <br>`python3 runme.py -d ex*/my* -c hunger --xaxis timestamp -t "Pet Hunger Over Time" -y Hunger -x "Time (minutes)" -I -n "pet_hunger" -S 0.5`

Plot the "hunger" column for each file on the same graph, if "name" value is "buttons":<br>`python3 runme.py -f ex*/my*/dog* -c hunger -p buttons_only --xaxis timestamp --col_eq_val name=buttons`

Plot the "temperature" column for each file on the same graph:<br>`python3 runme.py -d "ex*/*ospm*" -c temperature -t "Temperature Comparison" -y Temperature -p TEMP --ymin 20 --ymax 100`

Plot the sum of columns containing "power" for each file on the same graph:<br>`python3 runme.py -d "ex*/*auto*" -c *power* --sum -t "Power Sum Comparison" -y Power -p POWER -o 7 --ymin 20 --ymax 100`

Plot the "temperature" column as an individual PNG for each file and output to custom directory:<br>`python3 runme.py -d "ex*/*ospm*" -c temperature -t Temperature -y Temperature -p TEMP -i -I -D plots/TEMP_ospm_drupal`

Plot the averages of "core0"/"core1," and "core2"/"core3" columns for each file on the same plot.<br>`python3 runme.py -f "ex*/*ospm*/*drupal*" -c "core-0,core-1;core-2,core-3" --avg -t "Average Core Frequencies" -y Frequency -p FREQ`

## Plotly HTML Capabilities
These are various useful functions you can do in the generated HTML plots.

| Function | Action |
| --- | --- |
| Hide all lines except one | Double-click the line you want to isolate in the legend |
| Show a line | Click on a hidden line in the legend |
| Show all lines | Double click the legend |
| Export as png | Click the camera icon in the upper right. It will save a PNG of the current state, including hidden lines. NOTE: The legend will be cut off if there are too many items; this is a known bug in Plotly |
| Compare lines on hover | Click "compare data on hover" in the upper right. This will show data for all lines on hover, as opposed to just one |
| Zoom | Click and drag diagonally on the graph|
| Limit x-axis | Click and drag horizontally on the graph |
| Reset zoom/axes | Double-click the graph or click "reset axes" in the upper right |
