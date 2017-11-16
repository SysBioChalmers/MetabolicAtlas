use strict;
use Getopt::Long;
use Pod::Usage;

# handle the command line options
my $findThis = undef;
my $matchAllFields = 1;
my $includeCellLines = 1;
my $viewRelationshipsAsWell = 0;
parseCommandLineOptions();

my %bto;
readOBOFile(); # read in the BTO ontology

if(defined($findThis)){
  if($findThis eq "all"){
    print "ID\tNAME\tDEFINITION\n";
    foreach my $btoid (keys(%bto)){
      my $def=$bto{$btoid}->{"def"};
      $def=~s/\"//g; # remove all quote characters
      print $btoid."\t".$bto{$btoid}->{"name"}."\t".$def."\n";
    }
  }else{
    print "ID\tNAME\tDEFINITION\tSynonyms\tMATCHED_AT\n";
    foreach my $btoid (keys(%bto)){
      if($btoid =~ /$findThis/ || $bto{$btoid}->{"name"}=~m/$findThis/i){
        printBTO($btoid, "ID/Name");
      }else{
        if($matchAllFields){
          foreach my $s (keys(%{$bto{$btoid}->{"synonyms"}})){
            if($s =~ m/$findThis/i){
              printBTO($btoid, "Synonym");
            }
          }
        }
      }
    }
  }
}


sub printBTO{
  my ($id, $whereFound) = @_;
  my $current = $bto{$id};
  if(defined($whereFound)){
    if((!$includeCellLines) && ($current->{"name"}=~m/cell/)){
      return;
    }
    print $id . "\t" . $current->{"name"} . "\t" . $current->{"def"} .
      "\t" . $whereFound . "\n";
    foreach my $s (keys(%{$current->{"synonyms"}})){
      print "\tSynonym:\t" . $s."\n";
    }
    # for each hierarchy spin it upwards...
    my @rs = keys(%{$current->{"relationships"}});
    if(scalar(@rs)>0){
      foreach my $r (@rs){
        print "\tHierarchy:\t" . _getParentInfo($r, "") . "\n";
      }
    }
  }
  print "\n";
}


sub _getParentInfo{
  my ($parent_info, $str) = @_;
  my $parent_id = $parent_info;
  $parent_id =~ s/^.*BTO/BTO/;
  $parent_id =~ s/ .*//;
  $str .= $parent_info . " :: ";
  if(exists($bto{$parent_id}->{"relationships"})){
    my @r = keys($bto{$parent_id}->{"relationships"});
    $str .= _getParentInfo($r[0], $str); #ToDo: right now assumes a single parent...
  }
  return $str;
}


sub readOBOFile{
  open FILE, "<BTO.OBO" or die "missing input file\n";
  my $id = ""; my $name = ""; my $def = "";
  my @is_a; my @synonyms; my @relationships;
  while(my $line=<FILE>){
    chomp($line);
    if($line =~ m/^id:/){
      $id = $line;
      $id =~ s/^.*id: //;
    }elsif($line =~ m/^name:/){
      $name = $line;
      $name =~ s/^.*name: //;
    }elsif($line =~ m/^is_a:/){
      my $tmp = $line;
      $tmp =~ s/^.*is_a: //;
      push(@is_a, $tmp);
    }elsif($line =~ m/^(relationship|is_a):/){
      my $tmp = $line;
      $tmp =~ s/^(relationship|is_a): //;
      push(@relationships, $tmp);
    }elsif($line =~ m/^def:/){
      $def = $line;
      $def =~ s/^.*def: //;
    }elsif($line =~ m/^synonym:/){
      my $temp = $line;
      $temp =~ s/^.*synonym: //;
      $temp =~ s/ RELATED.*//;
      $temp =~ s/\"//g;
      push(@synonyms, $temp);
    }elsif(length($line)<1){
      # first "save" this one
      $bto{$id}->{"name"}=$name;
      $bto{$id}->{"def"}=$def;
      foreach my $i (@is_a){ $bto{$id}->{"is_a"}->{$i} = 1; }
      foreach my $s (@synonyms){ $bto{$id}->{"synonyms"}->{$s} = 1; }
      foreach my $r (@relationships){ $bto{$id}->{"relationships"}->{$r} = 1; }
      # then reset the "global" variables
      $id = ""; $name = ""; $def = "";
      @is_a = (); @synonyms = (); @relationships = ();
    }elsif($line =~ /^\[Typedef\]/){
      close FILE;
    }else{
      #print STDERR "LINE is '$line'\n";
    }
  }
  close FILE;
}


sub parseCommandLineOptions{
  my $man = 0; my $help = 0;
  GetOptions ("findThis=s" => \$findThis,
              "allFields=i" => \$matchAllFields,
              "includeCellLines=i"  => \$includeCellLines,
              "viewRelations" => \$viewRelationshipsAsWell,
              'help|?' => \$help, man => \$man) ||
      pod2usage(-verbose => 0);
  pod2usage(2) if $help;
  if(!defined($findThis)){
    pod2usage({-message => "Error in command line arguments, missing findThis", -verbose => 1});
  }
}


__END__

=head1 NAME

    sample - Using Getopt::Long and Pod::Usage

=head1 SYNOPSIS

    sample [options] [file ...]
     Options:
       -help            brief help message
       -man             full documentation
       -findThis        what are we looking for?

=head1 DESCRIPTION

    B<This program> will read the given input file(s) and do something
    useful with the contents thereof.

=cut
