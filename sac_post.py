import csv
import os
import re
import html2text

# Set the base directory of the project
base_directory = os.path.dirname(os.path.abspath(__file__))

# Set the relative paths for the CSV file and output directory
csv_file = os.path.join(base_directory, "data", "sac.csv")
output_directory = os.path.join(base_directory, "content", "sac")

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Delete all existing markdown files in the output directory
for file_name in os.listdir(output_directory):
    if file_name.endswith(".md"):
        file_path = os.path.join(output_directory, file_name)
        os.remove(file_path)

# Open the CSV file and iterate over each row
with open(csv_file, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Extract the relevant information from the row
        name = row["name"]
        date = row["date"]
        price = row["price"]
        additional_info_html = row["additional_info"]
        link = row["link"]
        thumbnail = row["thumbnail"]

        # Remove invalid characters from the name
        name = re.sub(r'[<>:"/\\|?*]', '', name)

        # Convert HTML to Markdown
        additional_info_markdown = html2text.html2text(additional_info_html)

        # Replace newline characters with <br> tags or double spaces for markdown
        additional_info_markdown = additional_info_markdown.replace('\n', '  \n')

        # Generate the markdown file name
        file_name = f"{date}-{name}.md"
        file_path = os.path.join(output_directory, file_name)

        # Generate the markdown content
        markdown_content = f"""---
title: "({date}) {name}"
---

# 제목
{name}

# 일시
{date}

# 가격
{price}

# 공연정보
{additional_info_markdown}

# 링크
[자세히 보기]({link} "{link}")
"""

        # Write the markdown content to the file
        with open(file_path, "w", encoding="utf-8") as markdown_file:
            markdown_file.write(markdown_content)

print("Markdown files generated successfully!")