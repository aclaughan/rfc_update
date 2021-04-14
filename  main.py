import fnmatch
import os
import smtplib
import sys

import requests

sys.path.append('/Users/alan/')
from secret import *
from email.message import EmailMessage


#
#      name: rfc_stats
# arguments: none
#   returns: dictionary of rfc stats found in local rfc directory
#               including:
#                   total number of rfc's locally
#                   number of text rfc's
#                   number of pdf rfc's
#                   highest rfc number
#                   number of missing rfc's
# ------------------------------------------------------------------------------
#
def rfc_stats():
    local_rfc_numbers = []
    rfcs = \
        {
            'ietf_url': "https://www.ietf.org/rfc",
            'rfc_dir': "/Users/alan/Documents/RFC's"
        }

    for fn in os.listdir(rfcs['rfc_dir']):
        if fnmatch.fnmatch(fn, "rfc*"):
            dot = fn.find('.')
            number = fn[3:dot]
            local_rfc_numbers.append(int(number))
            if fnmatch.fnmatch(fn, "*.txt"):
                rfcs['no_txt'] = rfcs.get('no_txt', 0) + 1
            if fnmatch.fnmatch(fn, "*.pdf"):
                rfcs['no_pdf'] = rfcs.get('no_pdf', 0) + 1

    rfcs['highest_no'] = max(local_rfc_numbers)
    rfcs['no_of_rfcs'] = len(local_rfc_numbers)
    rfcs['missing'] = [x for x in range(1, rfcs['highest_no']) if
                       x not in local_rfc_numbers]
    rfcs['no_missing_rfcs'] = len(rfcs['missing'])

    return rfcs


def download_rfcs(rfcs):
    rfcs['missing'] += range(rfcs['highest_no'] + 1, rfcs['highest_no'] + 21)

    for number in rfcs['missing']:
        rfc = requests.get(f'{rfcs["ietf_url"]}/rfc{number}.txt',
                           allow_redirects=True)
        if rfc.status_code != 404:
            open(f'{rfcs["rfc_dir"]}/rfc{number:05}.txt', 'wb+').write(
                rfc.content)
            print(f"    ADDED: rfc{number}.txt")


def summary(before, after):
    return f"""

                       before   after   diff
    -----------------------------------------
     number of rfc's:{before['no_of_rfcs']:>8}{after['no_of_rfcs']:>8}{(after['no_of_rfcs'] - before['no_of_rfcs']):>7}
       text versions:{before['no_txt']:>8}{after['no_txt']:>8}{(after['no_txt'] - before['no_txt']):>7}
        pdf versions:{before['no_pdf']:>8}{after['no_pdf']:>8}{(after['no_pdf'] - before['no_pdf']):>7}
          no missing:{before['no_missing_rfcs']:>8}{after['no_missing_rfcs']:>8}{(before['no_missing_rfcs'] - after['no_missing_rfcs']):>7}
         last rfp no:{before['highest_no']:>8}{after['highest_no']:>8}{(after['highest_no'] - before['highest_no']):>7}
         
    
    """


def email_summary(body):
    msg = EmailMessage()
    msg['Subject'] = 'ACRU | Summary'
    msg['From'] = f"Lbot <{GMUSER}>"
    msg['To'] = 'alan@claughan.com'
    msg.set_content(body)
    msg.add_alternative(f"""\
    <!DOCTYPE html>
    <html>
      <body>
        <h2 style="color:SlateGray;">Request For Comment Updater [v1.3]</h2><p>
        <pre>{body}</pre>
      </body>
    </html>
    """, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(GMUSER, GMPASS)

        smtp.send_message(msg)


def main():
    rfc_stats_before = rfc_stats()
    download_rfcs(rfc_stats_before)
    rfc_stats_after = rfc_stats()
    summary_msg = summary(rfc_stats_before, rfc_stats_after)
    print(summary_msg)
    email_summary(summary_msg)


if __name__ == '__main__':
    main()
