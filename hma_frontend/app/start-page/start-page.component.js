'use strict';

function setName() {
  this.name = "foo";
}


function StartPageCtrl() {
  var vm = this;
  vm.name = "world";
  vm.set = setName;
}

angular.
  module('startPage').
  component('startPage', {
    templateUrl: 'start-page/start-page.template.html',
    controller: StartPageCtrl,
    controllerAs: '$ctrl'
  });

