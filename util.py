import json
import os
from datetime import datetime

from schema import AssetType, EventType, get_chat_db

_repo_root = os.path.dirname(__file__)
_dump_prefix = "messages/inbox"
_message_filename = "message_1.json"


def get_dump_path(folder):
    """Returns a fully-qualified path to a particular thread dump."""
    return os.path.join(_repo_root, _dump_prefix, folder, _message_filename)


def _resolve_text(unicode_bytes):
    """Resolves Facebook text data, which is often dumped as Unicode bytes, to actual text."""
    return unicode_bytes.encode("charmap").decode("utf8")


def save_readable_titles():
    """Saves a mapping from chat title to chat folder in the data dump."""
    titles = []
    for d in os.listdir("messages/inbox"):
        # Ignore .DS_Store directories.
        if d[0] == ".":
            continue

        dump_path = get_dump_path(d)
        with open(dump_path, "r") as dump_file:
            dump = json.loads(dump_file.read())
            titles.append((_resolve_text(dump["title"]), d))

    titles.sort()
    titles_path = os.path.join(_repo_root, "titles.txt")
    with open(titles_path, "w") as title_file:
        for (readable, original) in titles:
            readable = readable.strip()
            if len(readable) == 0:
                readable = "<Deactivated User>"
            print(readable, file=title_file)
            print(f"Folder: {original}", file=title_file)
            print(file=title_file)


def _unix_to_datetime(time, is_ms=False):
    if is_ms:
        time = time / 1000
    return datetime.fromtimestamp(time)


_asset_prop_to_type = {
    "photos": AssetType.Photo,
    "videos": AssetType.Video,
    "audio_files": AssetType.Audio,
    "files": AssetType.Other,
    "gifs": AssetType.Gif,
}


def _store_message(ChatDB, m):
    sender = m["sender_name"]
    timestamp = _unix_to_datetime(m["timestamp_ms"], is_ms=True)
    m_type = m["type"]

    # Disregard content for shares (often boilerplate).
    if m_type == "Generic" and "content" in m:
        content = _resolve_text(m["content"])
    else:
        content = None

    # Store message before working on assets.
    message = ChatDB.Message.create(sender=sender, timestamp=timestamp, content=content)

    # Store Assets.
    if m_type == "Generic":
        assets = []
        # Media types that can have multiple assets at once.
        for media_type in {"photos", "videos", "audio_files", "files", "gifs"}:
            if media_type in m:
                for item in m[media_type]:
                    assets.append(
                        {
                            "message": message,
                            "type": _asset_prop_to_type[media_type],
                            "path": item["uri"],
                            "timestamp": None
                            if media_type == "gifs"
                            else _unix_to_datetime(item["creation_timestamp"]),
                        }
                    )
        # Or a single sticker.
        if "sticker" in m:
            assets.append(
                {"message": message, "type": AssetType.Sticker, "path": m["sticker"]["uri"]}
            )

        # Efficient bulk insert.
        ChatDB.Asset.insert_many(assets).execute()
    elif "share" in m:
        ChatDB.Asset.create(message=message, type=AssetType.Link, path=m["share"]["link"])

    # Store reactions.
    if "reactions" in m:
        reactions = []
        for item in m["reactions"]:
            reactions.append(
                {
                    "user": item["actor"],
                    "message": message,
                    "reaction": _resolve_text(item["reaction"]),
                }
            )

        ChatDB.Reaction.insert_many(reactions).execute()


def _store_event(ChatDB, m):
    actor = m["sender_name"]
    timestamp = _unix_to_datetime(m["timestamp_ms"], is_ms=True)
    m_type = m["type"]

    # Store Call.
    if m_type == "Call":
        if "missed" in m:
            duration = None
        else:
            duration = m["call_duration"]
        ChatDB.Event.create(
            actor=actor, timestamp=timestamp, type=EventType.Call, duration=duration
        )

    # Store Subscribes.
    elif m_type == "Subscribe":
        events = []
        for user in m["users"]:
            events.append(
                {
                    "actor": actor,
                    "timestamp": timestamp,
                    "type": EventType.Subscribe,
                    "target": user["name"],
                }
            )
        ChatDB.Event.insert_many(events).execute()

    # Store Unsubscribes.
    elif m_type == "Unsubscribe":
        events = []
        for user in m["users"]:
            events.append(
                {
                    "actor": actor,
                    "timestamp": timestamp,
                    "type": EventType.Unsubscribe,
                    "target": user["name"],
                }
            )
        ChatDB.Event.insert_many(events).execute()


def store_chat(folder):
    """Stores a chat dump in its corresponding SQLite database."""
    # Load raw data dump for folder.
    dump_path = get_dump_path(folder)
    with open(dump_path, "r") as dump_file:
        dump = json.loads(dump_file.read())

    print("Recreating chat DB from scratch.")
    ChatDB = get_chat_db(folder, truncate=True)
    ChatDB.open()

    # Create user references in DB.
    for p in dump["participants"]:
        ChatDB.User.create(name=p["name"])

    i = 0
    total = len(dump["messages"])

    # Store messages by type.
    for m in dump["messages"]:
        if m["type"] in {"Generic", "Share"}:
            _store_message(ChatDB, m)
            i += 1
        else:
            _store_event(ChatDB, m)
            i += 1
        if i % 1000 == 0:
            print(f"Stored {i} of {total} messages.")
    ChatDB.close()
    print("Done.")
