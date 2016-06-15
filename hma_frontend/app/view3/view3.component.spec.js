'use strict';

describe('view3', function() {
  beforeEach(function() {
    module('view3'),
    module('hmaApp')
  });

  describe('view3', function() {
    it('should have an example search',
       inject(function($componentController) {
	 var ctrl = $componentController('view3');
	 var expected = {
	   rc: "E_3748",
	   tissue: "adipose_tissue",
	   expression: "antibody_profiling"
	 };
	 expect(ctrl.search).toEqual(expected);
       }));
  });
});
