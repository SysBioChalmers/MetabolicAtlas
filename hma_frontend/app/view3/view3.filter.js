angular.
  module('view3').
  filter('chemicalFormula', function($sce){
    return function(val){
      if(val){ // formula is empty for all the enzymes!
	return $sce.trustAsHtml(val.replace(/([0-9])/g,"<sub>\$1</sub>"));
      }
      return "";
    }
  }).
  filter('chemicalName', function($sce){
    return function(val){
      return $sce.trustAsHtml(val.replace(/(\+)/g,"<sup>\$1</sup>"));
    }
  }).
  filter('getProteinFunction', function($sce){
    return function(val){
      return $sce.trustAsHtml(val);
    }
  });
