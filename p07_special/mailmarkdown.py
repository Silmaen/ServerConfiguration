"""
test to transform a markdown to html
"""
from common.MailingSystem import add_paragraph_with_lines, generate_htmlfile, clean_mail, add_paragraph_with_items, add_paragraph_with_array
from  common.maintenance import system_exec


def main(dry_run: bool = False):
    print("generate_htmlfile")
    generate_htmlfile()
