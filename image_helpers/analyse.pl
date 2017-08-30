use strict;

my $baseDir="/Users/halena/Documents/Sys2Bio/hma-prototype/frontend/src/assets/maps/compartment_level/";

my $only_look_at_lines_with="a28dff.*stroke.*transform";    # metabolite default color...
#my $only_look_at_lines_with="stroke.*transform";            # all

if($ARGV[0] && $ARGV[0] eq "test"){
  readFile("test file", "test.svg");
}elsif($ARGV[0]){
  readFile("input file - ".$ARGV[0], $baseDir.$ARGV[0].".svg");
}else{
  readFile("Lysosome", $baseDir."lysosome.svg");
  readFile("perixome", $baseDir."perixome.svg");
  readFile("ER", $baseDir."ER.svg");
  readFile("Nucleosome", $baseDir."nucleosome.svg");
  readFile("Mitochondria", $baseDir."mitochondrion.svg");
  readFile("Golgi", $baseDir."golgi.svg");
  readFile("C1", $baseDir."cytosol_1.svg");
  readFile("C2", $baseDir."cytosol_2.svg");
  readFile("C3", $baseDir."cytosol_3.svg");
  readFile("C4", $baseDir."cytosol_4.svg");
  readFile("C5", $baseDir."cytosol_5.svg");
  readFile("C6", $baseDir."cytosol_6.svg");
}


sub readFile{
  my ($compartment, $file) = @_;
  print STDERR "Compartment: ".$compartment."\n";
  my $minX=1000000; my $maxX=0; my $minY=10000000; my $maxY=0; my $count = 0;
  open FILE, "<" . $file or die "not possible to open file '$file'\n";
  while(my $line=<FILE>){
    if($line =~ m/$only_look_at_lines_with/){
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
