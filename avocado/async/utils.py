from django_rq import get_worker, get_queue

from avocado.conf import settings
from avocado.query import utils


def run_jobs():
    """
    Execute all the pending jobs.
    """
    get_worker(settings.ASYNC_QUEUE).work(burst=True)


def get_job(job_id):
    """
    Return the job for the specified ID or None if it cannot be found.

    Args:
        job_id(uuid): The ID of the job to retrieve.

    Returns:
        The job with the matching ID or None if no job with the supplied job
        ID could be found.
    """
    queue = get_queue(settings.ASYNC_QUEUE)
    return queue.fetch_job(job_id)


def get_job_count():
    """
    Returns the current number of jobs in the queue.
    """
    return get_queue(settings.ASYNC_QUEUE).count


def get_job_result(job_id):
    """
    Returns the result of the job with the supplied ID.

    If the job could not be found or the job is not finished yet, None will
    be returned as the job result.

    Args:
        job_id(uuid): The ID of the job to retrieve the result for.

    Returns:
        The result of the job with the matching ID or None if the job could
        not be found or is not finished.
    """
    return get_job(job_id).result


def get_jobs():
    """
    Returns a collection of all the pending jobs.
    """
    return get_queue(settings.ASYNC_QUEUE).jobs


def cancel_job(job_id):
    """
    Cancel the job and its associated query if they exist.

    Args:
        job_id(uuid): The ID of the job to cancel

    Returns:
        The cancellation result of the job's query if it had one. If the job
        could not be found or the job had no query, this method returns None.
    """
    job = get_job(job_id)

    if job is None:
        return None

    result = None
    query_name = job.meta.get('query_name')
    if query_name:
        canceled = utils.cancel_query(query_name)
        result = {
            'canceled': canceled
        }

    job.cancel()
    return result


def cancel_all_jobs():
    """
    Cancels all jobs.
    """
    get_queue(settings.ASYNC_QUEUE).empty()
