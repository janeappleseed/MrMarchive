#!/usr/bin/env python3

"""Additional utilities that extend MrMsay."""

import datetime
import logging

import mrmsay.logger
mrmsay.logger.logger_init(level=logging.DEBUG)
import mrmsay.db
import mrmsay.remote
from mrmsay.db import Comment, dump_comments as recent_comments
from mrmsay.remote import fetch_comments

__all__ = [
    'comments_from_date',
    'date_range',
    'earliest_date',
    'ensure_short_urls_all',
    'fetch_comments',
]

# UTC date of the earliest date in the database.
# Raises IndexError if the database is empty.
def earliest_date():
    earliest_comment = Comment.select().order_by(Comment.created_at).limit(1)[0]
    return earliest_comment.created_at.date()

# start_date and end_date should both be datetime.date objects.
# Range is inclusive on both ends.
def date_range(start_date, end_date):
    date = start_date
    while date <= end_date:
        yield date
        date += datetime.timedelta(1)

# Similar to date_range.
def month_range(start_date, end_date):
    month = datetime.date(start_date.year, start_date.month, 1)
    while month <= end_date:
        yield month
        if month.month == 12:
            month = datetime.date(month.year + 1, 1, 1)
        else:
            month = datetime.date(month.year, month.month + 1, 1)

# Similar to date_range.
def year_range(start_date, end_date):
    year = datetime.date(start_date.year, 1, 1)
    while year <= end_date:
        yield year
        year = datetime.date(year.year + 1, 1, 1)

def comments_from_date(date):
    date_str = date.strftime('%Y-%m-%d')
    return (Comment.select().where(Comment.created_at.startswith(date_str))
            .order_by(Comment.created_at.desc()))

def ensure_short_urls_all():
    for comment in Comment.select().where(Comment.short_url == ''):
        comment.short_url = mrmsay.remote.shorten_url(comment.url)
        comment.save()
