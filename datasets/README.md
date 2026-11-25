# Datasets

`questions.csv` is exported from the curated question bank during setup and contains the 64 Computer Networks MCQs used by the application. The source of truth is `src/data/question_bank.py`.

`synthetic_training_data.csv` is generated reproducibly with `python -m src.data.data_generator`. Each row represents a simulated question attempt. Student skill, topic strength, question difficulty, practice, forgetting, and noise affect outcomes. The model's features are built from earlier attempts only; no current answer is included as a predictor. Synthetic data is for demonstrating the pipeline, not validating educational outcomes. Replace it only with appropriately consented and governed data, preserving student-group evaluation and privacy safeguards.
