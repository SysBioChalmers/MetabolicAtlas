'use strict';

describe('HMA Frontend App', function() {
  it('should redirect `index.html` to `/`', function() {
    browser.get('index.html');
    expect(browser.getLocationAbsUrl()).toBe('/');
  });

  describe('Start page', function() {
    beforeEach(function() {
      browser.get('/');
    });

    it('should display `world`', function() {
      var heading = element.all(by.css('h1')).first();

      expect(heading.getText()).toContain("world");
    });
  });

  describe('View 3', function() {

  });

  describe('View 4', function() {

  });
});
