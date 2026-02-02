
import os
import re

def check_template_integrity(root_dir):
    block_tags = ['if', 'for', 'block', 'with', 'while', 'autoescape', 'comment', 'filter', 'spaceless']
    # Regex to find tags. Note: This is a simplified regex and might miss complex edge cases or commented out tags.
    # It finds {% tagname ... %}
    tag_pattern = re.compile(r'{%\s*(\w+)(?:\s+[^%]*)?\s*%}')
    
    issues = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if not filename.endswith('.html'):
                continue
            
            filepath = os.path.join(dirpath, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            stack = []
            
            for i, line in enumerate(lines):
                # Identify tags in the line
                matches = tag_pattern.finditer(line)
                for match in matches:
                    tag_name = match.group(1)
                    
                    if tag_name in block_tags:
                        stack.append((tag_name, i + 1))
                    elif tag_name.startswith('end'):
                        base_tag = tag_name[3:] # remove 'end'
                        if base_tag in block_tags:
                            if not stack:
                                issues.append(f"{filepath}:{i+1} - Unexpected {{% {tag_name} %}} without start tag.")
                            else:
                                last_tag, last_line = stack[-1]
                                if last_tag == base_tag:
                                    stack.pop()
                                else:
                                    # Mismatch
                                    issues.append(f"{filepath}:{i+1} - Mismatched tag. Found {{% {tag_name} %}}, expected end for {{% {last_tag} %}} (from line {last_line}).")
                                    # Attempt to recover? No, just report.
            
            if stack:
                for tag, line in stack:
                    issues.append(f"{filepath}:{line} - Unclosed tag {{% {tag} %}}.")

    return issues

if __name__ == "__main__":
    templates_dir = "/home/samir/E/Eighth Semester/AI in education/Auto Grading/templates"
    found_issues = check_template_integrity(templates_dir)
    if found_issues:
        print("Found issues:")
        for issue in found_issues:
            print(issue)
    else:
        print("No block tag issues found.")
