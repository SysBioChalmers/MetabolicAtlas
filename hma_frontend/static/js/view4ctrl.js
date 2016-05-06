app.controller('v4ElemsCtrl', [ '$scope', '$http', 'view4Graph', function( $scope, $http, view4Graph ){
    var cy; // mitght want a ref to cy
    // (usually better to have the srv as intermediary)
    $scope.elms = [];
    $scope.rels = [];
    $scope.enzymeName="ENSG00000164303"; //ENSG00000164303 and ENSG00000180011
    $http.defaults.headers.common['Authorization'] = 'Basic ' + window.btoa('hma' + ':' + 'K5U5Hxl8KG');
    var url = 'http://130.238.29.191/api/v1/enzymes/'+$scope.enzymeName+'/connected_metabolites?include_expressions=true';
    $http.get(url)
    .success(function(data, status, headers, config) {
        $scope.backend = data;
        console.log("Got the JSON from URL: "+url);
        //http://book.mixu.net/node/ch5.html
        //https://developer.mozilla.org/en/docs/Web/JavaScript/Reference/Global_Objects/Set
        //http://stackoverflow.com/questions/7958292/mimicking-sets-in-javascript
        var elms = [];
        var rels = [];
        var e = $scope.backend;
        var occ = {}; // occurences of each element, needed when assigning unique node ids
        var enzyme = {
            id: e.id,
            parentid: 'null',
            type: 'E',
            short: e.short_name,
            long: e.long_name,
            description: 'description',
            formula: 'formula',
            compartment: e.compartment
        };
        elms.push(enzyme);
        for( var i = 0; i < e.reactions.length; i++ ){
            var r = e.reactions[i];
            var reaction = {
                id: r.reaction_id,
                parentid: 'null',
                type: 'R',
                short: r.reaction_id,
                long: r.reaction_id,
                description: r.reaction_id,
                formula: r.reaction_id
            };
            elms.push(reaction);
            // add the enzyme - reaction as a link for the view4 graph
            var relation = {
                id: enzyme.id + '_' + reaction.id,
                source: enzyme.id,
                target: reaction.id
            };
            rels.push(relation);
            //var prs = r.products.concat(r.reactants);
            //for ( var im = 0; im < prs.length; im++ ){
            //    //reactionpool = [];
            //    var m = prs[im];
            //    var metabolite = {
            //        id: m.component_id,
            //        parentid: r.reaction_id,
            //        type: 'M',
            //        short: m.short_name,
            //        long: m.long_name,
            //        description: 'description',
            //        formula: m.formula,
            //        compartment: m.compartment
            //    };
            //    if (metabolite.id in occ){
            //        occ[metabolite.id]+=1;
            //        metabolite.id += '_'+occ[metabolite.id];
            //    }else{
            //        occ[metabolite.id]=1;
            //    }
            //    elms.push(metabolite);
            //};
            // go through the products
            for ( var im = 0; im < r.products.length; im++ ){
                var m = r.products[im];
                var metabolite = {
                    id: m.component_id,
                    parentid: r.reaction_id,
                    type: 'M',
                    short: m.short_name,
                    long: m.long_name,
                    description: 'description',
                    formula: m.formula,
                    compartment: m.compartment,
                    type: 'product'
                };
                if (metabolite.id in occ){
                    occ[metabolite.id]+=1;
                    metabolite.id += '_'+occ[metabolite.id];
                }else{
                    occ[metabolite.id]=1;
                }
                elms.push(metabolite);
            };
            // go through the reactants
            for ( var im = 0; im < r.reactants.length; im++ ){
                var m = r.reactants[im];
                var metabolite = {
                    id: m.component_id,
                    parentid: r.reaction_id,
                    type: 'M',
                    short: m.short_name,
                    long: m.long_name,
                    description: 'description',
                    formula: m.formula,
                    compartment: m.compartment,
                    type: 'reactant'
                };
                if (metabolite.id in occ){
                    occ[metabolite.id]+=1;
                    metabolite.id += '_'+occ[metabolite.id];
                }else{
                    occ[metabolite.id]=1;
                }
                elms.push(metabolite);
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
        view4Graph( $scope.elms, $scope.rels ).then(function( elmsCy ){
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
