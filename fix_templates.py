import os
import re

def fix_template(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace == with " == " only inside {% ... %} tags
    pattern = r'({%.*?)(?<! )==(?!= )(.*?%})'
    new_content = re.sub(pattern, r'\1 == \2', content)
    
    if content != new_content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")
    else:
        print(f"No changes needed for {filepath}")

templates_to_fix = [
    'templates/exams/question_form.html',
    'templates/exams/take_exam.html'
]

for t in templates_to_fix:
    full_path = os.path.join('/home/samir/E/Eighth Semester/AI in education/Auto Grading', t)
    if os.path.exists(full_path):
        fix_template(full_path)
    else:
        print(f"File not found: {full_path}")
