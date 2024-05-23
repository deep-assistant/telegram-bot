import vedis

data_base = vedis.Vedis('data_base.db')


def db_key(user_id, key):
    return f"{user_id}_{key}"
