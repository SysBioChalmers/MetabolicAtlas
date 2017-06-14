use strict;

my $baseDir="/Users/halena/Documents/Sys2Bio/hma-prototype/frontend/src/assets/maps/";

if($ARGV[0]){
  fixFile($baseDir."compartment_level/".$ARGV[0].".svg");
}else{
  print STDERR "Missing file name\n";
}

sub fixFile{
  my ($file) = @_;
  my $fTemp = collapseElements($file);
  my $fOut = removeDuplicates($fTemp);
  system("rm $fTemp");
  print STDERR "Generated file ".$fOut." from file ".$file."\n";
}

sub collapseElements{
  my ($file) = @_;
  open FILE, "<" . $file or die "not possible to open file '$file' for reading\n";
  my @lines = <FILE>;
  my $newFileName = $file . ".fixed.svg";
  open OUT, ">" . $newFileName or die "not possible to create ".$newFileName."\n";
  for(my $i=0; $i<=scalar(@lines); $i++){
    my $line = $lines[$i];
    #print STDERR "LINE is '$line'\n";
    my $potential_fulldescription = $lines[$i+1];
    my $potential_text_path = $lines[$i+3];
    if($line =~ m/^\n/){
      # skip do nothing
    }elsif($line =~ m/^<g.*>/){
      print OUT $line;
    }elsif($line =~ m/^<g/){
      chomp($line);
      chomp($potential_fulldescription);
      if($potential_fulldescription =~ m/>/){
        print OUT "  ".$line . " " . $potential_fulldescription . "</g>\n";
        $i=$i+2;
      }else{
        chomp($potential_text_path);
        if($potential_text_path =~ m/^<text/){
          if($lines[$i+5]=~m/^<text/){
            my $j = $i + 1;
            print OUT "  ".$line;
            while($lines[$j] !~ m/^<\/g>/){
              chomp($lines[$j]);
              print OUT "    ".$lines[$j++];
            }
            print OUT "</g>\n";
            $i = $j;
          }elsif($potential_text_path!~m/^>/){
            print OUT "  ".$line . " ".$potential_fulldescription . ">\n    ".
              $potential_text_path.$lines[$i+4]."\n</g>\n";
            $i=$i+5;
          }else{
            print OUT "  ".$line . " ".$potential_fulldescription . ">\n    ".$potential_text_path."\n</g>\n";
            $i=$i+4;
          }
        }elsif($potential_text_path =~ m/^<path/){
          print OUT "  ".$line . " ".$potential_fulldescription . ">\n    ";
          print OUT $potential_text_path;
          print OUT "\n</g>\n";
          $i=$i+3;
        }elsif($potential_fulldescription =~ m/^font/){
          if($lines[$i+3]=~m/^<image/){
            print OUT "  ".$line . " ".$potential_fulldescription . ">\n";
            $i=$i+2;
          }else{
            print OUT "  ".$line . " ".$potential_fulldescription . "></g>\n";
            $i=$i+3;
          }
        }else{
          print OUT "  ".$line . " ".$potential_fulldescription . "></g>\n";
          $i=$i+3;
        }
      }
    }else{
      print OUT $line;
    }
  }
  close OUT;
  return($newFileName);
}

sub removeDuplicates{
  my ($file) = @_;
  open FILE, "<" . $file or die "not possible to open file '$file' for reading\n";
  my @lines = <FILE>;
  my $newFileName = $file . ".unique.svg";
  open OUT, ">" . $newFileName or die "not possible to open file '$newFileName' for printing\n";
  for(my $i=1; $i<=scalar(@lines); $i++){
    if($lines[$i] eq $lines[$i-1]){
      # do nothing but skip the duplicated lines...
    }else{
      print OUT $lines[$i];
    }
  }
  close OUT;
  return($newFileName);
}
