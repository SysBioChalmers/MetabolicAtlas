'use strict';

function getDefaultRequestParams() {
  return {
    method: "get",
    headers: {
      'Authorization': 'Basic ' + window.btoa('hma' + ':' + 'K5U5Hxl8KG')
    }
  }
}

angular.
  module('core.backend').
  service('backendService', function(HMA_SETTINGS, $http, $q) {
    var HMA_BASE_URL = HMA_SETTINGS.BASE_URL;

    return({
      getConnectedMetabolites: getConnectedMetabolites,
      getExpressions: getExpressions,
      getInteractionPartners: getInteractionPartners,
      getReactionComponent: getReactionComponent
    });

    function getConnectedMetabolites(enzyme_id) {
      var params = getDefaultRequestParams();
      params['url'] = HMA_BASE_URL + "/enzymes/" + enzyme_id +
	"/connected_metabolites";
      var request = $http(params);

      return(request.then(handleSuccess, handleError));
    }

    function getExpressions(enzyme_id) {
      var params = getDefaultRequestParams();
      params['url'] = HMA_BASE_URL + "/expressions/" + enzyme_id;
      var request = $http(params);

      return(request.then(handleSuccess, handleError));
    }

    function getInteractionPartners(component_id) {
      var params = getDefaultRequestParams();
      params['url'] = HMA_BASE_URL + "/reaction_components/" + component_id +
	"/interaction_partners";
      var request = $http(params);

      return(request.then(handleSuccess, handleError));
    }

    function getReactionComponent(component_id) {
      var params = getDefaultRequestParams();
      params['url'] = HMA_BASE_URL + "/reaction_components/" + component_id;
      var request = $http(params);

      return(request.then(handleSuccess, handleError));
    }

    function handleSuccess(response) {
      return response.data;
    }

    function handleError(response) {
      if(!angular.isObject(response.data) || !response.data.error) {
	return($q.reject("An unknown error occurred."));
      }
      else {
	return($q.reject(response.data.error));
      }
    }
  });
