#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Mod: mailman

:Synopsis:

:Author:
    servilla

:Created:
    4/15/21
"""
import logging
import os
import smtplib

import click
from colorama import init, Fore, Style
import daiquiri


cwd = os.path.dirname(os.path.realpath(__file__))
logfile = cwd + "/mailman.log"
daiquiri.setup(
    level=logging.INFO,
    outputs=(
        daiquiri.output.File(logfile),
        "stdout",
    ),
)
logger = daiquiri.getLogger(__name__)


def send_mail(smtp_obj, subj: str, to: tuple, frm: str, msg: str) -> int:
    status = 1

    body = (
        ("Subject: " + subj + "\n").encode()
        + ("To: " + ",".join(to) + "\n").encode()
        + ("From: " + frm + "\n\n").encode()
        + (msg + "\n").encode()
    )

    init()
    user = input(Fore.RED + "User: ")
    passwd = input(Fore.RED + "Password: ")
    print(Style.RESET_ALL)

    try:
        smtp_obj.ehlo()
        smtp_obj.login(user, passwd)
        if smtp_obj.default_port != 465:
            smtp_obj.starttls()
            smtp_obj.ehlo()
        smtp_obj.sendmail(from_addr=frm, to_addrs=to, msg=body)
        status = 0
        logger.info(f"Sending email to: {to}")
    except Exception as e:
        errmsg = f"Sending email failed: {e}"
        logger.error(errmsg)
    finally:
        smtp_obj.quit()
    return status


help_subj = "Subject line (optional)"


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("to", nargs=-1, required=True)
@click.argument("frm", nargs=1)
@click.argument("msg", nargs=1)
@click.argument("host", nargs=1)
@click.argument("port", nargs=1)
@click.option("-s", "--subj", default="", help=help_subj)
def main(to: tuple, frm: str, msg: str, host: str, port: str, subj: str):
    """
    Simple module to test email relay host functionality.

    \b
        TO: Space separated list of destination email addresses.
        FRM: Source email address
        MSG: Quoted string message
        HOST: SMTP relay host
        PORT: SMTP connection port (SSL: 465, non-SSL: 25,587, or 8025)
    """
    port = int(port)
    if port == 465:
        smtp_obj = smtplib.SMTP_SSL(host, port)
    else:
        smtp_obj = smtplib.SMTP(host, port)
    logger.info(f"Created smtpObj to {host} on port {port}")
    status = send_mail(smtp_obj, subj, to, frm, msg)
    return status


if __name__ == "__main__":
    main()
