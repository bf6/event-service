#!/usr/bin/env python
import sqlite3

conn = sqlite3.connect('events.db')
c = conn.cursor()
c.execute('CREATE TABLE events (event_id text)')
conn.commit()
conn.close()
