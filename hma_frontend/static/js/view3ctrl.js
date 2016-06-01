app.controller('v3ElemsCtrl', [ '$scope', '$http', '$q', 'view3Graph', function( $scope, $http, $q, view3Graph ){
  $scope.search = {rc: "E_3748", tissue: "adipose_tissue", expression: "antibody_profiling"};
  $scope.rcexamples = "E_2571, E_3125";//display as search tips

  var mainURL="http://130.238.29.194/api/v1/";

  $scope.dosearch = function(fsearch) {
    $scope.search = angular.copy(fsearch);
    var cy; // might want a ref to cy
    // (usually better to have the srv as intermediary)
    // the $scope variables are 'visible' by the .html page
    $scope.elms = [];
    $scope.rels = [];
    //$scope.reactionComponentID="E_3125"; // gene symbol ZADH2 and uniprot Q8N4Q0 (ZADH2_HUMAN)
    //$scope.reactionComponentID="M_m02040s"; // gene symbol ZADH2 and uniprot Q8N4Q0 (ZADH2_HUMAN)
    //$scope.reactionComponentID="E_2571"; // gene symbol ENPP6 - only directly connected metabolites!
    //$scope.reactionComponentID="E_3749"; // gene symbol NOS2P1 - no uniprot!!!
    //$scope.reactionComponentID="E_3748"; // ENSG00000261052: gene symbol SULT1A3 and uniprot P0DMM9 (ST1A3_HUMAN)
    // http://130.238.29.194/api/v1/reaction_components/E_3125/interaction_partners
    // http://130.238.29.194/api/v1/reaction_components/M_m02040s/interaction_partners
    // http://130.238.29.194/api/v1/reaction_components/E_2571/interaction_partners
    $scope.reactionComponentID = $scope.search.rc; //connecting Sergius and Lenas naming :)

    //first get enzyme data
    $http.defaults.headers.common['Authorization'] = 'Basic ' + window.btoa('hma' + ':' + 'K5U5Hxl8KG');
    urlMainEnzyme = mainURL+'reaction_components/'+$scope.reactionComponentID;
    //http://130.238.29.194/api/v1/reaction_components/E_2571
    $http.get(urlMainEnzyme)
    .success(function(dataOuter, statusOuter, headersOuter, configOuter) {
      $scope.backend = dataOuter;
      console.log("Got the JSON from url "+urlMainEnzyme);
      var e = $scope.backend;
      var elms = {};
      var rels = {};
      var enzyme = {
          id: e.component_id,
          type: 'enzyme',
          short: e.short_name,
          long: e.long_name,
          description: 'description',
          formula: e.formula,
          compartment: e.compartment
      };
      elms[$scope.reactionComponentID] = enzyme;
      $scope.enzymeName = enzyme.short;
      $scope.enzymeFunction = "No known function in UniProt";
      if($scope.enzymeName=="ENPP6"){
        $scope.enzymeFunction = "Choline-specific glycerophosphodiester phosphodiesterase. The preferred substrate may be lysosphingomyelin (By similarity). Hydrolyzes lysophosphatidylcholine (LPC) to form monoacylglycerol and phosphorylcholine but not lysophosphatidic acid, showing it has a lysophospholipase C activity. Has a preference for LPC with short (12:0 and 14:0) or polyunsaturated (18:2 and 20:4) fatty acids. Also hydrolyzes glycerophosphorylcholine and sphingosylphosphorylcholine efficiently. Hydrolyzes the classical substrate for phospholipase C, p-nitrophenyl phosphorylcholine in vitro, while it does not hydrolyze the classical nucleotide phosphodiesterase substrate, p-nitrophenyl thymidine 5'-monophosphate. Does not hydrolyze diacyl phospholipids such as phosphatidylethanolamine, phosphatidylinositol, phosphatidylserine, phosphatidylglycerol and phosphatidic acid.";
        //$scope.enzymeFunction = "Choline-specific glycerophosphodiester phosphodiesterase. ";
      }else if($scope.enzymeName=="SULT1A3"){
        $scope.enzymeFunction="Sulfotransferase that utilizes 3'-phospho-5'-adenylyl sulfate (PAPS) as sulfonate donor to catalyze the sulfate conjugation of phenolic monoamines (neurotransmitters such as dopamine, norepinephrine and serotonin) and phenolic and catechol drugs. </br><b>Catalytic activity:</b></br>3'-phosphoadenylyl sulfate + a phenol = adenosine 3',5'-bisphosphate + an aryl sulfate.";
      }

    //then get the actual interaction partners....
    $http.defaults.headers.common['Authorization'] = 'Basic ' + window.btoa('hma' + ':' + 'K5U5Hxl8KG');
    $scope.API = urlMainEnzyme+'/interaction_partners';
    $http.get($scope.API)
    .success(function(data, status, headers, config) {
        $scope.backend = data;
        console.log("Got the JSON from url "+$scope.API);
        //http://book.mixu.net/node/ch5.html
        //https://developer.mozilla.org/en/docs/Web/JavaScript/Reference/Global_Objects/Set
        //http://stackoverflow.com/questions/7958292/mimicking-sets-in-javascript

        var b = $scope.backend;
        for( var i = 0; i < b.reactions.length; i++ ){
            var r = b.reactions[i];
            var mods = {};
            for (im = 0; im < r.modifiers.length; im++){
                var m = r.modifiers[im];
                var modifier = {
                    id: m.component_id,
                    type: m.type,
                    short: m.short_name,
                    long: m.long_name,
                    description: 'description',
                    formula: m.formula,
                    compartment: m.compartment,
                    reaction: r.reaction_id
                };
                mods[modifier.id] = modifier;
            };
            var mets = {};
            var marr = r.products.concat(r.reactants);
            for (im = 0; im < marr.length; im++){
                var m = marr[im];
                var metabolite = {
                    id: m.component_id,
                    type: m.type,
                    short: m.short_name,
                    long: m.long_name,
                    description: 'description',
                    formula: m.formula,
                    compartment: m.compartment,
                    reaction: r.reaction_id
                };
                mets[metabolite.id] = metabolite;
            };
            //console.log('mods json:'+JSON.stringify(mods));
            //console.log('mets json:'+JSON.stringify(mets));
            //Now update the elements and relationships
            for (var eid in mods){
                if (!(eid in elms)){
                    elms[eid] = mods[eid];
                }
            };
            for (var eid in mets){
                if (!(eid in elms)){
                    elms[eid] = mets[eid];
                }
            };
            //console.log('elms json:'+JSON.stringify(elms));

            // loop through all modifiers and all metabolites, and connect the ones in the same reactions....
            for (eid_mo in mods){
                for (eid_me in mets){
                    var relation = {
                        id: eid_mo + '_' + eid_me,
                        source: eid_mo,
                        target: eid_me
                    };
                    if (!( relation.id in rels)) {
                      if( eid_mo.reaction == eid_me.reaction){
                        rels[relation.id] = relation;
                      }
                    };
                };
            };
            // add a relation to everything from the main reactionComponentID as well...
            for (eid_mo in mods){
              var relation = {
                  id: eid_mo + '_' + $scope.reactionComponentID,
                  target: eid_mo,
                  source: $scope.reactionComponentID
              };
              rels[relation.id] = relation;
            }
            for (eid_me in mets){
              var relation = {
                  id: eid_me + '_' + $scope.reactionComponentID,
                  target: eid_me,
                  source: $scope.reactionComponentID
              };
              rels[relation.id] = relation;
            }
        };

        $scope.elms = elms;
        $scope.rels = rels;

        var elmsById = {};
        for( var i = 0; i < $scope.elms.length; i++ ){
          var node = $scope.elms[i];
          elmsById[ node.id ] = node;
        }
        $scope.elmsById = elmsById;

        var promises = [];
        var ids = [];
        for (eid in $scope.elms){
          var elem = $scope.elms[eid];
          var t = new String(elem.type);
          if ( t == "enzyme"){
            var exprAPI = mainURL+"reaction_components/"+eid+"/expressions?tissue=adipose&expression_type=rnaseq";
            var promise = $http({method: 'GET', url: exprAPI, cache: 'true'});
            promises.push(promise);
            ids.push(eid);
          }
        }
        console.log(promises.length);
        var xmax = 0;
        var levels = {};

        $q.all(promises).then(function(data2){
          //console.log(JSON.stringify(data2[0].data.expressions[0].level));
          for (i = 0; i < promises.length; i++){
            var eid = ids[i];
            levels[eid] = data2[i].data.expressions[0].level;
          }
          //console.log(JSON.stringify(levels));
          $scope.infoLevels = JSON.stringify(levels);

          // for (i = 0; i < promises.length; i++){
          //   var eid = ids[i];
          //   var ex = data2[i].data.expressions;
          //   //console.log(JSON.stringify(data2[i].data);
          //   var elem = $scope.elms[eid];
          //   var t = new String(elem.type);
          //   if ( t == "enzyme"){
          //     $scope.elms[eid].level = parseInt(ex[1].level);
          //     levels.push(parseInt(ex[1].level));
          //     if ($scope.elms[eid].level > xmax) {xmax = $scope.elms[eid].level;};
          //   }
          // }
        	//console.log(data2[0], data2[1]);
        });
        //console.log(levels);

        // //not working, i must combine promises with $q deferral
        // //https://www.jonathanfielding.com/combining-promises-angular/
        // console.log($scope.elms);
        // var xmax = 0;
        // for (eid in $scope.elms){
        //   var elem = $scope.elms[eid];
        //   console.log(elem.type + ' ' + elem.type === "enzyme");
        //   var t = new String(elem.type);
        //   if ( t == "enzyme"){
        //     //http://130.238.29.194/api/v1/reaction_components/E_3125/expressions?tissue=adipose&expression_type=rnaseq
        //     $scope.exprAPI = "http://130.238.29.194/api/v1/reaction_components/"+eid+"/expressions?tissue=adipose&expression_type=rnaseq";
        //     $http.get($scope.exprAPI)
        //     .success(function(data2, status2, headers2, config2) {
        //       console.log(eid + ' ' + JSON.stringify(data2));
        //       if (!(jQuery.isEmptyObject(data2))){
        //         console.log($scope.exprAPI + ' passed');
        //         elem.level = data2.expressions[1].level;
        //         $scope.elms[eid] = elem;
        //         if (elem.level > xmax) {xmax = elem.level;};
        //       }else{
        //         $scope.elms[eid].level = 0;
        //       }
        //
        //     }).error(function(error2, status2, headers2, config2) {
        //       console.log(status);
        //       console.log("Error occured fetching for" + eid);
        //     });
        //   }else{
        //     $scope.elms[eid].level = 0;
        //   }
        // }
        // //just trying to get the color scaling factor instead of the expression level
        // for (eid in $scope.elms){
        //   if ($scope.elms[eid].type == "enzyme"){
        //     $scope.elms[eid].level = (xmax - $scope.elms[eid].level)/xmax;
        //     console.log(eid + ' ' + $scope.elms[eid].level);
        //   }
        // }



        // might want some ui to prevent use of this controller until cy is loaded
        view3Graph( $scope.elms, $scope.rels ).then(function( elmsCy ){
          cy = elmsCy;

          // hide ui until cy loaded
          $scope.cyLoaded = true;

          cy.on('select', 'node', function(e){
            $scope.clickedNode = this.id();
            console.log($scope.elms);
            var elem = $scope.elms[this.id()];
            $scope.infoSymbol = elem.short;
            $scope.infoCompartment = elem.compartment;
            $scope.infoDescription = "";
            $scope.$apply();
          });

        });

    }).error(function(error, status, headers, config) {
        console.log(status);
        console.log("Error occured");
        console.log(error);
    });
  });


}; //dosearch
$scope.dosearch($scope.search);

} ]);
