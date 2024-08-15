# this program do post processing_ latexml

import re
import shutil
import os
from markdownify import markdownify as md


def read_files_in_directory(txt_file, directory):
    search_string = "&"
    matched_files = []

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                if content.count(search_string) > 10:
                    matched_files.append(os.path.splitext(filename)[0])

    with open(txt_file, "w", encoding="utf-8") as output_file:
        for file_prefix in matched_files:
            output_file.write(file_prefix + "\n")


def copy_matched_files(txt_file_path, source_directory, destination_directory):
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    with open(txt_file_path, "r", encoding="utf-8") as file:
        prefixes = [line.strip() for line in file.readlines()]

    for filename in os.listdir(source_directory):
        file_prefix = os.path.splitext(filename)[0]

        if file_prefix in prefixes:
            source_file_path = os.path.join(source_directory, filename)
            destination_file_path = os.path.join(destination_directory, filename)
            shutil.copy2(source_file_path, destination_file_path)
            print(f"Copied: {source_file_path} to {destination_file_path}")


def convert_files_to_html(source_directory):
    output_directory = os.path.join(source_directory, "html_new")

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(source_directory):
        file_path = os.path.join(source_directory, filename)

        if os.path.isfile(file_path):
            file_prefix = os.path.splitext(filename)[0]
            output_file = os.path.join(output_directory, file_prefix + ".html")
            os.system(f"latexmlc {file_path} --output {output_file}")
            print(f"Converted: {file_path} to {output_file}")

def markdown_html2md(html_dir):
    output_directory = os.path.join(html_dir, "md_new")
    count = 1
    success = 1
    for file_name in os.listdir(html_dir):
        if file_name.endswith('.html'):
            input_file_path = os.path.join(html_dir, file_name)
            output_file_name = file_name.replace('.html', '.md')
            output_file_path = os.path.join(output_directory, output_file_name)
            with open(input_file_path, 'r', encoding='utf-8') as file:
                try:
                    html_content = file.read()
                    md_table = md(html_content)
                    with open(output_file_path, 'w', encoding='utf-8') as output_file:
                        output_file.write(md_table)
                        success += 1
                except Exception as e:
                    execption_file = os.path.join("exception_file.txt")
                    with open(execption_file,
                              'a') as file:
                        file.write(f'{file_name}   raise an error, {e} ''\n')

            count = count + 1

    print(count)
    print(success)

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    new_lines = []
    for i, line in enumerate(lines):
        if i < 7 and line.startswith('1'):
            continue  # Skip lines starting with '1' in the first seven lines
        if line.startswith('</br>'):
            continue
        if 'Generated on' in line:
            break  # Stop processing if 'Generated on' is found
        if 'Untitled Document' in line:
            line = line.replace('Untitled Document', '')
        if re.search(r'\{.*?\}', line):
            continue

        new_lines.append(line)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)


def process_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            process_file(file_path)


def delete_small_files(folder_path, min_chars=40):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    # Check the number of characters in the file
                    if len(content) < min_chars:
                        os.remove(file_path)
                        print(f"Deleted due to small size: {file_path}")
                        continue

                    if '|' not in content:
                        os.remove(file_path)
                        print(f"Deleted due to poor format: {file_path}")
                        continue

            except Exception as e:
                print(f"Could not process file {file_path}: {e}")




directory_to_check = "/Data/share/jia.he/LatexTable/SemiTable/md_nocap"
source_dir_path = "/Data/share/jia.he/LatexTable/file_all/Cap/latex"
destination_directory = "/Data/share/jia.he/LatexTable/file_all/Cap/tex_new_8_12" # latex folder
txt_file = "/Data/share/jia.he/LatexTable/file_all/Cap/match_file.txt"
html_output_directory = os.path.join(destination_directory, "html_new") # html folder
# folder_path = os.path.join(html_output_directory, "md_new") # md folder
folder_path = "/Data/share/jia.he/LatexTable/file_all/Cap/tex_new_8_12/html_new/md_new"

final_md_path = "/Data/share/jia.he/LatexTable/SemiTable/md_cap"



# read_files_in_directory(txt_file, directory_to_check)
# copy_matched_files(txt_file, source_dir_path, destination_directory)
# convert_files_to_html(destination_directory)
# markdown_html2md(html_output_directory)
# process_folder(folder_path)
delete_small_files(final_md_path)

