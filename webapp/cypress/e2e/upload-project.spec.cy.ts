import 'cypress-file-upload';
Cypress.config('defaultCommandTimeout', 10000);

describe('Upload Project Page', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/upload-project');
  });

  it('should load the upload-project page correctly', () => {
    cy.contains('Upload and Analyze Projects');
  });

  it('should allow the user to select an analysis mode', () => {
    cy.contains('AI-Based').click();
    cy.contains('Static Tool').click();
  });

  it('should allow the user to cancel the upload', () => {
    cy.contains('Static Tool').click();
    cy.contains('Add Project').click();
    const file1 = "model_training_and_evaluation/model.py"

    cy.fixture(file1, 'utf8').then((fileContent) => {
      cy.get('[data-testid="file-input"]').attachFile({
        fileContent,
        fileName: "model.py",
        mimeType: 'text/x-python',
      });
    });

    cy.get('#removeButton').click();
  });

  it('should allow the user to add a project and view analysis result', async () => {

    cy.contains('Static Tool').click();

    const file1 = 'model_training_and_evaluation/model.py';
    const file2 = 'model_training_and_evaluation/dataset_preparation.py';

    cy.contains('Add Project').click();

    await Promise.all([
        cy.fixture(file1, 'utf8').then((fileContent) => ({
        fileContent,
        fileName: "model.py",
        mimeType: 'text/x-python',
        })),
        cy.fixture(file2, 'utf8').then((fileContent) => ({
        fileContent,
        fileName: "dataset_preparation.py",
        mimeType: 'text/x-python',
        }))
    ]).then((files) => {
        cy.get('[data-testid="file-input"]').attachFile(files);
    });

    cy.contains('Upload and Analyze All Projects').click();
    cy.get('#message').should('contain', 'Projects successfully analyzed!');

    cy.contains('View Analysis Result').click();
  });

  it('should allow the user to add a project and view analysis result (ai)', async () => {

    cy.contains('AI-Based').click();

    const file1 = 'model_training_and_evaluation/model.py';
    const file2 = 'model_training_and_evaluation/dataset_preparation.py';

    cy.contains('Add Project').click();

    await Promise.all([
        cy.fixture(file1, 'utf8').then((fileContent) => ({
        fileContent,
        fileName: "model.py",
        mimeType: 'text/x-python',
        })),
        cy.fixture(file2, 'utf8').then((fileContent) => ({
        fileContent,
        fileName: "dataset_preparation.py",
        mimeType: 'text/x-python',
        }))
    ]).then((files) => {
        cy.get('[data-testid="file-input"]').attachFile(files);
    });

    cy.contains('Upload and Analyze All Projects').click();
    cy.get('#message').should('contain', 'Projects successfully analyzed!');

    cy.contains('View Analysis Result').click();
  });

  it('should handle API failure gracefully', () => {

    cy.contains('Static Tool').click();
    // Stub the API call to simulate a failure
    cy.intercept('POST', '/api/detect_smell_static', {
      statusCode: 500,
      body: { error: 'Internal Server Error' },
    }).as('apiFailure');;

    cy.contains('Add Project').click();

    const validFile = {
      fileName: 'valid.py',
      fileContent: new Blob(['print("hello world")'], { type: 'text/x-python' }),
      mimeType: 'text/x-python',
    };

    cy.get('[data-testid="file-input"]').attachFile(validFile);
    cy.contains('Upload and Analyze All Projects').click();
    cy.wait('@apiFailure');
    cy.contains('Analysis failed for snippet:', { timeout: 10000 }).should('be.visible');
  });
});
