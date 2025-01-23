# Resume Analyzer 
## App by [Arif.my](https://arif.my)

A web-based **Resume Analysis Tool** that evaluates resumes against job descriptions to calculate key metrics such as **Job Matching Score** and **ATS Compatibility Score**. The tool provides actionable feedback to help job seekers optimize their resumes for better job opportunities.

---

## Features

- **Resume Upload**: Upload resumes in various formats (PDF, DOCX, etc.).
- **Job Description Matching**: Paste a job description or provide a job link for skill matching.
- **Key Metrics**:
  - **Job Matching Score**: Measures how well the resume matches the job description.
  - **ATS Compatibility Score**: Evaluates adherence to ATS standards (keywords, formatting, structure).
- **Interactive Visualizations**:
  - Displays scores using horizontal bar charts for a compact and clean look.
- **Detailed Feedback**:
  - Highlights key skills that align with the job.
  - Lists missing skills and provides suggestions for improvement.
- **Smooth User Experience**:
  - Responsive design for mobile and desktop.
  - Includes a wave loading animation during transitions.
- **Secure Handling of API Keys**:
  - Uses environment variables to protect sensitive API keys.

---

## Getting Started

Follow these steps to set up and run the **Resume Analyzer** locally:

### Prerequisites

1. **Install Python**:
   - Ensure Python 3.8 or above is installed on your system.
   - Download it from [python.org](https://www.python.org/downloads/).

2. **Install Pip**:
   - Pip is Python's package manager and comes pre-installed with Python.
   - Verify pip is installed by running:
     ```bash
     pip --version
     ```

3. **Install Git**:
   - Git is required to clone the repository.
   - Download it from [git-scm.com](https://git-scm.com/).

4. **Get an OpenAI API Key**:
   - Sign up at [OpenAI](https://platform.openai.com/signup/) and create an API key.
   - Copy the API key for later use.

5. **Set up Environment Variables**:
   - You’ll need to store your API key securely in an `.env` file.

---

### Installation Steps

1. **Clone the Repository**:
   - Open your terminal and run:
     ```bash
     git clone https://github.com/mmarifmz/resume_analyzer.git
     cd resume_analyzer
     ```

2. **Create a Virtual Environment**:
   - Create a virtual environment to manage dependencies:
     ```bash
     python -m venv venv
     ```
   - Activate the virtual environment:
     - **Windows**:
       ```bash
       venv\Scripts\activate
       ```
     - **macOS/Linux**:
       ```bash
       source venv/bin/activate
       ```

3. **Install Dependencies**:
   - Install the required Python packages:
     ```bash
     pip install -r requirements.txt
     ```

4. **Set up the `.env` File**:
   - Create a new `.env` file in the root of the project:
     ```bash
     touch .env
     ```
   - Add your OpenAI API key to the file:
     ```env
     OPENAI_API_KEY=your-api-key
     ```

5. **Run the Application**:
   - Start the Flask development server:
     ```bash
     python app.py
     ```
   - Open your browser and go to:
     ```text
     http://127.0.0.1:5000
     ```

---

## How to Use

1. **Upload Resume**:
   - Select a resume file in PDF, DOCX, or text format.
2. **Enter Job Description**:
   - Paste the job description or provide a job link.
3. **Analyze Results**:
   - View the Job Matching and ATS Scores.
   - Get actionable feedback on improving your resume.

---

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Bootstrap 5, Chart.js
- **Data Handling**: OpenAI API for text analysis
- **Visualization**: Chart.js for dynamic charts
- **Security**: Environment variables for API key management

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).