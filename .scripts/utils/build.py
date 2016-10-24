#!/usr/bin/env python3

import datetime
import os

import jinja2

import utils

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '../..')
TEMPLATE_DIR = os.path.join(HERE, '../templates')

# Returns the comment count for the date.
def build_for_date(date):
    template_file = os.path.join(TEMPLATE_DIR, 'day.html')
    destination_dir = os.path.join(ROOT, '%04d' % date.year, '%02d' % date.month, '%02d' % date.day)
    os.makedirs(destination_dir, exist_ok=True)
    destination_file = os.path.join(destination_dir, 'index.html')
    comments = utils.comments_from_date(date)
    with open(template_file) as fin:
        with open(destination_file, 'w') as fout:
            template = jinja2.Template(fin.read())
            fout.write(template.render(
                comments=comments,
                date=date.strftime('%Y-%m-%d'),
            ))
    return len(comments)

# dates is a list of tuples (date, count), where date is the %Y-%m-%d string.
# Returns the comment count for the month.
def build_for_month(month, dates):
    template_file = os.path.join(TEMPLATE_DIR, 'month.html')
    destination_dir = os.path.join(ROOT, '%04d' % month.year, '%02d' % month.month)
    os.makedirs(destination_dir, exist_ok=True)
    destination_file = os.path.join(destination_dir, 'index.html')
    with open(template_file) as fin:
        with open(destination_file, 'w') as fout:
            template = jinja2.Template(fin.read())
            fout.write(template.render(
                dates=dates,
                month=month.strftime('%Y-%m'),
            ))
    return sum([count for _, count in dates])

# months is a list of tuples (month, count), where month is the %Y-%m string.
# Returns the comment count for the year.
def build_for_year(year, months):
    template_file = os.path.join(TEMPLATE_DIR, 'year.html')
    destination_dir = os.path.join(ROOT, '%04d' % year.year)
    os.makedirs(destination_dir, exist_ok=True)
    destination_file = os.path.join(destination_dir, 'index.html')
    with open(template_file) as fin:
        with open(destination_file, 'w') as fout:
            template = jinja2.Template(fin.read())
            fout.write(template.render(
                months=months,
                year=year.strftime('%Y'),
            ))
    return sum([count for _, count in months])

def build_latest():
    template_file = os.path.join(TEMPLATE_DIR, 'latest.html')
    destination_dir = os.path.join(ROOT, 'latest')
    os.makedirs(destination_dir, exist_ok=True)
    destination_file = os.path.join(destination_dir, 'index.html')
    comments = utils.recent_comments(30)
    with open(template_file) as fin:
        with open(destination_file, 'w') as fout:
            template = jinja2.Template(fin.read())
            fout.write(template.render(
                comments=comments,
            ))
    return len(comments)

# dates is a list of tuples (date, count), where date is the %Y-%m-%d string.
# Returns the total comment count.
def build_index(dates):
    template_file = os.path.join(TEMPLATE_DIR, 'index.html')
    destination_file = os.path.join(ROOT, 'index.html')
    with open(template_file) as fin:
        with open(destination_file, 'w') as fout:
            template = jinja2.Template(fin.read())
            fout.write(template.render(
                dates=dates,
                last_updated=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            ))
    return sum([count for _, count in dates])

def main():
    utils.fetch_comments(force=True)
    utils.ensure_short_urls_all()
    earliest_date = utils.earliest_date()
    today = datetime.datetime.utcnow().date()

    # Generate daily pages
    daterange = utils.date_range(earliest_date, today)
    dates = []
    for date in daterange:
        dates.append((date, build_for_date(date)))

    # Generate monthly pages
    month = datetime.date(earliest_date.year, earliest_date.month, 1)
    dates_in_month = []
    months = []
    for date, count in dates:
        if date.year == month.year and date.month == month.month:
            dates_in_month.append((date.strftime('%Y-%m-%d'), count))
        else:
            # New month
            months.append((month, build_for_month(month, dates_in_month)))
            month = datetime.date(date.year, date.month, 1)
    months.append((month, build_for_month(month, dates_in_month)))

    # Generate yearly pages
    year = datetime.date(earliest_date.year, 1, 1)
    months_in_year = []
    for month, count in months:
        if month.year == year.year:
            months_in_year.append((month.strftime('%Y-%m'), count))
        else:
            # New year
            build_for_year(year, months_in_year)
            year = datetime.date(month.year, 1, 1)
    build_for_year(year, months_in_year)

    # Generate latest
    build_latest()

    # Generate index
    build_index([(date.strftime('%Y-%m-%d'), count) for date, count in reversed(dates)])

if __name__ == '__main__':
    main()
