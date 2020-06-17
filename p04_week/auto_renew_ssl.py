#!/usr/bin/env python
"""
procedures to renew SSL certificates
"""
from common.maintenance import logger, system_exec, add_mail


def check_certificates():
    ret, lines = system_exec("certbot certificates")
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
        add_mail("SSL certificates are still valid")
    else:
        logger.log("autoSSLRenew", "Certificates due to renewal")
        ret, lines = system_exec("certbot renew" + ["", " --dry-run"][dry_run])
        if ret != 0:
            logger.log_error("autoSSLRenew", "certbot return code (" + str(ret) + ")")
            for line in lines:
                logger.log_error("autoSSLRenew", line)
            return
        if check_certificates() or dry_run:
            logger.log("autoSSLRenew", "SSL Certificates have been successfully renewed")
            add_mail("SSL Certificates have been successfully renewed")
        else:
            logger.log_error("autoSSLRenew", "SSL Certificates are still invalid after renew")
            add_mail("SSL Certificates are still invalid after renew")
            add_mail("[VERBATIM]")
            for line in lines:
                logger.log_error("autoSSLRenew", line)
                add_mail(line)
            add_mail("[/VERBATIM]")


if __name__ == "__main__":
    main()
