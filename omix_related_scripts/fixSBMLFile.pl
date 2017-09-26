use strict;

my $fileName = $ARGV[0];

my %reactions;
_readECNumber("ReactionToMetabolite.txt");
my %reconAbb;
readLabel("labels.tab");
my %subsystems;
readPathwayInformation("subsystem.tab");
my %cofactors;
readSplitNodeInformation("currencyMets.csv");
my %modifications; my %modifiers; my @enzymes; my %enzymeNames;
readGeneAssociationsFromSBML2("../HMRdatabase2_00 2.xml");


my $rec_ID;
open FILE, "<" . $fileName or die "not possible to open '$fileName'\n";
while(my $line = <FILE>){
  if($line =~ m/species boundaryCondition/){
    _addAnnotationsToMetabolite($line);
  }elsif($line =~ m/\W\WlistOfSpecies\W/){
    # at the end of the list of species add all the enzymes as well...
    #_addAllEnzymes();
    print $line;
  }elsif($line =~ m/reaction fast/){
    $rec_ID = _addAnnotationsToReactions($line);
  }elsif($line =~ m/reaction/){
  #  print _addCoFactorsToReactions($rec_ID);
  #print STDERR "in here with line '$line'\n";
    _addGeneAssociationsToReaction($rec_ID);
    print $line;
  }else{
    print $line;
  }
}
close FILE;


sub _addAnnotationsToMetabolite{
  my ($line) = @_;
  chomp($line);
  my $metName = $line;
  $metName =~ s/^.*name=.//;
  $metName =~ s/. compartment.*$//;
  my $originalName = $metName;
  print STDERR "no label for '$metName'\n" if(!(exists($reconAbb{$metName})));
  my $metId = $line;
  $metId =~ s/^.*id=.M_/M_/;
  $metId =~ s/\W .*$//;
  my $n = $reconAbb{$metName};
  if($n =~ m/MISSING/ || (!(exists($reconAbb{$metName})))){
    $n = $metId; # so its apparent that this is MISSING!
  }
  if($metName =~ m/ENSG/){
    $metName = $n;
    $line =~ s/M\_E/E/; # fix this!
  }
  #print STDERR "metid is '$metId' from line '$line'\n";
  $line =~ s/name.*compartment/name=\"$metName\" originalName=\"$originalName\" reconAbb=\"$n\" metaid=\"_$metId\" compartment/;
  print $line . "\n";
}


sub _addAnnotationsToReactions{
  my ($line) = @_;
  chomp($line);
  my $rID = $line;
  $rID =~ s/^.*id=\W//;
  $rID =~ s/\W.*$//;
  my $reaction_id = $rID;
  $reaction_id =~ s/^R.//; # remove the R_ that ended up before the number of the SBML file...
  print STDERR "Reaction id is '$reaction_id'\n" if $reaction_id=~m/3905/;
  if(exists($reactions{$rID})){
    my $str = " metaid='_$rID'>\n";
    $str .= _addCoFactorsToReactions($reaction_id);
    $str .= "      	<annotation>\n";
    $str .= "      	  <rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'\n";
    $str .= "      	    xmlns:bqbiol='http://biomodels.net/biology-qualifiers/'>\n";
    $str .= "      	    <rdf:Description rdf:about='#_$rID'>\n";
    $str .= "      	      <bqbiol:is>\n";
    $str .= "      	        <rdf:Bag>\n";
    foreach my $ec (keys(%{$reactions{$rID}->{"EC"}})){
      $str .= "      	         <rdf:li rdf:resource='http://identifiers.org/ec-code/$ec'/>\n";
    }
    $str .= "      	       </rdf:Bag>\n";
    $str .= "      	      </bqbiol:is>\n";
    $str .= "      	    </rdf:Description>\n";
    $str .= "      	  </rdf:RDF>\n";
    $str .= "      	</annotation>\n";
    chop($line);  # remove the last chars
    print $line;
    print $str;
  }else{
  	#there are reactions that do not have an EC number, but of course they should still have annotation(s) if applicable!!!
  	my $str = " metaid='_$rID'>\n";
    $str .= _addCoFactorsToReactions($reaction_id);
    chop($line);  # remove the last chars
    print $line;
    print $str;
  }
  return($reaction_id);
}

sub _addCoFactorsToReactions{
  my ($reaction_id) = @_;
  my $str = "";
  $str .= "        <notes xmlns=\"http://www.w3.org/1999/xhtml\">\n";
  $str .= "          <p>SUBSYSTEM: $subsystems{$reaction_id}</p>\n";
  foreach my $cofactor (keys(%{$cofactors{$reaction_id}})){
    $str .= "          <p>COFACTOR: $cofactor</p>\n";
  }
  $str .= "        </notes>\n";
  return $str;
}

