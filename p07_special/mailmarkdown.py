"""
test to transform a markdown to html
"""
from common.MailingSystem import add_paragraph_with_lines, generate_htmlfile, clean_mail, add_paragraph_with_items, add_paragraph_with_array
from  common.maintenance import system_exec


def main(dry_run: bool = False):
    ret, lines = system_exec("ipconfig", "moi")
    clean_mail()

    add_paragraph_with_lines("titre1", 2, ["pre message"], lines, ["postmessage"])

    add_paragraph_with_items("titre2", 2, ["pre message"], ["coco","caca","pipi"], ["postmessage"])

    add_paragraph_with_array("titre3", 2, ["col1", "col2", "col3"], [["a", "b", "c"],["1", "2", "3"],["9", "5", "1"]], ["pre message"], ["postmessage"])

    generate_htmlfile()
