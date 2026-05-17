import numpy as np


def generate_user_embeddings(n_users=50000, dim=64):
    return np.random.normal(0, 1, (n_users, dim)).astype("float32")


def generate_item_embeddings(n_items=200000, dim=64):
    return np.random.normal(0, 1, (n_items, dim)).astype("float32")


def save():
    users = generate_user_embeddings()
    items = generate_item_embeddings()

    np.save("user_embeddings.npy", users)
    np.save("item_embeddings.npy", items)


if __name__ == "__main__":
    save()