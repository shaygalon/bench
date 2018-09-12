use Getopt::Long;
use GD::Graph::lines;
use GD::Graph::Data;
use Data::Dumper;
use strict;

my $plot_names="core-0,memnet-freq";
my $csv_file="test.csv";
my $out_file=$csv_file;
my $nodes=1;
my $y_title="freq";
my $add_fields=0;
my $offset=0;
my $ymin=undef;
my $ymax=undef;
GetOptions ("input=s" => \$csv_file,    
            "fields=s"   => \$plot_names,     
			"add" => \$add_fields,
			"offset" => \$offset,
            "nodes=i"   => \$nodes,     
			"y_title=s" => \$y_title,
			"miny=s" => \$ymin,
			"maxy=s" => \$ymax,
			"out=s"  => \$out_file)  ; 

my @column=split ',',$plot_names;
my @data1=();
my @data2=();
my $numvals=0;


open(F,"<$csv_file");

my $header=0;
my @cidx;

my $last_row=0;
my @row=();
my @column_name=();
my %vals={};
my %tvals={};
#parse the csv file
while (<F>) {
	chomp;
	my $line=$_;
	my @f=split ',';
	if ($header==0) {
		my @name=@f;
		foreach my $cn (@column) {
			if ($line !~ $cn) { die "Could not find column $cn to plot"; } 
		}
		my $i=0;
		my %idx;
		foreach my $cn (@name) {
			$idx{$cn}=$i;
			$i++;
		}
		foreach my $cn (@column) {
			push @cidx, $idx{$cn};
		}
		for ($i=0; $i<$nodes; $i++) {
			if ($add_fields) {
				push @column_name, "N$i";
			} else {
				foreach my $cn (@column) {
					push @column_name, "$cn-N$i";
				}
			} 
		}
		$header=1;
		next;
	}
	if ($f[0] < $nodes) {
		my $total=$offset;
	 foreach my $col (@cidx) {
		if ($add_fields) { $total += $f[$col]; } 
		else {	
			 push @{$vals{"$f[0]-$col"}},$f[$col]; 
			 $tvals{"$f[0]-$col"}+=$f[$col]; 
		}
	 }
	 if ($add_fields) { push @{$vals{"$f[0]"}},$total; }
	}

    if ($f[0] == ($nodes-1)) { $numvals++; }
}
close(F);

# if some values are missing on the last row, fill in from last measurement in case output file was cut in the middle of line
if (!$add_fields) {
my $minval=$numvals;
for (my $i=0; $i<$nodes; $i++) {
	    foreach my $col (@cidx) {
			my $val=scalar(@{$vals{"$i-$col"}}); 

			if ($val < $numvals) {
				my $j;
				my $replicate=$vals{"$i-$col"}[$val-1];
				for ($j=0; $j<$numvals-$val; $j++) {
					push @{$vals{"$i-$col"}},$replicate;
				}
			}
		}
}
}



my @ticks=(1..$numvals);
push @data1,\@ticks;
for (my $i=0; $i<$nodes; $i++) {
	if ($add_fields) {push @data1,\@{$vals{"$i"}};} else { 
		foreach my $col (@cidx) {
		 push @data1,\@{$vals{"$i-$col"}}; 
		 print "Average for $i - $col = ".$tvals{"$i-$col"}/$numvals."\n";
		}
	}
}
			 
my $graph = GD::Graph::lines->new(600,300);
 
$graph->set( 
    x_label         => 'time',
    y_label         => $y_title,
    title           => $csv_file,
    line_width  => 2,
    # Set colors for datasets
    dclrs       => ['blue', 'green', 'red', 'yellow'],
	x_tick_number => 'auto',
    y_min_value => $ymin,
    y_max_value => $ymax,
    #y_max_value     => 7,
    #y_tick_number   => 8,
    #y_label_skip    => 3,
 
    #x_labels_vertical => 1,
) or die $graph->error;

$graph->set_legend_font(GD::gdMediumBoldFont);
$graph->set_legend(@column_name);
#print Dumper(\@data1);
my $image = $graph->plot(\@data1) or die $graph->error;

my $file = "$out_file.png";
open(my $out, '>', $file) or die "Cannot open '$file' for write: $!";
binmode $out;
print $out $graph->gd->png;
close out;

