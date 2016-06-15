'use strict';

function router ($locationProvider, $routeProvider) {
  $locationProvider.hashPrefix('!');

  $routeProvider.
    when('/', {
      template: '<start-page></start-page>'
    }).
    when('/view3', {
      template: '<view3></view3>'
    }).
    when('/view4', {
      template: '<view4></view4>'
    }).
    otherwise({redirectTo: '/'});
};

angular.
  module('hmaApp').
  config(['$locationProvider', '$routeProvider', router]);
