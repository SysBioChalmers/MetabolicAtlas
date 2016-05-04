app.controller('searchResultsCtrl', [ '$scope', '$http', 'searchResults', function( $scope, $http, searchResults ){
    $scope.name="";

    $scope.searching = function(toSearchFor){
      $scope.name = toSearchFor;
      $scope.LoadData();
    };

    $scope.LoadData = function(){

      $http.defaults.headers.common['Authorization'] = 'Basic ' + window.btoa('hma' + ':' + 'K5U5Hxl8KG');
      $http.get('http://130.238.29.191/api/v1/reaction_components?name='+$scope.name)
      .success(function(data, status, headers, config) {
          $scope.backend = data;
          console.log("Got the JSON for "+$scope.name);
          var elms = [];
          var e = $scope.backend;
          for( var i = 0; i < e.reaction_components.length; i++ ){
            var c = e.reaction_components[i];
            var rc = {
              id: c.component_id,
              type: c.type,
              short: c.short_name,
              long: c.long_name,
              description: "description",
              formula: c.formula,
              compartment: c.compartment
            };
            elms.push(rc);
          };
          $scope.elms = elms;

          searchResults( $scope.elms );

      }).error(function(error, status, headers, config) {
        console.log(status);
        console.log("Error occured");
      });
    };

    if($scope.name!=""){
      $scope.LoadData();
    }


  $scope.onSelected = function(elem){
     //Nothing happens right now
  };

} ]);
