Cypress.config('defaultCommandTimeout', 10000);

describe('Homepage', () => {
  it('should load the homepage and display the correct title', () => {
    cy.visit('http://localhost:3000'); 
    cy.title().should('include', 'CodeSmile'); 
    cy.get('h1').should('contain', 'Welcome to CodeSmile Web-App');
  });

  it('should navigate to the upload-python page when "Analyze Python Code" button is clicked', () => {
    cy.visit('http://localhost:3000');
    cy.contains('Analyze Python Code').click(); 
    cy.url().should('include', '/upload-python'); 
  });

  it('should navigate to the upload-project page when "Analyze Project" button is clicked', () => {
    cy.visit('http://localhost:3000');
    cy.contains('Analyze Project').click();
    cy.url().should('include', '/upload-project');
  });

  it('should navigate to the reports page when "Generate Reports" button is clicked', () => {
    cy.visit('http://localhost:3000');
    cy.contains('Generate Reports').click();
    cy.url().should('include', '/reports');
  });

  it('should navigate to the about page when "About CodeSmile" button is clicked', () => {
    cy.visit('http://localhost:3000');
    cy.contains('About CodeSmile').click();
    cy.url().should('include', '/about');
  });
});
