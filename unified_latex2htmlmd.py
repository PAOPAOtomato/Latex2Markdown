import json
import re
import htmltabletomd
import os
from bs4 import BeautifulSoup
from markdownify import markdownify as md

global_flag = 'NoCap'
global_flag_latex_str = 'Not-str'


def filter_table_from_json_file(json_file_path,
                                output_tex_folder):  # extract each table data from json file and write to a .tex file. Even though html elements may include
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    output_dic = output_tex_folder
    os.makedirs(output_dic, exist_ok=True)
    file_index = 0
    for entry in data:
        arxiv_id = entry['arxiv_id']
        arxiv_id = arxiv_id.replace("/", "")
        # find = "/"
        # if find in entry['arxiv_id']:  # deal with the exception which '\' is consist in arxiv_id
        #     arxiv_id = entry['arxiv_id'].split('/')[0] + '' + entry['arxiv_id'].split('/')[1]
        # else:
        #     arxiv_id = entry['arxiv_id']

        num_table = 1
        for i, table in enumerate(entry['tables']):
            #file_name = f'{arxiv_id}_{num_table}.tex'
            file_name = arxiv_id + "_{}.tex".format(str(i).zfill(3))
            file_path = os.path.join(output_dic, file_name)
            with open(file_path, 'w') as tex_file:
                tex_file.write('\\documentclass{article}\n')
                tex_file.write('\\usepackage{booktabs}\n')
                tex_file.write('\\begin{document}\n')
                if global_flag == 'NoCap':
                    tex_file.write(table['table'] + '\n')
                else:  # in case of Cap
                    tex_file.write(table['table_cap'] + '\n')
                tex_file.write('\\end{document}\n')
            file_index += 1
            num_table += 1

    print(f'Finish loading data, the latex files are saved at: {output_tex_folder}')




def latex_to_html(file_dir):
    count = 0
    for root, dirs, files in os.walk(file_dir):  # 获取当前文件夹的信息
        for file in files:  # 扫描所有文件
            if os.path.splitext(file)[1] == ".tex":  # 提取出所有后缀名为.html的文件
                os.chdir(root)  # os.chdir() 方法用于改变当前工作目录到指定的路径。
                file_name = os.path.basename(file)
                count = count + 1
                # 使用os.system调用pandoc进行格式转化
                os.system("pandoc -f latex --mathjax -t html " + file + " -o " + os.path.splitext(file)[0] + ".html")
                print(f'Latex to Html in total:{count}')


def html_to_markdown(output_html_file, output_md_file):
    with open(output_html_file, 'r', encoding='utf-8') as file:
        try:
            html_content = file.read()
            content = html_content
            md_table = htmltabletomd.convert_table(content, all_cols_alignment="center")
            if global_flag == 'NoCap':
                with open(output_md_file, 'w', encoding='utf-8') as output_file:
                    output_file.write(md_table)
            else:
                soup = BeautifulSoup(html_content, 'lxml')  # get the caption from html
                captions = soup.find_all('caption')
                with open(output_md_file, 'w', encoding='utf-8') as output_file:
                    if captions:
                        string_caption = str(captions[0])  # caption is list type, convert to string
                        output_file.write(md(string_caption))
                        output_file.write('\n')
                    output_file.write(md_table)

        except Exception as e:
            file_name = os.path.basename(output_html_file)
            with open("/Data/share/jia.he/LatexTable/eception.txt", 'a') as file:
                file.write(f'{file_name}   raise an error, {e} ''\n')  # only converting the table

def html2md_markdonify(input, output):
    file_name = os.path.basename(input)
    with open(input, 'r', encoding='utf-8') as file:
        try:
            html_content = file.read()
            md_table = md(html_content)
            if len(html_content) < 50: # filter out empty file, some may only contain \n\n\n
                with open("/Data/share/jia.he/LatexTable/eception_markdownify.txt",
                              'a') as file:
                    file.write(f'{file_name}   is empty.')  # only converting the table
            else:
                with open(output, 'w', encoding='utf-8') as output_file:
                    output_file.write(md_table)
                    # print(md_table)
                    # print("success")

        except Exception as e:

            with open("/Data/share/jia.he/LatexTable/eception_markdownify.txt",
                          'a') as file:
                file.write(f'{file_name}   raise an error, {e} ''\n')  # only converting the table


def html_str_to_markdown(html_str):
    md_str = htmltabletomd.convert_table(html_str, all_cols_alignment="center")
    return md_str


def rename_file(folder_path):  # this function zfill the file name
    files = os.listdir(folder_path)
    for filename in files:
        match = re.search(r'_(\d+)(\.\w+)$', filename)
        number_part = match.group(1)
        ext = match.group(2)
        new_number_part = f"{int(number_part) - 1:03d}"

        new_filename = filename[:match.start(1) - 1] + f"_{new_number_part}{ext}"
        old_file = os.path.join(folder_path, filename)
        new_file = os.path.join(folder_path, new_filename)
        os.rename(old_file, new_file)
        print(f"RENAME:{old_file} to {new_file}")


def delete_unwanted_fields(folder_path):
    brackets_pattern = re.compile(r'\\\\\((.*?)\\\\\)', re.DOTALL)
    brackets_pattern_2 = re.compile(r'\\\\', re.DOTALL)
    brackets_pattern_3 = re.compile(r'\\', re.DOTALL)

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                content = brackets_pattern.sub(r'$\1$', content)
                content = brackets_pattern_2.sub(r'PLACE_HOLDER_DOUBLE_BACKSLASH', content)
                content = brackets_pattern_3.sub('', content)
                content = content.replace('PLACE_HOLDER_DOUBLE_BACKSLASH', '\\')

                print("yes")

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)


