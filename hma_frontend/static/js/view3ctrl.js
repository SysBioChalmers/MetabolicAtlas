app.controller('v3ElemsCtrl', [ '$scope', '$http', 'view3Graph', function( $scope, $http, view3Graph ){
    var cy; // mitght want a ref to cy
    // (usually better to have the srv as intermediary)
    $scope.elms = [];
    $scope.rels = [];
    $scope.reactionComponentID="E_3125"; // gene symbol ZADH2 and uniprot Q8N4Q0 (ZADH2_HUMAN)
    $scope.reactionComponentID="M_m02040s"; // gene symbol ZADH2 and uniprot Q8N4Q0 (ZADH2_HUMAN)
    $scope.reactionComponentID="E_2571"; // gene symbol ENPP6 - only directly connected metabolites!
    $scope.reactionComponentID="E_3749"; // gene symbol NOS2P1 - no uniprot!!!
    $scope.reactionComponentID="E_3748"; // ENSG00000261052: gene symbol SULT1A3 and uniprot P0DMM9 (ST1A3_HUMAN)
    $http.defaults.headers.common['Authorization'] = 'Basic ' + window.btoa('hma' + ':' + 'K5U5Hxl8KG');
    $http.get('http://130.238.29.191/api/v1/reaction_components/'+$scope.reactionComponentID+'/interaction_partners')
    .success(function(data, status, headers, config) {
        $scope.backend = data;
        console.log("Got the JSON");
        //http://book.mixu.net/node/ch5.html
        //https://developer.mozilla.org/en/docs/Web/JavaScript/Reference/Global_Objects/Set
        //http://stackoverflow.com/questions/7958292/mimicking-sets-in-javascript
        var elms = {};
        var rels = {};
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
                    compartment: m.compartment
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
                    compartment: m.compartment
                };
                mets[metabolite.id] = metabolite;
            };
            console.log('mods json:'+JSON.stringify(mods));
            console.log('mets json:'+JSON.stringify(mets));
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
            console.log('elms json:'+JSON.stringify(elms));
            for (eid_mo in mods){
                for (eid_me in mets){
                    var relation = {
                        id: eid_mo + '_' + eid_me,
                        source: eid_mo,
                        target: eid_me
                    };
                    if (!( relation.id in rels)) {
                        rels[relation.id] = relation;
                    };
                };
            };
        };

        $scope.elms = elms;
        $scope.rels = rels;

        var elmsById = {};
        for( var i = 0; i < $scope.elms.length; i++ ){
          var node = $scope.elms[i];
          elmsById[ node.id ] = node;
        }

        // might want some ui to prevent use of this controller until cy is loaded
        view3Graph( $scope.elms, $scope.rels ).then(function( elmsCy ){
          cy = elmsCy;

          // hide ui until cy loaded
          $scope.cyLoaded = true;
        });

    }).error(function(error, status, headers, config) {
        console.log(status);
        console.log("Error occured");
    });

  /*
  // test versions of the elements and relationships
  $scope.elms = [
    { id: 'e1', parentid: 'null', type:'E', short:'E1', long:'long E1', description:'super long E1', formula: 'E1f' },
    { id: 'r1', parentid: 'null', type:'R', short:'R1', long:'long R1', description:'super long R1', formula: 'R1f' },
    { id: 'r2', parentid: 'null', type:'R', short:'R2', long:'long R2', description:'super long R2', formula: 'R2f' },
    { id: 'm1', parentid: 'r1', type:'M', short:'M1', long:'long M1', description:'super long M1', formula: 'M1f' },
    { id: 'm2', parentid: 'r1', type:'M', short:'M2', long:'long M2', description:'super long M2', formula: 'M2f' },
    { id: 'm3', parentid: 'r2', type:'M', short:'M3', long:'long M3', description:'super long M3', formula: 'M3f' },
    { id: 'm4', parentid: 'r2', type:'M', short:'M1', long:'long M1', description:'super long M1', formula: 'M1f' }
  ];

  $scope.rels = [
    { id: 'e1_r1', source: 'e1', target: 'r1' },
    { id: 'e1_r2', source: 'e1', target: 'r2' }
  ];
  */



  $scope.onSelected = function(elem){
     //Nothing happens rite now
  };

} ]);
