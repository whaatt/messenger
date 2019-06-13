import os
from pathlib import Path

from peewee import (
    AutoField,
    CharField,
    Check,
    CompositeKey,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
    TextField,
)
from playhouse.sqlite_ext import FTS5Model, RowIDField, SearchField

_repo_root = os.path.dirname(__file__)
_data_dir = os.path.join(_repo_root, "data")
Path(_data_dir).mkdir(exist_ok=True)


class AssetType:
    Photo = "photo"
    Video = "video"
    Audio = "audio"
    Gif = "gif"
    Sticker = "sticker"
    Link = "link"
    Other = "other"


class EventType:
    Call = "call"
    Subscribe = "subscribe"
    Unsubscribe = "unsubscribe"


def get_chat_db(chat_name, truncate=False):
    """Returns a fresh chat DB instance (really a namespace) containing table references."""
    db_file = os.path.join(_data_dir, chat_name + ".db")
    if truncate and os.path.exists(db_file):
        os.remove(db_file)
    db = SqliteDatabase(db_file)

    class BaseModel(Model):
        class Meta:
            database = db

    class User(BaseModel):
        name = CharField(primary_key=True)

    class Message(BaseModel):
        id = AutoField()  # Auto-added, but let's be explicit here.
        sender = ForeignKeyField(User, backref="messages")
        timestamp = DateTimeField()
        content = TextField(null=True)

        class Meta:
            indexes = ((("sender", "timestamp"), True),)

    class MessageIndex(FTS5Model):
        content = SearchField()

        class Meta:
            database = db

    class Reaction(BaseModel):
        user = ForeignKeyField(User, backref="reactions")
        message = ForeignKeyField(Message, backref="messages")
        reaction = CharField()

        class Meta:
            primary_key = CompositeKey("user", "message")

    class Asset(BaseModel):
        id = AutoField()
        message = ForeignKeyField(Message, backref="assets")
        path = TextField()
        type = CharField()  # AssetType.X
        timestamp = DateTimeField(null=True)

        class Meta:
            indexes = ((("message", "path"), True),)

    class Event(BaseModel):
        id = AutoField()
        actor = ForeignKeyField(User, backref="acted_events")
        timestamp = DateTimeField()
        type = CharField()  # EventType.X
        target = ForeignKeyField(User, backref="targeted_events", null=True)
        duration = IntegerField(constraints=[Check("duration >= 0")], null=True)

        class Meta:
            indexes = ((("actor", "timestamp", "target"), True),)

    class ChatDB:
        def __init__(self, User, Message, MessageIndex, Reaction, Asset, Event):
            self.User = User
            self.Message = Message
            self.MessageIndex = MessageIndex
            self.Reaction = Reaction
            self.Asset = Asset
            self.Event = Event

        def open(self):
            """Returns whether connection could be opened."""
            if db.connect(reuse_if_open=True):
                db.create_tables([User, Message, MessageIndex, Reaction, Asset, Event])
                return True
            return False

        def close(self):
            return db.close()

        def is_closed(self):
            return db.is_closed()

    # Keep ChatDB constructor private but allow user to open and close instance.
    return ChatDB(
        User=User,
        Message=Message,
        MessageIndex=MessageIndex,
        Reaction=Reaction,
        Asset=Asset,
        Event=Event,
    )
