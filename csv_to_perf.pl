use XML::Loy;

open(CSV,"<$ARGV[0]");
$FN=$ARGV[0];
$FN=~s/.csv//;
my $xml = XML::Loy->new('report' => { 'name' => $FN});

$header=0;
while (<CSV>) {
	chomp;
	if (/^#/) {
		next if ($header);
		$header=1;
		$hl=$_;
		$hl=~s/#//;
		next;
	}
	push @r,$_;
}
close(CSV);
if (!defined($hl)) {
	$hl="Test,Unit,Result,Other";
}
@hf=split /,/,$hl;
if ($hl =~ /Unit/i) { $has_unit=1; } else { $has_unit=0; }

 
# Add elements to the document
my $header = $xml->add('test' => { 'name' => $FN, 'executed' => 'yes' } );
my $r=$header->add('result' => {} );
my $m=$r->add('metrics' => {} );
for $fl (@r) {
	@f=split /,/,$fl;
	if ($has_unit) { $unit=$f[1]; } else { $unit="A"; }
	$m->add($f[0] => { 'unit' => $unit, 'mesure' => $f[2], 'isRelevant' => "yes" } );
}
print $xml->to_pretty_xml;



