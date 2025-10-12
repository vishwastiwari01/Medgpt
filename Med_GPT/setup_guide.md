# 🚀 MedGPT Setup Guide

Follow these steps to get your demo running in **5 minutes**.

## Step 1: Create Project Structure

Create a folder called `medgpt-demo` and set up this structure:

```
medgpt-demo/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── README.md
├── documents/
│   ├── diabetes_guidelines.txt
│   ├── hypertension_management.txt
│   └── antibiotic_protocols.txt
└── utils/
    ├── __init__.py
    ├── document_processor.py
    ├── vector_store.py
    └── llm_handler.py
```

## Step 2: Create Files

Copy each code file from the artifacts into the correct location:

1. **app.py** - Main application (in root folder)
2. **config.py** - Configuration (in root folder)
3. **requirements.txt** - Dependencies (in root folder)
4. **utils/document_processor.py** - Document processing
5. **utils/vector_store.py** - Vector search
6. **utils/llm_handler.py** - LLM handler
7. **documents/*.txt** - Three medical documents

**Important**: Create an empty `__init__.py` file in the `utils/` folder:

```bash
# In terminal/command prompt
touch utils/__init__.py
# Or on Windows: type nul > utils\__init__.py
```

## Step 3: Create the Three Medical Documents

Create these three text files in the `documents/` folder:

### documents/diabetes_guidelines.txt
```
TYPE 2 DIABETES MELLITUS - CLINICAL MANAGEMENT GUIDELINES

First-Line Treatment:
Metformin is the preferred first-line pharmacological agent for type 2 diabetes mellitus. The initial dose is typically 500mg once or twice daily with meals, gradually titrated to 1000mg twice daily based on tolerability and glycemic response. Metformin improves insulin sensitivity and reduces hepatic glucose production. Common side effects include gastrointestinal symptoms such as nausea, diarrhea, and abdominal discomfort, which can be minimized by starting with low doses and taking with food.

Diagnostic Criteria:
Diabetes is diagnosed when fasting plasma glucose is ≥126 mg/dL on two separate occasions, or HbA1c ≥6.5%, or random plasma glucose ≥200 mg/dL with symptoms of hyperglycemia. Prediabetes is defined as fasting glucose 100-125 mg/dL or HbA1c 5.7-6.4%.

Glycemic Targets:
The general HbA1c target for most adults with type 2 diabetes is <7%. More stringent targets (HbA1c <6.5%) may be appropriate for younger patients with short disease duration and no cardiovascular disease. Less stringent targets (HbA1c <8%) may be considered for patients with limited life expectancy, advanced complications, or extensive comorbidities.

Second-Line Agents:
When metformin monotherapy is insufficient, second-line options include GLP-1 receptor agonists such as semaglutide and dulaglutide which are particularly beneficial for patients with established cardiovascular disease or those needing weight loss. SGLT2 inhibitors like empagliflozin and dapagliflozin reduce cardiovascular events and progression of kidney disease. DPP-4 inhibitors such as sitagliptin offer neutral effects on weight. Sulfonylureas like glipizide and glyburide are effective but carry risk of hypoglycemia and weight gain.

Insulin Therapy:
Basal insulin is indicated when combination therapy fails to achieve glycemic targets. NPH insulin or long-acting analogs such as glargine or detemir are typically started at 10 units daily or 0.1-0.2 units per kg body weight, titrated based on fasting glucose levels.

Lifestyle Modifications:
Medical nutrition therapy and physical activity remain cornerstones of diabetes management. Patients should aim for 150 minutes of moderate-intensity aerobic activity per week. Weight loss of 5-10% can significantly improve glycemic control in overweight individuals.
```

### documents/hypertension_management.txt
```
HYPERTENSION MANAGEMENT PROTOCOL

Blood Pressure Classification:
Normal blood pressure is defined as systolic <120 mmHg and diastolic <80 mmHg. Elevated blood pressure is systolic 120-129 and diastolic <80. Stage 1 hypertension is systolic 130-139 or diastolic 80-89 mmHg. Stage 2 hypertension is systolic ≥140 or diastolic ≥90 mmHg. Hypertensive crisis is systolic >180 or diastolic >120 requiring immediate medical attention.

First-Line Antihypertensive Agents:
For most patients with stage 1 or 2 hypertension, first-line therapy includes thiazide diuretics such as chlorthalidone 12.5-25mg daily or hydrochlorothiazide 25-50mg daily. ACE inhibitors like lisinopril 10-40mg daily or enalapril 5-20mg twice daily are preferred for patients with diabetes or chronic kidney disease. Calcium channel blockers such as amlodipine 5-10mg daily are effective alternatives, especially for elderly patients or those of African descent. ARBs like losartan 50-100mg daily are suitable alternatives to ACE inhibitors when cough occurs.

Combination Therapy:
If monotherapy fails to achieve blood pressure targets after 4-6 weeks, combination therapy is recommended. Effective combinations include ACE inhibitor plus calcium channel blocker, ACE inhibitor plus thiazide diuretic, or ARB plus calcium channel blocker. Triple therapy adds a third agent from a different class.

Blood Pressure Targets:
For most adults with hypertension, the treatment goal is <130/80 mmHg. For adults aged 65 years or older, a target of <130/80 is reasonable if tolerated. For patients with diabetes or chronic kidney disease, the target remains <130/80 mmHg.

Resistant Hypertension:
Resistant hypertension is defined as blood pressure above goal despite adherence to three antihypertensive agents of different classes at optimal doses, including a diuretic. Spironolactone 25-50mg daily is the preferred fourth-line agent for resistant hypertension.

Hypertensive Emergency Management:
Hypertensive emergencies require immediate blood pressure reduction using intravenous agents such as labetalol, nicardipine, or nitroprusside in intensive care settings. Blood pressure should be reduced by no more than 25% in the first hour to avoid organ hypoperfusion.
```

### documents/antibiotic_protocols.txt
```
ANTIBIOTIC PRESCRIBING GUIDELINES

Community-Acquired Pneumonia:
For outpatient management of previously healthy adults with community-acquired pneumonia, amoxicillin 1g three times daily or doxycycline 100mg twice daily for 5-7 days is recommended. For patients with comorbidities such as diabetes, heart disease, or COPD, combination therapy with amoxicillin-clavulanate 875/125mg twice daily plus azithromycin 500mg on day 1 then 250mg daily for days 2-5 is preferred.

Uncomplicated Urinary Tract Infection:
For acute uncomplicated cystitis in women, nitrofurantoin 100mg twice daily for 5 days or trimethoprim-sulfamethoxazole 160/800mg twice daily for 3 days are first-line options. Fosfomycin 3g as a single dose is an alternative. Fluoroquinolones should be reserved for complicated infections due to side effect profile and resistance concerns.

Acute Bacterial Sinusitis:
Most cases of acute sinusitis are viral and do not require antibiotics. Bacterial sinusitis is suspected when symptoms persist beyond 10 days or worsen after initial improvement. First-line treatment is amoxicillin-clavulanate 875/125mg twice daily for 5-7 days. For penicillin-allergic patients, doxycycline 100mg twice daily or levofloxacin 500mg daily are alternatives.

Streptococcal Pharyngitis:
Group A streptococcal pharyngitis is treated with penicillin V 500mg twice daily or amoxicillin 500mg twice daily for 10 days. For penicillin-allergic patients, azithromycin 500mg on day 1 followed by 250mg daily for days 2-5, or cephalexin 500mg twice daily for 10 days in patients without severe penicillin allergy.

Skin and Soft Tissue Infections:
For simple cellulitis without purulence, cephalexin 500mg four times daily or dicloxacillin 500mg four times daily for 5-10 days is appropriate. If MRSA is suspected based on local prevalence or purulent drainage, trimethoprim-sulfamethoxazole 160/800mg twice daily plus cephalexin, or doxycycline 100mg twice daily, or clindamycin 300-450mg three times daily should be used.

Antibiotic Stewardship Principles:
Antibiotics should only be prescribed when bacterial infection is confirmed or highly suspected. The narrowest spectrum agent effective against the likely pathogen should be selected. Treatment duration should be the shortest effective period. Obtain cultures before initiating therapy when feasible, especially for serious infections.

Penicillin Allergy Assessment:
Most patients reporting penicillin allergy can safely receive penicillins or cephalosporins. True IgE-mediated reactions such as anaphylaxis, angioedema, or urticaria occurring within one hour of exposure represent true allergy. Delayed rashes or family history of allergy do not preclude use. Consider allergy testing or graded challenge when appropriate.
```

## Step 4: Install Python Dependencies

```bash
# Make sure you're in the medgpt-demo folder
cd medgpt-demo

# Install all required packages
pip install -r requirements.txt
```

This will install:
- streamlit
- sentence-transformers
- faiss-cpu
- PyPDF2
- anthropic (optional, for AI responses)
- python-dotenv

**Note**: First run will download the embedding model (~23MB). This is normal!

## Step 5: Run the Application

```bash
streamlit run app.py
```

Your browser will automatically open to `http://localhost:8501`

## Step 6: Test the Demo

1. Check "Use Sample Medical Documents" in the sidebar
2. Click "Initialize Sample Documents" button
3. Wait for processing (5-10 seconds)
4. Ask a question like: "What is the first-line treatment for type 2 diabetes?"
5. Review the answer with citations!

## 🎯 Demo Questions That Work Well

Try these to impress judges:

1. **"What is the first-line medication for type 2 diabetes?"**
   - Shows: Citation to diabetes_guidelines.txt

2. **"What are the blood pressure targets for treating hypertension?"**
   - Shows: Specific numerical targets with source

3. **"Which antibiotic should I prescribe for strep throat?"**
   - Shows: Multiple options with patient considerations

4. **"What are the diagnostic criteria for diabetes?"**
   - Shows: Specific lab values with citations

5. **"How do you treat resistant hypertension?"**
   - Shows: Multi-step protocol

6. **"What is the first-line treatment for breast cancer?"**
   - Shows: Handles missing information gracefully (not in knowledge base)

## 🔧 Troubleshooting

### Issue: ModuleNotFoundError
```bash
pip install -r requirements.txt --upgrade
```

### Issue: utils module not found
Create `__init__.py` in utils folder:
```bash
touch utils/__init__.py
```

### Issue: No documents folder
Make sure you created the documents/ folder with the three .txt files

### Issue: Slow first run
The embedding model downloads on first run (~23MB). This is normal!

## 🎨 Optional: Add Claude API

For full AI-powered responses:

1. Get API key from https://console.anthropic.com/
2. Create `.env` file in project root
3. Add: `ANTHROPIC_API_KEY=sk-ant-...your-key...`
4. Restart the app

Without API key, you still get working responses using the fallback mode!

## ✅ You're Ready!

Your MedGPT demo is now running. Show judges:
1. Document upload system
2. Semantic search in action
3. Cited, verifiable answers
4. Graceful handling of unknown queries
5. Professional UI

## 🚀 Next Steps for Buildathon

- Add more medical documents
- Create a slide deck explaining the vision
- Prepare 2-3 demo queries
- Explain how this reduces misdiagnosis
- Discuss scaling to full medical library

Good luck! 🎉