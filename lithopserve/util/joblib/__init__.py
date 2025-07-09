from joblib.parallel import register_parallel_backend


def register_lithops():
    """ Register Lithops Backend to be called with parallel_backend(lithopserve). """
    try:
        from lithopserve.util.joblib.lithops_backend import LithopsBackend
        register_parallel_backend("lithopserve", LithopsBackend)
    except ImportError:
        msg = ("To use the Lithops backend you must install lithopserve.")
        raise ImportError(msg)


__all__ = ["register_lithops"]
