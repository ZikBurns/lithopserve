import contextlib
from multiprocessing import Pipe, Process
from lithopserve.worker.profiler import Profiler
import logging

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def profiling_context(jobrunner_conn, monitored_process_pid, prometheus, job, profiler_timeout):
    """
    Context manager that starts a profiling process for a monitored process,
    and ensures a graceful cleanup when done.
    """
    parent_conn, child_conn = Pipe()  # Create a pipe for inter-process communication
    profiler = Profiler()

    # Start the profiling process
    monitoring_process = _start_monitoring_process(profiler, child_conn, monitored_process_pid, prometheus, job, profiler_timeout)

    try:
        yield profiler  # Yield control to the caller with the profiler object
    finally:
        try:
            _send_stop_signal(parent_conn)  # Send a signal to stop profiling
        except Exception as e:
            logger.error(f"Failed to send stop signal: {e}")

        try:
            _handle_jobrunner_signal(jobrunner_conn)  # Check for signals from the jobrunner
        except Exception as e:
            logger.error(f"Error handling jobrunner signal: {e}")

        _finalize_process(monitoring_process, parent_conn, profiler)  # Ensure the process finishes and collect data

        _close_connections(parent_conn, child_conn)  # Close pipes to free resources


def _start_monitoring_process(profiler, child_conn, monitored_process_pid, prometheus, job, profiler_timeout):
    """
    Start the profiling process.
    """
    monitoring_process = Process(
        target=profiler.start_profiling,
        args=(child_conn, monitored_process_pid, prometheus, job, profiler_timeout)
    )
    monitoring_process.start()
    return monitoring_process


def _send_stop_signal(parent_conn):
    """
    Send a stop signal to the profiling process through the pipe.
    """
    if parent_conn and parent_conn.writable:
        parent_conn.send("stop")
    else:
        logger.warning("Parent connection is not writable")


def _handle_jobrunner_signal(jobrunner_conn):
    """
    Check if the jobrunner has sent a 'Finished' signal and send a 'stop' signal if necessary.
    """
    if jobrunner_conn.poll():
        message = jobrunner_conn.recv()
        if message == "Finished":
            _send_stop_signal(jobrunner_conn)


def _finalize_process(monitoring_process, parent_conn, profiler):
    """
    Ensure the profiling process finishes within the timeout and update the profiler with the collected data.
    """
    try:
        # Wait for the process to finish, or force terminate if it's still alive after the timeout
        monitoring_process.join(timeout=5)
        if monitoring_process.is_alive():
            logger.warning("Profiling process is still alive, terminating...")
            monitoring_process.terminate()
            monitoring_process.join()  # Ensure the process has fully stopped

    except Exception as e:
        logger.error(f"Error finalizing profiling process: {e}")
        if monitoring_process.is_alive():
            monitoring_process.terminate()
            monitoring_process.join()


def _close_connections(parent_conn, child_conn):
    """
    Close the pipe connections to release resources.
    """
    try:
        if parent_conn:
            parent_conn.close()
        if child_conn:
            child_conn.close()
    except Exception as e:
        logger.error(f"Error closing pipe connections: {e}")
