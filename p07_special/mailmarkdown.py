"""
test to transform a markdown to html
"""
from common.AllDefaultParameters import data_dir
import os


def get_style():
    fp = open(os.path.join(data_dir, "mail.css"))
    ret = "".join([line.strip() for line in fp.readlines()])
    fp.close()
    return ret


def to_html(text):
    """
    simple wrapper to the markdown lib
    :param text: input text
    :return:
    """
    from markdown import markdown
    from datetime import datetime
    fp = open(os.path.join(data_dir, "mailtemplate.html"))
    lines = fp.readlines()
    fp.close()
    ret_lines = []
    md_lines = markdown("".join(text), extensions=['tables']).splitlines()
    for line in lines:
        if "{% content %}" in line:
            indent = line.split("{% content %}")[0]
            for li in md_lines:
                ret_lines.append(indent + li + "\n")
            continue
        if "{% date %}" in line:
            line = line.replace("{% date %}", datetime.now().strftime("%Y %m %d"))
        if "{% style %}" in line:
            line = line.replace("{% style %}", get_style())
        ret_lines.append(line)
    return ret_lines


def main(dry_run: bool = False):
    fp = open(os.path.join(data_dir, "mail.md"))
    lines = fp.readlines()
    fp .close()
    html = to_html(lines)
    fo = open(os.path.join(data_dir, "mail.html"), "w")
    fo.writelines(html)
    fo.close()
