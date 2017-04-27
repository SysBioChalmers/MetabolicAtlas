use strict;

my $baseDir="/Users/halena/Documents/Sys2Bio/hma-prototype/frontend/src/assets/maps/";

if($ARGV[0]){
  readFile("input file", $baseDir."compartment_level/lysosome.svg");
}else{
  readFile("L", $baseDir."compartment_level/lysosome.svg");
  readFile("P", $baseDir."compartment_level/perixome.svg");
  readFile("ER", $baseDir."compartment_level/ER.svg");
  readFile("Golgi", $baseDir."compartment_level/golgi.svg");
  readFile("C1", $baseDir."compartment_level/cytosol_1.svg");
  readFile("C2", $baseDir."compartment_level/cytosol_2.svg");
  readFile("C3", $baseDir."compartment_level/cytosol_3.svg");
  readFile("C4", $baseDir."compartment_level/cytosol_4.svg");
  readFile("C5", $baseDir."compartment_level/cytosol_5.svg");
  readFile("C6", $baseDir."compartment_level/cytosol_6.svg");
}


sub readFile{
  my ($compartment, $file) = @_;
  print STDERR "Compartment: ".$compartment."\n";
  my $minX=1000000; my $maxX=0; my $minY=10000000; my $maxY=0; my $count = 0;
  open FILE, "<" . $file or die "not possible to open file '$file'\n";
  while(my $line=<FILE>){
    if($line =~ m/stroke.*transform/){
      chomp($line);
      my $pos = $line;
      $pos =~ s/^.*transform=.matrix.//;
      $pos =~ s/\).*$//;
      my @m = split(",", $pos);
      my $x = $m[4];
      my $y = $m[5];
      $minX = $x if($x < $minX);
      $maxX = $x if($x > $maxX);
      $minY = $y if($y < $minY);
      $maxY = $y if($y > $maxY);
      $count++;
    }
  }
  close FILE;
  print STDERR "X: ".$minX." - ".$maxX . " count=".$count."\n";
  print STDERR "Y: ".$minY." - ".$maxY . " count=".$count."\n";
}
