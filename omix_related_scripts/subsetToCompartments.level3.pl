use strict;

my $fileName = $ARGV[0];
my $compartmentToLookFor = $ARGV[1];

my %reconAbb;
readLabel("labels.tab");
my %metabolites;


open FILE, "<" . $fileName or die "not possible to open '$fileName'\n";
while(my $line = <FILE>){
  if($line =~ m/species boundaryCondition/){
    chomp($line);
    my $metId = _getMetID($line);
    $metabolites{$metId} = $line; # remember all metabolites so I can properly deal with transporter reactions...
    _printMetaboliteInformation($metId, $line);
  }elsif($line =~ m/reaction fast/){
    _printReactions($line);
  }elsif($line =~ m/\Wcompartment constant/){
    _printCompartmentInformation($line);
  }elsif($line =~ m/ENS.*compartment="/){
    #if($line =~ m/C_$compartmentToLookFor/){ # all enzymes are "located" in c...
      $line =~ s/compartment="C_/compartment="/; # just in case...
      print $line;
    #}
  }else{
    # if its not a species (eg metabolite) or reaction definition print the line...
    print $line;
  }
}
close FILE;


# originally I planned on only including the compartment of interest, but as I now include transport reactions as well I figured that having all compartments was good...
sub _printCompartmentInformation{
  my ($line) = @_;
  if($line =~ m/name=.Boundary/){
    print $line;
  }else{
  #}elsif($line =~ m/id=.$compartmentToLookFor/ || $line=~m/id=\"c/){
    chop($line); chop($line); chop($line);
    $line = $line . " outside=\"x\"/>\n";
    print $line;
  }
}

sub _printMetaboliteInformation{
  my ($metId, $line) = @_;
  if($line =~ m/compartment=.$compartmentToLookFor/ || $line=~m/ENSG/){
    $metId =~ s/$compartmentToLookFor$//;
    my $metName = $line;
    $metName =~ s/^.*name=.//;
    $metName =~ s/. (compartment|reconAbb|originalName).*$//;
    my $label = _lineBreakMetaboliteNames($metName);
    #print STDERR "Label is '$label' for name '$metName'\n" if($metName!~m/^ENSG/);
    my @splitted = split(" name=", $line);
    my $lastPart = $splitted[1];
    $lastPart =~ s/^.*originalName/originalName/;
    $line = $splitted[0] . ' name="' . $label . '" ' . $lastPart;
    #print STDERR "For line '$line'\n" if($metName!~m/^ENSG/);
    $line =~ s/id=\"M_E/id=\"E/; # fix this!
    #print STDERR $line."\n";
    print $line . "\n";
  }
}

sub _printReactions{
  my ($reactionXML) = @_; # all the lines of the reaction
  my $line = <FILE>; # start reading the relevant lines
  while($line !~ m/^\s+\W\Wreaction\W/){
    $reactionXML .= $line;
    $line = <FILE>;
  }
  $reactionXML .= $line; # add the end reaction line as well...
  if($reactionXML =~ m/species=.M_m[0-9]+$compartmentToLookFor/){
    print $reactionXML;
  }
}

# these are hex code numbers!
# &#xb2; means subscript 2
# is a great resource > http://www.fileformat.info/info/unicode/char/1d62/index.htm
sub _lineBreakMetaboliteNames{
  my ($name) = @_;
  $name =~ s/alpha/&#x3B1;/g;
  $name =~ s/beta/&#x3B2;/g;
  $name =~ s/gamma/&#x3B3;/g;
  $name =~ s/hydroxy/OH/g;
  $name =~ s/H2/H&#x2082;/g; # fixes H2O2, H2O, FADH2
  $name =~ s/O2/O&#x2082;/g; # fixes H2O2, O2, CO2&#x2082;
  $name =~ s/H\+/H&#x207a;/g;
  $name =~ s/NAD\+/NAD&#x207a;/;
  $name =~ s/NADP\+/NADP&#x207a;/;
  $name =~ s/^Na\+/NA&#x207a;/;
  $name =~ s/^K\+/K&#x207a;/;
  $name =~ s/^Pi$/P&#x1d62;/;
  $name =~ s/^Pi pool$/P&#x1d62; pool/;
  $name =~ s/^PPi$/PP&#x1d62;/;
  my $ret = $name;
  #print STDERR "Return value is now '$ret'\n" if($name !~ m/ENSG/);
  my $minLength = 17;
  my $newLine = "&#xD;";
  if(length($name)>$minLength){
    $ret = "";
    my @chars = split("", $name);
    my $found = "";
    foreach my $char (@chars){
      if($char=~m/(-|,| )/ && length($found)>$minLength){
        $ret = $ret . $newLine . $found . $char;
        $found = ""; # reset to start collecting the next part
      }else{
        $found .= $char;
      }
    }
    if((length($found)>$minLength) && ($found=~m/-/)){
      my $rin = rindex($found, "-");
      $ret .= substr($found,0,$rin) . $newLine. substr($found,$rin);
    }else{
      $ret .= $newLine . $found; # add the last part as well :)
    }
    $ret =~ s/^$newLine//; # remove the first <BR>
  }
  #print STDERR "Returning '$ret'\n" if($name !~ m/ENSG/);
  return $ret;
}


sub readLabel{
  my ($fileName) = @_;
  open FILE, "<" . $fileName or die "not possible to open file '$fileName' for reading\n";
  while(my $line = <FILE>){
    chomp($line);
    my @cols = split(/\t/, $line);
    my $id = $cols[3];
    my $name = $cols[4];
    $reconAbb{$id} = $name;
  }
  close FILE;
}


sub _getMetID{
  my ($line) = @_;
  my $metId = $line;
  if($line=~m/M_m/){
    $metId =~ s/^.*id=.M_m/M_m/;
    $metId =~ s/\" .*$//;
  }else{
    $metId =~ s/^.*id=.M_E/E/;
    $metId =~ s/\" name.*$// if($line=~m/ENSG/);
  }
  return($metId);
}
