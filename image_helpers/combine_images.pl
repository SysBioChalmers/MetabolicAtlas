use strict;

my $baseDir="/Users/halena/Documents/Sys2Bio/hma-prototype/frontend/src/assets/maps/compartment_level/without_details/";

if($ARGV[0] && $ARGV[0] eq "combine"){
  open OUT, ">".$baseDir."../../whole_metabolic_network_without_details.svg";
  print OUT addTitle();
  # "line 1"
  adjustPositions($baseDir."cytosol_5.svg", 7000, 6000);
  adjustPositions($baseDir."lysosome.svg", 32000, 0);
  adjustPositions($baseDir."golgi.svg", 50000, 5000);
  adjustPositions($baseDir."cytosol_2.svg", 67000, 10000);
  # "line 2"
  adjustPositions($baseDir."nucleosome.svg", 24000, 29000);
  adjustPositions($baseDir."cytosol_4.svg", 37000, 17000);
  adjustPositions($baseDir."ER.svg", 56000, 21000);
  # "line 2.5"
  adjustPositions($baseDir."cytosol_6.svg", 0, 25000);
  adjustPositions($baseDir."cytosol_3.svg", 78000, 24000);
  # "line 3"
  adjustPositions($baseDir."mitochondrion.svg", 3000, 45000);
  adjustPositions($baseDir."cytosol_1.svg", 46000, 47000);
  adjustPositions($baseDir."perixome.svg", 61000, 50000);
  print OUT "\n</svg>\n";
}else{
  open OUT, ">testingtesting.svg";
  print OUT addTitle();
  adjustPositions($baseDir."golgi.svg");
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
  # remove the header parts
  my $line;
  while($line = <FILE>){
    if($line=~m/<\Wdefs>/){
      last;
    }
  }
  while($line = <FILE>){
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
    }elsif($line =~ m/^\s*<(.xml|svg|title|desc|defs|.defs|.svg)/){
      # do nothing for the title
    }else{
      print OUT $line;
    }
  }
  close FILE;
}
