
var app = angular.module('app', []);

app.factory('searchResults', [ '$q', function( $q ){
  var searchResults = function(elms){
    var deferred = $q.defer();
    return deferred.promise;
  };

  searchResults.listeners = {};

  function fire(e, args){
    var listeners = searchResults.listeners[e];

    for( var i = 0; listeners && i < listeners.length; i++ ){
      var fn = listeners[i];

      fn.apply( fn, args );
    }
  }

  function listen(e, fn){
    var listeners = searchResults.listeners[e] = searchResults.listeners[e] || [];

    listeners.push(fn);
  }

  searchResults.onSelected = function(fn){
    listen('onSelected', fn);
  };

  return searchResults;


} ]);
