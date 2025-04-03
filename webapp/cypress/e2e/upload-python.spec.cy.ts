import 'cypress-file-upload';
Cypress.config('defaultCommandTimeout', 50000);

describe('Upload Python Code Page (E2E)', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/upload-python');
    cy.clearLocalStorage();
    cy.clearCookies();
  });

  it('should upload a valid Python file and show its name', () => {
    const filePath = 'model_training_and_evaluation/model.py'; 
    cy.fixture(filePath, 'utf8').then((fileContent) => {
      cy.get('[role="file-uploader"]').attachFile({
        fileContent,
        fileName: "/model.py",
        mimeType: 'text/x-python',
      });
    });
    cy.get('#file-name').should('contain', 'model.py');  
  });

  it('should toggle between analysis modes (AI-Based and Static Tool)', () => {
    cy.contains('AI-Based').click();
    cy.contains('AI-Based').should('have.class', 'bg-red-500');  
    cy.contains('Static Tool').click();
    cy.contains('Static Tool').should('have.class', 'bg-blue-500'); 
  });

  it('should display progress and results in Static Tool mode', () => {
    const filePath = 'model_training_and_evaluation/dataset_preparation.py';
    cy.fixture(filePath, 'utf8').then((fileContent) => {
      cy.get('[role="file-uploader"]').attachFile({
        fileContent,
        fileName: "dataset_preparation.py",
        mimeType: 'text/x-python',
      });
    });

    cy.contains('Static Tool').click();  
    cy.get('button').contains('Upload Code (Static Mode)').click(); 

    cy.get('[data-testid="progress"]').should('exist');    

    cy.contains('Smell #1').should('be.visible');  
    cy.contains('Smell #2').should('be.visible');
  });

  it('should display progress and results in AI mode', () => {
    const filePath = 'model_training_and_evaluation/dataset_preparation.py';
    cy.fixture(filePath, 'utf8').then((fileContent) => {
      cy.get('[role="file-uploader"]').attachFile({
        fileContent,
        fileName: "dataset_preparation.py",
        mimeType: 'text/x-python',
      });
    });

    cy.contains('AI-Based').click();  
    cy.get('button').contains('Upload Code (AI Mode)').click(); 

    cy.get('[data-testid="progress"]').should('exist');    

    cy.contains('Smell #1').should('be.visible');  
  });

  it('should display no smells message for clean code', () => {
    cy.contains('Static Tool').click();
    const filePath = 'model_training_and_evaluation/pipeline.py';
    cy.fixture(filePath, 'utf8').then((fileContent) => {
      cy.get('[role="file-uploader"]').attachFile({
        fileContent,
        fileName: "pipeline.py",
        mimeType: 'text/x-python',
      });
    });
    cy.contains('Upload Code').click();
    cy.get("#progress-bar").should('be.visible')
    cy.contains('No code smells detected! Your code is clean!').should('be.visible');
  });

  it('should show an error when uploading an empty Python file', () => {
    cy.contains('Static Tool').click();

    const emptyFile = new File([], 'empty_file.py', { type: 'text/x-python' });

    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(emptyFile);

    cy.get('[role="file-uploader"]').attachFile({
      fileContent: emptyFile,  
      fileName: 'empty_file.py',
      mimeType: 'text/x-python',
    }, { allowEmpty: true });
    cy.contains('Upload Code').click();
    cy.contains('Code Snippet cannot be empty').should('be.visible');
  });

  it('should show an error when the API returns an error', () => {
    cy.contains('Static Tool').click();
    const filePath = 'model_training_and_evaluation/model.py';
    cy.fixture(filePath, 'utf8').then((fileContent) => {
      cy.get('[role="file-uploader"]').attachFile({
        fileContent,
        fileName: "model.py",
        mimeType: 'text/x-python',
      });
    });
    cy.intercept('POST', '/api/detect_smell_static', { statusCode: 500, body: { error: 'Internal Server Error' } }).as('apiFailure');
    cy.contains('Upload Code').click();
    cy.wait('@apiFailure');
    cy.contains('Error: Failed to analyze code.', { timeout: 10000 }).should('be.visible');
  });
});
