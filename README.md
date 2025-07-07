

## 🚀 Hackathon Project: Smart Startup Name Chooser

### 📍 In collaboration with RNE Tunisia & Hill

This project is the code behind a demo built for **RNE Tunisia**, in collaboration with Hill . The goal is to help entrepreneurs choose valid startup names that comply with RNE's naming rules using an intelligent and guided step-by-step process.

We built a **modular pipeline** that takes the user from idea to name validation using simple logic, rule-checking, and semantic filtering. Our aim was to keep the process transparent so that users can understand the decision-making logic at every step.

---

## 🛠️ Project Structure

### 1. `hill-rules.ipynb`

**Goal**: Encode RNE's name validation rules as functions.

**Contents**:

* Hard-coded rules derived from RNE guidelines.
* Examples of invalid names (e.g., reserved keywords, government-related words, etc.).
* Functions to check rule violations for a given name.
* Output: Binary pass/fail or rule-specific violations.

---

### 2. `hiillll.ipynb`

**Goal**: Build a user-facing pipeline that guides a user through name selection and validation.

**Contents**:

* Interactive name input.
* Use of the validation rules from `hill-rules.ipynb`.
* User feedback at each stage (e.g., "Name contains restricted word").
* Suggestions for modification or improvements to the name.
* Serves as a minimal working prototype for UI/backend integration.

---

### 3. `semantic-search.ipynb`

**Goal**: Filter or flag names using **semantic similarity** (e.g., for originality or category match).

**Contents**:

* Embedding-based name analysis using a pre-trained sentence transformer or similar model.
* Semantic similarity search against a database of existing company names or restricted terms.
* Helps detect names that are too similar to existing businesses, which could be legally problematic or confusing.

---

## ⚙️ Tech Stack

* Python 3
* Jupyter Notebooks
* Sentence Transformers / Semantic Search
* Simple rule-based logic and string processing


