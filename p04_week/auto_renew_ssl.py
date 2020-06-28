#!/usr/bin/env python
"""
procedures to renew SSL certificates
"""
from common.maintenance import logger, system_exec
from common.MailingSystem import add_paragraph, add_paragraph_with_lines


def check_certificates():
    """
    check the actual certificates to see if a renewal has to be done
    :return: True if the certificates are still valid
    """
    ret, lines = system_exec("/usr/local/bin/certbot certificates")
    if ret != 0:
        logger.log_error("autoSSLRenew", "getting certificates (" + str(ret) + ")")
        for line in lines:
            logger.log_error("autoSSLRenew", line)
    for line in lines:
        if "INVALID" in line:
            return False
        if "VALID:" in line:
            try:
                days = int(line.split("VALID:")[-1].split("day")[0])
            except:
                return False
            if days < 25:
                return False
    return True


def main(dry_run: bool = False):
    """
    main script execution
    :param dry_run: if the script should be run without system modification
    :return:
    """
    #
    if check_certificates():
        logger.log("autoSSLRenew", "Certificates Still valid")
        add_paragraph("SSL renewal", message="SSL certificates are still valid")
    else:
        logger.log("autoSSLRenew", "Certificates due to renewal")
        ret, lines = system_exec("/usr/local/bin/certbot renew" + ["", " --dry-run"][dry_run])
        if ret != 0:
            logger.log_error("autoSSLRenew", "certbot return code (" + str(ret) + ")")
            for line in lines:
                logger.log_error("autoSSLRenew", line)
            return
        if check_certificates() or dry_run:
            logger.log("autoSSLRenew", "SSL Certificates have been successfully renewed")
            add_paragraph("SSL renewal", message="SSL Certificates have been successfully renewed")
        else:
            logger.log_error("autoSSLRenew", "SSL Certificates are still invalid after renew\n" + "\n".join(lines))
            add_paragraph_with_lines("SSL renewal", pre_message=["SSL Certificates are still invalid after renew"],
                                     lines=lines)


if __name__ == "__main__":
    main()
