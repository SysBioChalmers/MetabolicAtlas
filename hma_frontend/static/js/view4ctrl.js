app.controller('v4ElemsCtrl', [ '$scope', '$http', 'view4Graph', function( $scope, $http, view4Graph ){

  $scope.search = {rc: "ENSG00000180011", tissue: "adipose_tissue", expression: "antibody_profiling"};

  $scope.rcexamples = "ENSG00000180011, ?";//display as search tips

  $scope.API = "http://130.238.29.194/api/v1/enzymes/ENSG00000180011/connected_metabolites?include_expressions=true";

  $scope.dosearch = function(fsearch) {
    $scope.search = angular.copy(fsearch);
    //$scope.API = "http://130.238.29.194/api/v1/reaction_components/E_2571/interaction_partners";
    $scope.API = "http://130.238.29.194/api/v1/enzymes/"+$scope.search.rc+"/connected_metabolites?include_expressions=true";

    var cy; // might want a ref to cy
    // (usually better to have the srv as intermediary)
    $scope.elms = [];
    $scope.rels = [];
    $scope.enzymeName="ENSG00000164303"; //ENSG00000164303 and ENSG00000180011
    $http.defaults.headers.common['Authorization'] = 'Basic ' + window.btoa('hma' + ':' + 'K5U5Hxl8KG');
    $http.get($scope.API)
    .success(function(data, status, headers, config) {
        $scope.backend = data;
        console.log("Got the JSON from URL: "+$scope.API);
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
                formula: 'formula'
            };
            elms.push(reaction);
            // add the enzyme - reaction as a link for the view4 graph
            var relation = {
                id: enzyme.id + '_' + reaction.id,
                source: enzyme.id,
                target: reaction.id
            };
            rels.push(relation);

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
          cy.on('select', 'node', function(e){
            $scope.clickedNode = this.id();
            console.log('selected ' + this.id());
            //var elem = $scope.elms[this.id()]; //TODO: will currently fail because the same metabolite is in multiple places
            $scope.infoSymbol = this.id();
            $scope.infoDescription = "";
            $scope.$apply();
          });
        });

    }).error(function(error, status, headers, config) {
        console.log(status);
        console.log("Error occured");
    });

  }; //dosearch
  $scope.dosearch($scope.search);
} ]);
