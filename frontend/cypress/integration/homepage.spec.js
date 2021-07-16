/// <reference types="Cypress" />

context('Homepage', () => {

  describe('Basic', () => {
    it('Hide loading screen', () => {
      cy.visit('/')
      cy.get('#init-loading').should('not.exist')
    })
    it('Standard charset', () => {
      // https://on.cypress.io/document
      cy.document().should('have.property', 'charset').and('eq', 'UTF-8')
    })
    it('Cookie policy', () => {
      Cypress.Cookies.debug(true)
      // cy.getCookies().should('be.empty')
      cy.get('#cookies').should('be.visible')
      cy.get('#cookies').find('.button').click()
      cy.get('#cookies').should('not.exist')
    })
  })

  describe('Navbar', () => {
    it('Works in all screen sizes', () => {
      // cy.viewport(2999, 2999)
      cy.viewport('macbook-15')
      cy.get('.navbar-menu .is-active').should('not.exist')
      cy.get('.navbar-burger').should('be.hidden')
      cy.viewport('iphone-5')
      cy.get('.navbar-burger').should('be.visible')
      cy.get('.navbar-burger').click()
      cy.get('.navbar-burger .is-active').should('not.exist')
      cy.get('.navbar-end').children().should('have.length', 6)
      cy.get('.navbar-end .navbar-item').first().click()
    })
  })

  describe('Homepage banner', () => {
    it('Each item has image and footer', () => {
      cy.visit('/')
      cy.get('aside li').should('have.length', 9)
      cy.get('aside li').each(($el) => {
        cy.get($el).click()
        cy.get('#home').find('.is-v-aligned > a > .card > img').should('exist')
        cy.get('#home').find('.is-v-aligned > a > .card > footer').should('exist')
      })
    })
  })

  describe('News', () => {
    it('Valid links', () => {
      cy.visit('/')
      cy.get('#newsandcommunity').find('.card-content > p > a').each(($el) => {
        cy.wrap($el).should('have.attr', 'href')
        cy.wrap($el).click()
        cy.get('.navbar-brand').click()
      })
    })
  })

})
