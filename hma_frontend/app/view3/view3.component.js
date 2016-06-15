'use strict';

function generateGraph(updateFun, vm, elements, relations) {
  var json = [];
  for (var element_id in elements) {
    var element = elements[element_id];
    json.push({
      group: 'nodes',
      data: {
	id: element_id,
	name: element.short,
	type: element.type
      }
    });
  }
  for (var relation_id in relations) {
    var relation = relations[relation_id];
    json.push({
      group: 'edges',
      data: {
	id: relation_id,
	source: relation.source,
	target: relation.target
      }
    });
  }
  $(function() {
    var info = {};
    var cy = cytoscape({
      container: $('#cy')[0],

      style: cytoscape.stylesheet()
        .selector('node')
        .css({
          'content': 'data(name)',
          'font-size': "20px",
          //'height': 80,
          //'width': 'mapData(weight, 1, 200, 1, 200)',
          'text-valign': 'top',
          'text-halign': 'center'
          //'color': 'white',
          //'text-outline-width': 2,
          //'text-outline-color': '#888'
        })
        .selector('node[type="metabolite"]')
        .css({
          'shape': 'elipse',
          'background-color': '#00ff00',
          'width': 15,
          'height':15,
          'color': '#000000'
        })
        .selector('node[type="enzyme"]')
        .css({
          'shape': 'rectangle',
          'background-color': '#ff0000',
          'width': 20,
          'height':20,
          'color': '#000000'
        })
        .selector('edge')
        .css({
          'width': 3,
          'line-color': '#ccc',
          'target-arrow-color': '#ccc',
          'target-arrow-shape': 'triangle'
        })
        .selector(':selected')
        .css({
          'background-color': 'black',
          'line-color': 'black',
          'target-arrow-color': 'black',
          'source-arrow-color': 'black',
          'text-outline-color': 'black'
        }),
      layout: {
        name: 'random',
      },
      elements: json
    });
    cy.$('node').qtip({
      content: 'Remove<br />' +
	'Re-center view<br />' +
	'Only 1st level interactions<br />' +
	'Expand to 1st level interactions',
      position: {
        my: 'top center',
        at: 'bottom center'
      },
      style: {
        classes: 'qtip-bootstrap',
        tip: {
          width: 16,
          height: 8
        }
      }
    });
    cy.on('select', 'node', function(e) {
      vm.clickedNode = this.id();
      var node = vm.elements[vm.clickedNode];
      info['symbol'] = node.id;
      info['compartment'] = node.compartment;
      info['description'] = "";
      vm.infoSymbol = info.symbol;
      vm.infoCompartment = info.compartment;
      vm.infoDescription = info.description;
      updateFun();
    });
  });
}

function getInteractionPartners(reactionComponent, reactions) {
  var elements = {};
  var relations = {};
  elements[reactionComponent.component_id] =
    parseComponent(reactionComponent.component_id,
		   reactionComponent);
  for (var i = 0; i < reactions.length; i++) {
    var reaction = reactions[i];
    var modifiers = reaction.modifiers;
    var active_components = reaction.reactants.concat(reaction.products);
    var all_components = active_components.concat(modifiers);
    var parsed_components = parseComponents(reaction.id, all_components);
    var modifier_relations = getModifierRelations(modifiers, active_components);
    for (var relation_id in modifier_relations) {
      relations[relation_id] = modifier_relations[relation_id];
    }
    for (var j = 0; j < all_components.length; j++) {
      var component = all_components[j];
      var relation = {
	id: component.component_id + '_' + reactionComponent.component_id,
	source: component.component_id,
	target: reactionComponent.component_id
      }
      relations[relation.id] = relation
    }
    for (var component_id in parsed_components) {
      var component = parsed_components[component_id];
      elements[component_id] = component;
    }
  };
  return {'elements': elements, 'relations': relations};
}

function getModifierRelations(modifiers, components) {
  var relations = {}
  for (var i = 0; i < modifiers.length; i++) {
    var modifier = modifiers[i];
    for (var j = 0; j < components.length; j++) {
      var component = components[j];
      var relation = {
	id: modifier.component_id + '_' + component.component_id,
	source: modifier.component_id,
	target: component.component_id
      }
      relations[relation.id] = relation;
    }
  }
  return relations;
}

function parseComponents(reaction_id, components) {
  var parsed = {}
  for (var i = 0; i < components.length; i++) {
    var component = parseComponent(reaction_id, components[i]);
    parsed[component.id] = component;
  }
  return parsed;
}

