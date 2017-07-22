from peewee import *

database = SqliteDatabase('phash.db')


def before_request_handler():
    database.connect()


def after_request_handler():
    database.close()


class Image(Model):
    key = CharField(unique=True)
    gallery_id = CharField()
    phash = CharField()

    class Meta:
        database = database

if __name__ == '__main__':
    for image in Image.select():
        print image.phash