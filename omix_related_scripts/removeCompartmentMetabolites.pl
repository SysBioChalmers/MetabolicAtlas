use strict;


my $fileName = $ARGV[0];
my $compartmentToRemove = $ARGV[1];
my $found = 0;

# 2 loop through the SBML file and see if there is a metabolite specified in the compartment, if so remove it
open FILE, "<" . $fileName or die "not possible to open file '$fileName'\n";
my @lines = <FILE>;
close FILE;
open OUT, ">" . $fileName;
for(my $i=0; $i<scalar(@lines); $i++){
  my $line = $lines[$i];
  if($line =~ m/<species.*M_m/ && $line=~m/compartment=.$compartmentToRemove/){
  	#print STDERR "To remove this line '$line'";
  }elsif($line =~ m/notes xmlns=/){
  	#print STDERR "To manipulate this line '$line'";
  	print OUT "        <notes>\n";
  }else{
    print OUT $line;
    if($line =~ m/speciesReference.*species=.M_m[0-9]+$compartmentToRemove/){
    	#print STDERR "Ensure this reaction is removed $line\n";
    	$found++;
	}
   }
}
close OUT;

print "In total $found number of speciesReferences are found in reactions\n";

# read in the lines again so that the above changes are included...
open FILE, "<" . $fileName or die "not possible to open file '$fileName'\n";
my @newlines = <FILE>;
close FILE;

### test to actually remove the reaction info and not simply counting it...
_removeReactions($fileName);


sub _removeReactions{
  my ($fName) = @_;
  open REMOVED, ">" . $fName or die "not possible to open file '$fName'\n";
  my $str = ""; my $isReaction = 0; my $doNotPrintThisReaction = 0; # remember the reaction lines as specifics
  for(my $i=0; $i<scalar(@newlines); $i++){
  	my $line = $newlines[$i];
    if($line =~ m/reaction fast/){
    	$str .= $line;
    	$isReaction = 1;
    }elsif($isReaction){
    	$str .= $line;
    	if($line =~ m/reaction/){
    		print REMOVED $str if(! $doNotPrintThisReaction);
    		# reset the "memory"
    		$str =  "";
    		$isReaction = 0;
    		$doNotPrintThisReaction = 0;
    	}elsif($line =~ m/speciesReference.*species=.M_m[0-9]+$compartmentToRemove/){
    		$doNotPrintThisReaction = 1;
    	}
    }else{
    	print REMOVED $line;
    }
  }
  close REMOVED;
}