sub _addGeneAssociationsToReaction{
  my ($rec_ID) = @_;
  #print STDERR "in here with '$rec_ID' which is '$modifications{$rec_ID}'\n";
  if(length($modifications{$rec_ID})>1){
    my $to_print = "        ".$modifications{$rec_ID} . "\n";
    $to_print =~ s/.modifierSpeciesReference/\n          <modifierSpeciesReference/g;
    $to_print =~ s/<\WlistOfModifiers/\n        <\/listOfModifiers/;
    print $to_print;
  }
}

sub _addAllEnzymes{
  foreach my $e (@enzymes){
    print $e . "\n";
  }
}

# read annotation files...
#<rdf:li rdf:resource='http://identifiers.org/ec-code/"EC:1.1.1.1;EC:1.1.1.71"'/>
sub _readECNumber{
  my ($fileName) = @_;
  open FILE, "<" . $fileName or die "not possible to open '$fileName'\n";
  while(my $line = <FILE>){
    chomp($line);
    my @cols = split("\t", $line);
    my $reactionID = "R_" . $cols[0];
    my $ec = $cols[2];
    $ec =~ s/\"//g; # remove any starting/ending " from the text
    if(length($ec)>1){
      my @eTemp = split(";", $ec);
      foreach my $e (@eTemp){
        $e =~ s/^EC://; # to fit with the lookup function of identifiers.org
        $reactions{$reactionID}->{"EC"}->{$e} = 1;
      }
    }
  }
  close FILE;
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


# the pathway drawing requires the SUBSYSTEM information from the SBML version2 file...
sub readPathwayInformation{
  my ($fileName) = @_;
  open FILE, "<" . $fileName or die "not possible to open file '$fileName' for reading\n";
  while(my $line = <FILE>){
    chomp($line);
    my @cols = split(/\t/, $line);
    my $reaction_id = $cols[0];
    my $subsystem = $cols[1];
    $subsystems{$reaction_id} = $subsystem;
    print STDERR "Reaction id is '$reaction_id'\n" if $reaction_id=~m/3905/;
  }
  close FILE;
}

# it would be nice of the split nodes/cofactors/currency metabolites where added...
sub readSplitNodeInformation{
  my ($fileName) = @_;
  open FILE, "<" . $fileName or die "not possible to open file '$fileName' for reading\n";
  while(my $line = <FILE>){
    chomp($line);
    my @cols = split(",", $line);
    my $metabolite_id = $cols[0];
    for(my $colIndex=1; $colIndex < scalar(@cols); $colIndex++){
      $cofactors{$cols[$colIndex]}->{"M_".$metabolite_id} =1; # for each HMR reaction remember the metabolite(s) that are split nodes...
    }
  }
  close FILE;
}


# I need the gene associations and gene symbols found in the earlier sbml version....
sub readGeneAssociationsFromSBML2{
  my ($fileName) = @_;
  open FILE, "<" . $fileName or die "not possible to open file '$fileName' for reading\n";
  while(my $line = <FILE>){
    chomp($line);
    if($line =~ m/modifierSpeciesReference/){
      my $rID = $line; #<reaction metaid="metaid_R_HMR_3905" id="R_HMR_3905"
      $rID =~ s/^.*metaid=.metaid_R_//;
      $rID =~ s/\".*$//;
      # for each reaction get the whole line of modifier information ... <listOfModifiers>
      my $mod_info = $line;
      $mod_info =~ s/^.*\WlistOfModifiers\W\WmodifierSpeciesReference/<listOfModifiers><modifierSpeciesReference/;
      $mod_info =~ s/..listOfModifiers.*$/<\/listOfModifiers>/;
      #print STDERR "Adding rID '$rID' and mod '$mod_info'\n";
      $modifications{$rID} = $mod_info;
      # for each reaction get a list of the modifiers
      my @mods = split("modifierSpeciesReference",$line); #<modifierSpeciesReference species="E_3369"/>
      foreach my $mod (@mods){
        $mod =~ s/^.*species=.//;
        $mod =~ s/\".*$//;
        $modifiers{$rID}->{$mod} = 1;
      }
    }elsif($line =~ m/species.*ENSG/){
      # when I find an enzyme remember its name ... species metaid="metaid_E_2116 ... <p>SHORT NAME: ADHFE1</p>
      my $enzyme_id   = $line;
      my $enzyme_name = $line;
      $enzyme_id      =~ s/^.*metaid=.metaid_//;
      $enzyme_id      =~ s/\".*$//;
      $enzyme_name    =~ s/^.*SHORT NAME: //;
      $enzyme_name    =~ s/\W\Wp\W.*$//;
      push(@enzymes, $line);
      $enzymeNames{$enzyme_id} = $enzyme_name;
    }
  }
  close FILE;
}
