"""
Global mailing system
"""
import os
import shutil
from common.AllDefaultParameters import data_dir, config_dir, resource_dir, template_dir
from common.maintenance import logger, system_exec


md_mail_file = os.path.join(data_dir, "mail.md")
html_mail_file = os.path.join(data_dir, "mail.html")
template_mail_file = os.path.join(template_dir, "mailtemplate.html")
css_mail_file = os.path.join(resource_dir, "mail.css")
mailing_list_file = os.path.join(config_dir, "MailingList")
mail_to_send = os.path.join(data_dir, "mail_to_send")


def clean_mail():
    """
    clean the mail markdown & html
    """
    if os.path.exists(md_mail_file):
        os.remove(md_mail_file)
    if os.path.exists(html_mail_file):
        os.remove(html_mail_file)
    if os.path.exists(mail_to_send):
        os.remove(mail_to_send)


def new_mail():
    """
    create a new mail with title and date as Markdown file
    """
    from datetime import datetime
    clean_mail()
    fd = open(md_mail_file, "w")
    fd.write("# Activity Report from argawaen.net server #\n")
    fd.write("## General ##\n")
    fd.write("> " + datetime.now().strftime("%Y %m %d %H:%M:%S") + "\n")
    fd.write("\n")
    fd.close()


def test_mail():
    """
    test for mail file existence and create it if needed
    :return:
    """
    if not os.path.exists(md_mail_file):
        new_mail()


def add_mail_line(line: str):
    """
    Add directly a raw line into the markdown file
    :param line: the line to add
    """
    test_mail()
    fd = open(md_mail_file, "a")
    fd.write(line.strip() + "\n")
    fd.close()


def add_paragraph(title: str, level: int = 2, message=None):
    """
    add a full paragraph in the md file
    :param title:
    :param level:
    :param message:
    :return:
    """
    if message is None:
        message = []
    test_mail()
    fd = open(md_mail_file, "a")
    quote = ["", ">"*(level-2)][level>2]
    fd.write(quote + " " + "#"*level + " " + title + " " + "#"*level + "\n")
    quote += ">"
    for line in message:
        fd.write(quote + " " + line + "\n")
    fd.write("\n")
    fd.close()


def add_paragraph_with_lines(title: str, level: int = 2, pre_message=None, lines=None, post_message=None):
    """
    add a full paragraph in the md file
    :param title:
    :param level:
    :param pre_message:
    :param lines:
    :param post_message:
    :return:
    """
    if post_message is None:
        post_message = []
    if pre_message is None:
        pre_message = []
    if lines is None:
        lines = []
    message = []
    for it in pre_message:
        message.append(it)
    if len(pre_message) > 0:
        message.append("")
    for line in lines:
        message.append("    " + line)
    if len(lines) > 0:
        message.append("")
    for it in post_message:
        message.append(it)
    if len(post_message) > 0:
        message.append("")
    add_paragraph(title, level, message)


def add_paragraph_with_items(title: str, level: int = 2, pre_message=None, lines=None, post_message=None):
    """
    add a full paragraph in the md file
    :param title:
    :param level:
    :param pre_message:
    :param lines:
    :param post_message:
    :return:
    """
    if post_message is None:
        post_message = []
    if pre_message is None:
        pre_message = []
    if lines is None:
        lines = []
    message = []
    for it in pre_message:
        message.append(it)
    if len(pre_message) > 0:
        message.append("")
    for line in lines:
        message.append("* " + line)
    if len(lines) > 0:
        message.append("")
    for it in post_message:
        message.append(it)
    if len(post_message) > 0:
        message.append("")
    add_paragraph(title, level, message)


def add_paragraph_with_array(title: str, level: int = 2, col_titles=None, rows=None, pre_message=None,
                             post_message=None):
    """

    :param title:
    :param level:
    :param col_titles:
    :param rows:
    :param pre_message:
    :param post_message:
    :return:
    """
    if post_message is None:
        post_message = []
    if pre_message is None:
        pre_message = []
    if rows is None:
        rows = []
    if col_titles is None:
        col_titles = []
    test_mail()
    fd = open(md_mail_file, "a")
    fd.write("> " + "#"*level + " " + title + " " + "#"*level + "\n")
    # pre message
    for line in pre_message:
        fd.write("> " + line + "\n")
    fd.write(">\n")
    # array
    fd.write("> |")
    for col_title in col_titles:
        fd.write(" " + col_title + " |")
    fd.write("\n")
    fd.write("> |")
    for col_title in col_titles:
        fd.write(" --- |")
    fd.write("\n")
    for r in rows:
        if len(r) != len(col_titles):
            logger.log_error("Problems with columns")
            continue
        fd.write("> |")
        for a in r:
            fd.write(" " + a + " |")
        fd.write("\n")
    fd.write(">\n")
    # post message
    for line in post_message:
        fd.write("> " + line + "\n")
    fd.write("\n")
    fd.close()


