import json
import os

repo_root = os.path.dirname(__file__)
relative_prefix = "messages/inbox"
message_filename = "message_1.json"


def resolve(unicode_bytes):
    """Facebook emoji data is often dumped as Unicode bytes."""
    return unicode_bytes.encode("charmap").decode("utf8")


def save_readable_titles():
    titles = []
    for d in os.listdir("messages/inbox"):
        # Ignore .DS_Store directories.
        if d[0] == ".":
            continue

        data_path = os.path.join(repo_root, relative_prefix, d, message_filename)
        with open(data_path, "r") as data_file:
            data = json.loads(data_file.read())
            titles.append((resolve(data["title"]), d))

    titles.sort()
    titles_path = os.path.join(repo_root, "titles.txt")
    with open(titles_path, "w") as title_file:
        for (readable, original) in titles:
            readable = readable.strip()
            if len(readable) == 0:
                readable = "<Deactivated User>"
            print(readable, file=title_file)
            print(f"Folder: {original}", file=title_file)
            print(file=title_file)
