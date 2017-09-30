use strict;



# 1 get a list of all enzymes in the SBML file of interest
`grep modifierSpeciesReference $ARGV[0] | sort -u > test`;
`perl -p -i -e "s/^.*species..//" test`;
`perl -p -i -e "s/...\$//" test`;
open FILE, "<test";
my %enzymes;
while(my $line=<FILE>){
  chomp($line);
  $enzymes{$line}=1;
}
close FILE;


# 2 loop through the SBML file and see if the enzyme is specified, if so keep it
open FILE, "<" . $ARGV[0] or die "not possible to open file '$ARGV[0]'\n";
my @lines = <FILE>;
close FILE;
open OUT, ">" . $ARGV[0];
for(my $i=0; $i<scalar(@lines); $i++){
  my $line = $lines[$i];
  if($line =~ m/<species.*ENSG/ || $line=~m/<species.*E_/){
    my $enzyme = $line;
    $enzyme =~ s/^.*id=\"E/E/;
    $enzyme =~ s/\".*\n//;
    #print STDERR "Enzyme '$enzyme' froml line '$line'\n";
    if(exists($enzymes{$enzyme})){
      print OUT $line;
    }
  }else{
    print OUT $line;
  }
}