def get_style():
    """
    read and condense the css file
    :return: condensed css content
    """
    fp = open(css_mail_file)
    ret = "".join([line.strip() for line in fp.readlines()])
    fp.close()
    return ret


def generate_htmlfile():
    """
    convert the md file into html
    """
    fp = open(md_mail_file)
    lines = fp.readlines()
    fp.close()
    from markdown import markdown
    from datetime import datetime
    fp = open(template_mail_file)
    text = fp.readlines()
    fp.close()
    ret_lines = []
    md_lines = markdown("".join(lines), extensions=['tables']).splitlines()
    for line in text:
        if "{% content %}" in line:
            indent = line.split("{% content %}")[0]
            for li in md_lines:
                ret_lines.append(indent + li.rstrip() + "\n")
            continue
        if "{% date %}" in line:
            line = line.replace("{% date %}", datetime.now().strftime("%Y %m %d"))
        if "{% style %}" in line:
            line = line.replace("{% style %}", get_style())
        ret_lines.append(line.rstrip() + "\n")
    fo = open(html_mail_file, "w")
    for line in ret_lines:
        fo.write(line)
    fo.close()


def restart_smtpd():
    """
    restart the mail service
    :return: execution status
    """
    ret, lines = system_exec("rcctl restart smtpd")
    for line in lines:
        if 'failed' in line:
            return False
        if 'ok' not in line:
            return False
    return True


def get_mailing_list():
    """
    get the mailing list for config file
    :return: list of mail where to send
    """
    fd = open(mailing_list_file)
    ret = fd.readlines()
    fd.close()
    return ret


def sendmail(local_mail_file, local_mailing_list):
    """

    :param local_mail_file:
    :param local_mailing_list:
    :return:
    """
    ret, lines = system_exec("cat " + local_mail_file + " | sendmail " + local_mailing_list)
    if len(lines) == 0:
        return True
    # there is a problem
    temp_pb = False
    for line in lines:
        if "451" in line:
            temp_pb = True
            break
    if not temp_pb:
        # this is a true problem
        logger.log_error("mailing", "Mail sending problem:")
        for line in lines:
            logger.log("mailing", line)
        return False
    # attempt to restart smtpd:
    if not restart_smtpd():
        # error during restart
        logger.log_error("mailing", "unable to restart smtpd")
        return False
    # resend message
    ret, lines = system_exec("cat " + local_mail_file + " | sendmail " + local_mailing_list)
    if len(lines) == 0:
        return True
    logger.log_error("mailing", "Mail sending problem:")
    for line in lines:
        logger.log("mailing", line)
    return False


def send_html():
    """
    sed a mail if exist
    """
    if not os.path.exists(html_mail_file):
        return
    logger.log("mailing", "Mail need to be sent")
    m_list = get_mailing_list()
    mailing_string = " ".join(m_list)
    header_lines = "\n".join(["From: maintenance@argawaen.net", "To: " + mailing_string,
                              "Subject: Activity repport from argawaen.net server", "Mime-Version: 1.0",
                              "Content-Type: text/html"])
    fd = open(html_mail_file)
    html_lines_mail = fd.readlines()
    fd.close()
    mail_txt = open(mail_to_send, "w")
    mail_txt.write(header_lines + "\n")
    mail_txt.write("\n")
    for line in html_lines_mail:
        mail_txt.write(line + "\n")
    mail_txt.close()
    if not sendmail(mail_to_send, mailing_string):
        # do save+flush ONLY if mail is sent successfully
        return
    save_dir = os.path.join(data_dir, "save")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for f in [md_mail_file, html_mail_file, mail_to_send]:
        shutil.copy2(f, os.path.join(save_dir, os.path.basename(f)))


def end_mail_procedure(cleanup: bool = True):
    """
    gather all stuf, send mail and clean
    :return:
    """
    if not os.path.exists(md_mail_file):
        return
    logger.log("mailing", "Mail need to be sent")
    generate_htmlfile()
    send_html()
    clean_mail()
