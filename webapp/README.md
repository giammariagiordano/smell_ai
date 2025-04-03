# **CodeSmile WebApp**

CodeSmile WebApp is a web-based application that performs AI-driven and static analysis of code smells, along with report generation. This README provides instructions for setting up and running the project.

## **Features**
- **AI Analysis Service**: Analyze code smells using AI algorithms.
- **Static Analysis Service**: Perform rule-based code smell detection.
- **Report Service**: Generate and download detailed reports of analyzed code.
- **Gateway**: API Gateway that orchestrates requests across services.
- **Frontend WebApp**: User-friendly interface to interact with all services.

## **Getting Started**

### **Prerequisites**
- [Docker](https://www.docker.com/) (v20+ recommended)
- [Docker Compose](https://docs.docker.com/compose/) (v2.12+ recommended)

## **Setup and Usage**

1. **Clone the Repository**
```bash
git clone https://github.com/xDaryamo/smell_ai.git
cd smell_ai
``` 

2. **Build and Start the Web App**
```bash
docker-compose build
docker-compose up
``` 

3. **Access the WebApp**

Once the containers are running, navigate to the UI at `http://localhost:3000`.


## **Run app locally**

### **Services set up**
Install dependencies and run services directly: 

```bash
cd webapp/gateway
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
``` 

```bash
cd smell_ai
pip install -r requirements.txt
uvicorn webapp.services.aiservice.app.main:app --host 0.0.0.0 --port 8001
``` 

```bash
cd smell_ai
pip install -r requirements.txt
uvicorn webapp.services.staticanalysis.app.main:app --host 0.0.0.0 --port 8002
``` 

```bash
cd smell_ai
pip install -r requirements.txt
uvicorn webapp.services.report.app.main:app --host 0.0.0.0 --port 8003
``` 

### **UI set up**
```bash
cd webapp
npm install
npm run build
npm run start
```

### ⚠️ Important: Switching Between Docker and Local Execution
If you want to switch from Docker-based execution to local execution (or vice versa), ensure that the import statements in the service files match the chosen execution mode.
Check the paths and configurations in the Python services files to avoid import-related errors.

## **Ollama set up**

To successfully run the model using **Ollama**, follow these steps:

### 1. Install Ollama
First, ensure that **Ollama** is installed on your system. You can download and install it by following the official instructions available at: [https://ollama.ai](https://ollama.ai).

### 2. Create the Model
Once Ollama is installed, open the **Command Prompt** (Windows) or **Terminal** (macOS/Linux) and use the following command to create the model:

```bash
ollama create codesmile -f <Modelfile_location>
```

## **Testing**

### **UI Components Testing**
The UI components have been tested using Jest, a JavaScript testing framework. Jest ensures that all components render correctly and function as expected in isolation. To run tests, execute the following bash:

```bash
cd webapp
npm test
``` 

### **E2E Testing**
End-to-end tests have been implemented using Cypress, a robust framework for testing web applications. Cypress tests cover the user journey, ensuring that all workflows function correctly. To run tests, execute the following bash:

```bash
cd webapp
npx cypress open
``` 
Select E2E testing in your browser of choice and run the single test suites(specs).

## **Services Overview**

### **1. Gateway**
The API Gateway routes requests between the frontend and services.
- **Port**: `8000`
- **Endpoints**:
  - `/api/detect_smell_ai`: Proxy for AI analysis.
  - `/api/detect_smell_static`: Proxy for static analysis.
  - `/api/generate_report`: Proxy for generating reports.

### **2. AI Analysis Service**
Provides AI-driven code smell detection.
- **Port**: `8001`
- **Endpoint**: `/detect_smell_ai`

### **3. Static Analysis Service**
Performs static, rule-based analysis.
- **Port**: `8002`
- **Endpoint**: `/detect_smell_static`

### **4. Report Service**
Generates reports based on analysis results.
- **Port**: `8003`
- **Endpoint**: `/generate_report`

### **5. Frontend WebApp**
A React-based user interface for interacting with the services.
- **Port**: `3000`


## **Configuration**

### **Environment Variables**
You can configure services using environment variables in the `docker-compose.yml` or a `.env` file:
- AI_ANALYSIS_SERVICE=`http://ai_analysis_service:8001`
- STATIC_ANALYSIS_SERVICE=`http://static_analysis_service:8002`
- REPORT_SERVICE=`http://report_service:8003`
- NEXT_PUBLIC_API_BASE_URL=`http://localhost:8000/api`

## **Technologies Used**
Here are the core technologies and tools used to realize the web app:

**Services**
- **FastAPI**: Framework used for building the backend services with high performance and easy-to-use APIs.
- **Uvicorn**: ASGI server used to run FastAPI applications.
- **Docker**: Containerization tool to package and deploy services in isolated environments.
- **Docker Compose**: Tool to manage multi-container Docker applications, used to orchestrate the various backend services.
  
**UI**
- **React**: JavaScript library used for building the user interface of the web app.
- **Next.js**: React framework for server-side rendering and static site generation.
- **Node.js**: JavaScript runtime used for running Next.js and managing frontend dependencies.
- **npm**: Package manager for managing frontend dependencies.

## Acknowledgments

This project is a **contribution** to the work presented in the paper:  
**"When Code Smells Meet ML: On the Lifecycle of ML-Specific Code Smells in ML-Enabled Systems"**  
- Authors: *[Gilberto Recupito](https://github.com/gilbertrec), [Giammaria Giordano](https://github.com/giammariagiordano), [Filomena Ferrucci](https://docenti.unisa.it/001775/en/home), [Dario Di Nucci](https://github.com/dardin88), [Fabio Palomba](https://github.com/fpalomba)*  
- [Read the full paper here](https://arxiv.org/abs/2403.08311)

The improvements implemented in this project were carried out by **[Dario Mazza](https://github.com/xDaryamo)** and **[Nicolò Delogu](https://github.com/XJustUnluckyX)**. This work was completed as part of the *Software Engineering: Management and Evolution* course within the Master's Degree program in Computer Science.
