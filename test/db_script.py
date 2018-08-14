from db_test import db
db.drop_all()
db.create_all()
from db_test import User, Entry
from datetime import datetime
t1 = datetime.utcnow()
t2 = datetime.utcnow()

# children (the many relationship) need to be created w/
# a parent as an entry; the creation of the parent is not dependent on the child
# e.g. you can create a user w/o entries, but you can'tcreate an entry w/o a user
sam = User(username='sam', join_time=t1)
aria = User(username='aria', join_time=t2)
david = User(username='david', join_time=datetime.utcnow())

e1 = Entry(entry="entry 1", entry_time=datetime.utcnow(), user=sam)
e2 = Entry(entry="entry 2", entry_time=datetime.utcnow(), user=aria)
e3 = Entry(entry="entry 3", entry_time=datetime.utcnow(), user=sam)
e4 = Entry(entry="entry 4", entry_time=datetime.utcnow(), user=sam)
e5 = Entry(entry="entry 5", entry_time=datetime.utcnow(), user=sam)
db.session.add_all([sam, aria, david, e1, e2])
db.session.add_all([e3, e4, e5])
db.session.commit()


# query all entries w user_id = 1
Entry.query.filter_by(user_id=1).all()

# count entries of above
# filter uses operator overloading
Entry.query.filter(Entry.user_id==1).count()

# Convert it