function parseComponent(reaction_id, component) {
  return {
    id: component.component_id,
    type: component.type,
    short: component.short_name,
    long: component.long_name,
    description: 'description',
    formula: component.formula,
    compartment: component.compartment,
    reaction: reaction_id
  }
}

function getLevels() {
  // 1. filter enzymes
  // 2. for each enzyme, get expression levels

  // var promises = [];
  // var ids = [];
  // for (eid in vm.elms){
  //   var elem = vm.elms[eid];
  //   var t = new String(elem.type);
  //   if ( t == "enzyme"){
  //     var exprAPI = mainURL+"reaction_components/"+eid+"/expressions?tissue=adipose&expression_type=rnaseq";
  //     var promise = $http({method: 'GET', url: exprAPI, cache: 'true'});
  //     promises.push(promise);
  //     ids.push(eid);
  //   }
  // }
  // console.log(promises.length);
  // var xmax = 0;
  // var levels = {};

  // $q.all(promises).then(function(data2){
  //   //console.log(JSON.stringify(data2[0].data.expressions[0].level));
  //   for (var i = 0; i < promises.length; i++){
  //     var eid = ids[i];
  //     levels[eid] = data2[i].data.expressions[0].level;
  //   }
  //   //console.log(JSON.stringify(levels));
  //   vm.infoLevels = JSON.stringify(levels);

  // });
  return [];
}

function View3Ctrl($scope, $http, $q, backendService) {
  var vm = this;
  // FIXME: There must be a nicer way of doing this...
  var updateFun = function() {
    $scope.$apply();
  };

  vm.search = {
    rc: "E_3748",
    tissue: "adipose_tissue",
    expression: "antibody_profiling"
  };
  vm.rcexamples = "E_2571, E_3125";//display as search tips

  vm.dosearch = function(fsearch) {
    vm.search = angular.copy(fsearch);
    vm.elms = [];
    vm.rels = [];
    vm.reactionComponentID = vm.search.rc; //connecting Sergius and Lenas naming :)


    backendService.getReactionComponent("E_3748").then(function(result) {
      vm.component = result;
      backendService.
	getInteractionPartners(vm.component.component_id).
	then(function(result) {
	  vm.interaction_partners = getInteractionPartners(vm.component,
							   result.reactions);
	  vm.elements = vm.interaction_partners.elements;
	  vm.relations = vm.interaction_partners.relations;
	  generateGraph(updateFun, vm, vm.elements, vm.relations);
	  // TODO
	  //vm.infoLevels = getLevels();

	  vm.enzymeName = vm.component.short_name;
	  vm.enzymeFunction = "No known function in UniProt";
	  if(vm.enzymeName=="ENPP6"){
            vm.enzymeFunction = "Choline-specific glycerophosphodiester phosphodiesterase. The preferred substrate may be lysosphingomyelin (By similarity). Hydrolyzes lysophosphatidylcholine (LPC) to form monoacylglycerol and phosphorylcholine but not lysophosphatidic acid, showing it has a lysophospholipase C activity. Has a preference for LPC with short (12:0 and 14:0) or polyunsaturated (18:2 and 20:4) fatty acids. Also hydrolyzes glycerophosphorylcholine and sphingosylphosphorylcholine efficiently. Hydrolyzes the classical substrate for phospholipase C, p-nitrophenyl phosphorylcholine in vitro, while it does not hydrolyze the classical nucleotide phosphodiesterase substrate, p-nitrophenyl thymidine 5'-monophosphate. Does not hydrolyze diacyl phospholipids such as phosphatidylethanolamine, phosphatidylinositol, phosphatidylserine, phosphatidylglycerol and phosphatidic acid.";
            //vm.enzymeFunction = "Choline-specific glycerophosphodiester phosphodiesterase. ";
	  }else if(vm.enzymeName=="SULT1A3"){
            vm.enzymeFunction="Sulfotransferase that utilizes 3'-phospho-5'-adenylyl sulfate (PAPS) as sulfonate donor to catalyze the sulfate conjugation of phenolic monoamines (neurotransmitters such as dopamine, norepinephrine and serotonin) and phenolic and catechol drugs. </br><b>Catalytic activity:</b></br>3'-phosphoadenylyl sulfate + a phenol = adenosine 3',5'-bisphosphate + an aryl sulfate.";
	  }
	});
    });
  }; //dosearch
  vm.dosearch(vm.search);

};

angular.
  module('view3').
  component('view3', {
    templateUrl: 'view3/view3.template.html',
    controller: ['$scope', '$http', '$q', 'backendService', View3Ctrl],
    bindToController: true,
    bindings: {
      infoSymbol: '@',
      infoCompartment: '@',
      infoDescription: '@'
    }
  });
