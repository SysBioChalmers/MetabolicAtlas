
var app = angular.module('app', []);

app.factory('view3Graph', [ '$q', function( $q ){
  var cy;
  var view3Graph = function(elms, rels){
    var deferred = $q.defer();

    var elmsjson = [];
    for( i in elms ){
        elmsjson.push({
            group: 'nodes',
            data: {
                id: elms[i].id,
                name: elms[i].short,
                type: elms[i].type
            }
        });
    };

    for( i in rels ){
      elmsjson.push({
        group: 'edges',
        data: {
          id: rels[i].id,
          source: rels[i].source,
          target: rels[i].target
        }
      });
    }

    console.log('view3 cy json:'+JSON.stringify(elmsjson));

    $(function(){ // on dom ready

      cy = cytoscape({
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
          name: 'random'
        },

        elements: elmsjson,

        ready: function(){
          deferred.resolve( this );
        }
      });
      cy.qtip({
        content: 'Remove<br>Re-center view<br>Only 1st level interactions<br>Expand to 1st level interactions',
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
    }); // on dom ready

    return deferred.promise;
  };

  view3Graph.listeners = {};

  function fire(e, args){
    var listeners = view3Graph.listeners[e];

    for( var i = 0; listeners && i < listeners.length; i++ ){
      var fn = listeners[i];

      fn.apply( fn, args );
    }
  }

  function listen(e, fn){
    var listeners = view3Graph.listeners[e] = view3Graph.listeners[e] || [];

    listeners.push(fn);
  }

  view3Graph.onSelected = function(fn){
    listen('onSelected', fn);
  };

  return view3Graph;


} ]);
