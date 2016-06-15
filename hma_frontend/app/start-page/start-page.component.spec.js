'use strict';

describe('startPage', function() {
  beforeEach(module('startPage'));

  describe('startPage', function() {
    it('should create a model with `name` set to `world`',
       inject(function($componentController) {
	 var ctrl = $componentController('startPage');

	 expect(ctrl.name).toBe("world");
       }));
  });
});
