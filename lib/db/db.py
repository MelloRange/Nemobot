from os.path import isfile
from sqlite3 import connect

from apscheduler.triggers.cron import CronTrigger

DB_PATH = "./data/db/database.db"
BUILD_PATH = "./data/db/build.sql"

conn = connect(DB_PATH, check_same_thread=False)
c = conn.cursor()


def with_commit(func):
	def inner(*args, **kwargs):
		func(*args, **kwargs)
		commit()

	return inner


@with_commit
def build():
	if isfile(BUILD_PATH):
		executescript(BUILD_PATH)


def commit():
	print("Committing...")
	conn.commit()


def autosave(sched):
	sched.add_job(commit, CronTrigger(second=0))


def close():
	conn.close()


def get_one(command, *values):
	c.execute(command, tuple(values))

	if (fetch := c.fetchone()) is not None:
		return fetch[0]
	else:
		return None


def get_line(command, *values):
	c.execute(command, tuple(values))

	return c.fetchone()


def get_all(command, *values):
	c.execute(command, tuple(values))

	return c.fetchall()


def get_column(command, *values):
	c.execute(command, tuple(values))

	return [item[0] for item in c.fetchall()]


def execute(command, *values):
	c.execute(command, tuple(values))


def executemany(command, valueset):
	c.executemany(command, valueset)


def executescript(path):
	with open(path, "r", encoding="utf-8") as script:
		c.executescript(script.read())