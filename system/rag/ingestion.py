#Purpose: Load and extract text
"""
File Name: ingestion.py
Goals:
-read and extract PDF files
-attach source metadata
-reject unsupported files
-return structured document objects
"""

calfresh_information = [] 

try: 
    with open('data/raw/Food_CalFresh.txt', 'r') as file:
        calfresh_information = file.readlines()
        print(f'Loaded{len(calfresh_information)} entries')
except OSError:
    print("Cannot load information")
