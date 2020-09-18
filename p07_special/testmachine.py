
from common.maintenance import logger
from common.MailingSystem import add_paragraph_with_array
from common.machine import get_current_day_machines


def network():
    """
    compute network statistics
    :return:
    """
    titles, rows = get_current_day_machines()
    logger.log("daily", "Connected machines:")
    logger.log("daily", "\n".join(["\t".join(titles), ["\t".join(r) for r in rows]]))
    add_paragraph_with_array("Connected machines", col_titles=titles, rows=rows)


def main(dry_run: bool = False):
    """
    do the job
    :param dry_run: not a true execution
    """
    if not dry_run:
        network()
