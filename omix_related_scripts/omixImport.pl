use strict;

# for the omix import we will highlight the metabolites that occur in a transporter reaction by size!

my $compartmentFile = $ARGV[0];
my $compartmentToLookFor = $ARGV[1];
my $hmrfile = $ARGV[2];

my %all_metabolites;
my %nonCompartmentMetabolites;
my %transportReactionMetabolites; # all metabolites that occur in the reactions that have a metabolite that is transported across a compartment
my %metabolitesTransported; # the metabolites that are physically transported out/in of the compartment
my %all_enzymes;

_readHMRModel($hmrfile);
_findAllTransports($compartmentFile);
writeInfo($compartmentFile);


sub writeInfo{
  my ($fileName) = @_;
  open FILE, "<" . $fileName or die "not possible to open file '$fileName'\n";
  my $header = <FILE>; # xml file specification
  print $header;
  my $include = <FILE>; # sbml include statements
  chop($include); chop($include);
  $include .= ' xmlns:layout="http://www.sbml.org/sbml/level3/version1/layout/version1">\n';
  print $include;
  while(my $line = <FILE>){
    #print STDERR "line is '$line'\n";
    if($line =~ m/<\WlistOfSpecies\W/){
      foreach my $met (keys(%nonCompartmentMetabolites)){
        print $all_metabolites{$met} . "\n";
      }
    }
    print $line;
    if($line =~ m/<\WlistOfReactions\W/){
      _addLayoutInformation();
    }
  }
  close FILE;
}

#                <layout:dimensions layout:height="40.0" layout:width="60.0"/>
sub _addLayoutInformation{
  # add the layout in which I fake a position but make the transporter metabolites larger....
  my $layoutInformation = '    <layout:listOfLayouts>
      <layout:layout layout:id="DefaultLayout">
        <layout:dimensions layout:height="640.0" layout:width="660.0"/>
          <layout:listOfSpeciesGlyphs>';
  foreach my $met (keys(%metabolitesTransported)){
    if($met !~ m/M_/){
      print STDERR "not a recognised metabolite, was '$met'\n";
    }
    $layoutInformation .= _addLayoutForSpecies($met, "-409.0", "-386.0");
  }
  foreach my $enzyme (keys(%all_enzymes)){
    $layoutInformation .= _addLayoutForSpecies($enzyme, "-409", "-200.0");
  }
  $layoutInformation .= '
          </layout:listOfSpeciesGlyphs>
      </layout:layout>
    </layout:listOfLayouts>
';
  print $layoutInformation;
}

sub _addLayoutForSpecies{
  my ($id, $posX, $posY) = @_;
  return('
          <layout:speciesGlyph layout:id="SpeciesGlyph_'.$id.'" layout:species="'.$id.'">
            <layout:boundingBox>
              <layout:position layout:x="'.$posX.'" layout:y="'.$posY.'"/>
            </layout:boundingBox>
          </layout:speciesGlyph>');
}



# first read the compartment sbml file so that I can find all non compartment metabolites
sub _findAllTransports{
  my ($fileName) = @_;
  open FILE, "<" . $fileName or die "not possible to open file '$fileName'\n";
  my %metabolitesForThisReaction; my $isTransportReaction = 0;
  while(my $line = <FILE>){
    if($line =~ m/speciesReference/){
      my $metId = _getMetID($line);
      if($line !~ m/species="M_m[0-9]+$compartmentToLookFor/){
        $nonCompartmentMetabolites{$metId} = 1;
        $isTransportReaction = 1;
        my $metIdForThisCompartment = $metId;
        #print STDERR "Met id is 1: '$metIdForThisCompartment'\t";
        chop($metIdForThisCompartment);
        #print STDERR "Met id is 2: '$metIdForThisCompartment'\t";
        $metIdForThisCompartment .= $compartmentToLookFor;
        #print STDERR "Met id is 3: '$metIdForThisCompartment'\n";
        if(exists($all_metabolites{$metIdForThisCompartment})){
          #print STDERR "Found for '$metIdForThisCompartment' was originally '$metId'\n";
          $metabolitesTransported{$metIdForThisCompartment} = 1;
        }
      }
      $metabolitesForThisReaction{$metId} = 1;
    }elsif($line =~ m/reaction fast/){
      if($isTransportReaction){
        foreach my $met (keys(%metabolitesForThisReaction)){
          $transportReactionMetabolites{$met} = 1;
        }
      }
      %metabolitesForThisReaction = {}; # clear the hash of metabolites....
    }
    # remember all enzymes
    if($line =~ m/species boundaryCondition/){
      my $metId = _getMetID($line);
      #print STDERR "Line is $line which results in met id $metId\n";
      $all_enzymes{$metId} = 1 if($metId=~m/^E/);
    }
  }
  # deal with the last reaction....
  if($isTransportReaction){
    foreach my $met (keys(%metabolitesForThisReaction)){
      $transportReactionMetabolites{$met} = 1;
    }
  }
  close FILE;
}

# read the original model so I get all metabolites!
sub _readHMRModel{
  my ($fileName) = @_;
  open FILE, "<" . $fileName or die "not possible to open file '$fileName'\n";
  while(my $line = <FILE>){
    if($line =~ m/species boundaryCondition/){
      chomp($line);
      my $metId = _getMetID($line);
      $all_metabolites{$metId} = $line; # remember all metabolites so I can properly deal with transporter reactions...
    }
  }
  close FILE;
}

sub _getMetID{
  my ($line) = @_;
  chomp($line);
  my $metId = $line;
  if($line=~m/M_m/){
    $metId =~ s/^.*(id|species)=.M_m/M_m/;
    $metId =~ s/\" .*$//;
  }else{
    $metId =~ s/^.*id=.(M_|)E/E/;
    $metId =~ s/\" name.*$//;
  }
  return($metId);
}