def delete_unwanted_fields_html_str(md_str):
    patterns_replacements = [
        (r'</?ul>', ''),
        (r'<li><p>', '*'),
        (r'</p></li><br>', '</br>'),
        (r'<br>', ''),
        (r'\\\((.*?)\\\)', r'$\1$'),
        (r'\\\$(\\)', r'$'),
        (r'\\\$', r'$'),
        (r'\$\ ', r'$'),
        (r'<span class="math inline">\\\((.*?)\\\)</span>', r'$\1$'),
        (r'\\\\\((.*?)\\\\\)', r'$\1$'),
        (r'\\\=', '='),
        (r'\\einheit\{(.*?)\}', r'\1'),
        (r'\\\)', ''),
        (r'\<span class="citation" data-cites="(.*?)"></span>', r'$??$'),
        (r'\$\x5c\\', r'$\\'),
        (r'&#124;', r'\|'),
        (r'\\Delta', r'\\ Delta'),
        (r'<span>', ''),
        (r'<span class="math inline">', ''),
        (r'</span>', ''),
        (r'\\\\cdot', r'\\cdot'),
        (r'\\_', '_'),
        (r'\\\\mathrm', ''),
        (r'\\mbox', ''),
        (r'<strong>', ''),
        (r'</strong>', ''),
        (r'\\rm', ''),
        (r'&lt;', '<'),
        (r'\{\\text\{(.*?)\}\}', r'{\1}'),
        (r':---:', '---')
    ]

    content = md_str
    for pattern, replacement in patterns_replacements:
        content = re.sub(pattern, replacement, content)

    return content


def write_to_json(json_file, md_folder):
    if global_flag == 'NoCap':
        md_with_caption_folder = ""


    # counter_caption = 0
    counter = 0
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for entry in data:
        arxiv_id = entry['arxiv_id']
        arxiv_id = arxiv_id.replace('/', '')
        tables = entry['tables']

        for index, table in enumerate(tables):
            md_filename = f"{arxiv_id}_{str(index).zfill(3)}.md"
            md_filepath = os.path.join(md_folder, md_filename)
            try:
                with open(md_filepath, 'r', encoding='utf-8') as md_file:
                    md_content = md_file.read()
                    if global_flag == 'NoCap':
                        table['md_no_caption'] = md_content
                        counter += 1
                    else:
                        table['md_with_caption'] = md_content
                        counter += 1

            except Exception as e:
                file_name = os.path.basename(md_filepath)
                with open("/Data/share/jia.he/LatexTable/failed_write_in_json.txt", 'a') as file:
                    file.write(f'{file_name}   raise an error, {e} ''\n')  # only converting the table

    print(counter)
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)




# Combined process function
def process_json_file(json_file_path, output_latex_folder, output_html_folder, output_md_folder):
    # filter_table_from_json_file(json_file_path, output_latex_folder)  # using what
    # latex_to_html(output_latex_folder)
    #
    # os.system("cd " + output_latex_folder)
    # os.system("mv *html " + output_html_folder)

    os.makedirs(output_md_folder, exist_ok=True)
    count = 1
    for file_name in os.listdir(output_html_folder):
        if file_name.endswith('.html'):
            print("HTML TO Md: number:" + str(count))
            count = count + 1
            input_file_path = os.path.join(output_html_folder, file_name)
            output_file_name = file_name.replace('.html', '.md')
            output_file_path = os.path.join(output_md_folder, output_file_name)
            html2md_markdonify(input_file_path, output_file_path)

    print("Html to Md, done")
    print(count)
    # rename_file(output_md_folder)
    # print("Rename all set")

    delete_unwanted_fields(output_md_folder)
    print("Filter Done")

    # Write to JSON file
    # write_to_json(json_file_path, output_md_folder)
    # print(
    #     "Finish Writing-----------------------------------------------------------------------------------------------------------------------------")


def process_latex_str(html_str):
    md_str = html_str_to_markdown(html_str)
    print("HTML2MD, done")
    md_str = delete_unwanted_fields_html_str(md_str)
    print("Filter Done")
    return md_str


# Main function to execute the script
def main():
    html_str = ""
    json_file = "/Data/share/jia.he/LatexTable/files/000000_000020_bk copycp.json"
    if global_flag_latex_str == 'str':
        process_latex_str(html_str)

    else:
        if global_flag == 'NoCap':
            output_latex_no_cap_folder = "/Data/share/jia.he/LatexTable/file_all/nocap/latex_nocap"
            output_html_no_cap_folder = "/Data/share/jia.he/LatexTable/file_all/nocap/html_nocap"
            output_md_no_cap_folder = "/Data/share/jia.he/LatexTable/file_all/nocap/md_nocap"
            process_json_file(json_file, output_latex_no_cap_folder, output_html_no_cap_folder, output_md_no_cap_folder)
        else:
            output_latex_cap_folder = "/Data/share/jia.he/LatexTable/file_all/Cap/latex"
            output_html_cap_folder = "/Data/share/jia.he/LatexTable/file_all/Cap/html"
            output_md_cap_folder = "/Data/share/jia.he/LatexTable/file_all/Cap/md"
            process_json_file(json_file, output_latex_cap_folder, output_html_cap_folder, output_md_cap_folder)


if __name__ == "__main__":
    main()
