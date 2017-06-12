use strict;

my $baseDir="/Users/halena/Documents/Sys2Bio/hma-prototype/frontend/src/assets/maps/";

if($ARGV[0] && $ARGV[0] eq "combine"){
  open OUT, ">".$baseDir."whole_metabolic_network.svg";
  print OUT addTitle();
  adjustPositions($baseDir."compartment_level/cytosol_5.svg", 7000, 6000);
  adjustPositions($baseDir."compartment_level/lysosome.svg", 28700, 0);
  adjustPositions($baseDir."compartment_level/golgi.svg", 43000, 0);
  adjustPositions($baseDir."compartment_level/cytosol_2.svg", 55000, 0);
  adjustPositions($baseDir."compartment_level/nucleus.svg", 20000, 20000);
  adjustPositions($baseDir."compartment_level/cytosol_4.svg", 37000, 17000);
  adjustPositions($baseDir."compartment_level/ER.svg", 55000, 21000);
  adjustPositions($baseDir."compartment_level/cytosol_6.svg", 0, 25000);
  adjustPositions($baseDir."compartment_level/cytosol_3.svg", 75000, 24000);
  adjustPositions($baseDir."compartment_level/mitochondrion.svg",3000, 57000);
  adjustPositions($baseDir."compartment_level/cytosol_1.svg", 46000, 55000);
  adjustPositions($baseDir."compartment_level/perixome.svg", 58000, 60000);
  print OUT "\n</svg>\n";
}else{
  open OUT, ">testingtesting.svg";
  print OUT addTitle();
  adjustPositions($baseDir."compartment_level/golgi.svg")
  print OUT "\n</svg>\n";
}




sub addTitle{
  my $str = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>
<svg xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\"  version=\"1.2\" baseProfile=\"tiny\">
<title>Metabolic Network</title>

";
}


sub adjustPositions{
  my ($file, $addX, $addY) = @_;
  open FILE, "<" . $file or die "not possible to open file '$file'\n";
  while(my $line = <FILE>){
    if($line =~ m/stroke.*transform/){
      chomp($line);
      my $pos = $line;
      $pos =~ s/^.*transform=.matrix.//;
      $pos =~ s/\).*$//;
      my @m = split(",", $pos);
      my $x = $m[4];
      my $y = $m[5];
      my $i = index($line, 'transform="matrix');
      my $x2 = $x + $addX;
      my $y2 = $y + $addY;
      $line =~ s/$x,$y/$x2,$y2/;
      print OUT $line . "\n";
    }elsif($line =~ m/text fill/){
      chomp($line);
      my $pos = $line;
      $pos =~ s/^.*x.=//;
      $pos =~ s/. font-family.*//;
      my $x = $pos; my $y =$pos;
      $x =~ s/\"\s.*//;
      $y =~ s/^.*\"//;
      my $x2 = $x + $addX;
      my $y2 = $y + $addY;
      $line =~ s/x=.$x. y=.$y/x=\"$x2\" y=\"$y2/;
      print OUT $line . "\n";
    }elsif($line =~ m/^<(.xml|svg|title|desc|defs|.defs|.svg)/){
      # do nothing for the title
    }else{
      print OUT $line;
    }
  }
  close FILE;
}
