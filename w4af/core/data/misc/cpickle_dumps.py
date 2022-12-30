import pickle


def cpickle_dumps(obj):
    """
    :param obj: The object to pickle
    :return: The pickled version of obj
    """
    return pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)
