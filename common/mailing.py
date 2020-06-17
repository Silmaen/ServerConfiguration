#!/usr/bin/env python

from .maintenance import *
from .htmlwrite import htmlfile
import shutil

# line followed by this line is automatically transformed into 'section title'
#           h1       h2      h3     h4    h5     h6
title_str = ["======", "=====", "====", "===", "----", "---"]
# syntax coloring: key words
color_str = {"Ok": "#00C800", "Better": "#00C800", "Passed": "#00C800", "Warning": "#FFAF00", "Worse": "#FFAF00",
             "Error": "red", "Failed": "red", "Unfeasable": "red"}
# syntax coloring: key lines
color_line = {"[V]": "#8000B8"}
#
mailing_list = ["argawaen@argawaen.net"]
mail_file_html = os.path.join(data_dir, "hmail")
mail_file_html_content = os.path.join(data_dir, "mail.html")
mailing_string = " ".join(mailing_list)


#
def convert_mail(strlist, formatted: bool = False):
    hf = htmlfile(title="[Maintenance] srv.argawaen.net")
    hf.setKeywordColor(color_str)
    hf.setFormatted(formatted)
    premode = 0
    listniv = 0
    for line_id, line in enumerate(strlist):
        cline = line.strip()
        nline = ""
        # retrieving the 'next' line
        if line_id + 1 < len(strlist):
            nline = strlist[line_id + 1]
            nline = nline.strip()
        # VERBATIM mode activation/deactivation
        if cline == "[VERBATIM]":
            hf.addLine("<pre>")
            premode = 1
            continue
        if cline == "[/VERBATIM]":
            hf.addLine("</pre>")
            premode = 0
            continue
        # if we are in VERBATIM mode: no aditionnal formating
        if premode == 1:
            hf.addLine(cline + "\n")
            continue
        # coloring line
        for key in color_line.keys():
            if cline.startswith(key):
                cline = "<font color=\"" + color_line[key] + "\">" + cline.lstrip(key).strip() + "</font>"
        #   treatment of an empty line
        if cline == "":
            # if we were in the list, close the list
            if listniv > 0:
                hf.addLine("</ul>")
                listniv = 0
            continue
        # if we are in the list, add an item to the list
        if listniv > 0:
            hf.addLine(cline, "li")
            continue
        # if the line ends with ':' then start a list
        if cline.endswith(":"):
            hf.addLine("<ul><b>" + cline + "</b>", "")
            listniv += 1
            continue
        # ignore title identifier line
        if cline in title_str:
            continue
        # check for a title modifier
        if nline in title_str:
            niv = title_str.index(nline) + 1
            if niv < 3:
                hf.addLine("<hr>")
            hf.addSection(cline, niv)
            continue
        # else: this is a standard line, write it into a paragraph
        hf.addParargraph(cline)
    hf.addLine("<hr>")
    return hf.generate()


def restart_smtpd():
    ret, lines = system_exec("rcctl restart smtpd")
    for line in lines:
        if 'failed' in line:
            return False
        if 'ok' not in line:
            return False
    return True


def sendmail(local_mail_file, local_mailing_list):
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


def main(cleanup: bool = True, formatted: bool = False):
    #
    if not os.path.exists(mail_file_txt):
        if not cleanup:
            logger.log_error("mailing", "no mail file named:" + mail_file_txt)
        return
    #
    logger.log("mailing", "Mail need to be sent")
    # get the mail data
    ffi = open(mail_file_txt, "r")
    lines = ffi.readlines()
    ffi.close()

    # store an html formatted version
    fp = open(mail_file_html_content, "w")
    fp.write(convert_mail(lines, True))
    fp.close()

    # convert to compressed html format
    html_lines_mail = convert_mail(lines, formatted)

    # create the header lines
    header_lines = "\n".join(["From: maintenance@argawaen.net", "To: " + mailing_string,
                              "Subject: Activity repport from argawaen.net server", "Mime-Version: 1.0",
                              "Content-Type: text/html"])

    mail_txt = open(mail_file_html, "w")
    mail_txt.write(header_lines + "\n")
    mail_txt.write("\n")
    mail_txt.write(html_lines_mail + "\n")
    mail_txt.close()
    if not sendmail(mail_file_html, mailing_string):
        # do save+flush ONLY if mail is sent successfully
        return
    save_dir = os.path.join(data_dir, "save")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for f in [mail_file_html, mail_file_txt, mail_file_html_content]:
        shutil.copy2(f, os.path.join(save_dir, os.path.basename(f)))
    if cleanup:
        for f in [mail_file_html, mail_file_html_content]:
            os.remove(f)
        flush_mail()


if __name__ == "__main__":
    main()
