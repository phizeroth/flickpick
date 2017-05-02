from collections import OrderedDict
from prettytable import PrettyTable
import datetime
import os
import random
import sys
import time

from peewee import *

db = SqliteDatabase('flicklist.db')



class Flick(Model):
	owner = CharField()
	rank = IntegerField()
	title = CharField()
	genre = CharField()
	avail = CharField()
	watched = BooleanField(default=False)
	date_added = DateField(default=datetime.datetime.now)
	date_watched = DateField(null=True, default=None)
	
	class Meta:
		database = db
		
		
# === SOME FUNCTIONS ===

def initialize():
	"""Create the database and the table if they don't exist"""
	db.connect()
	db.create_tables([Flick], safe=True)
		
		
def clear():
	os.system('cls' if os.name == 'nt' else 'clear')
		
#def menu_loop():

def main_menu_loop():
	"""Show the menu"""
	choice = None
	
	while choice not in ('q', 'quit', 'exit'):
		list_all()
		print("\n === main menu ===")
		for key, value in menu.items():
			print("  {}) {}".format(key, value.__doc__) if (len(key) == 1) else 
				  " {}) {}".format(key, value.__doc__))
		print("  q) Quit")
		choice = input("\nChoice:  ").lower().strip()
		
		if choice in menu:
			menu[choice]()
			
def pretty_table(q, owner):
	"""Creates pretty table"""
	rows = []
	for __ in q:
		rows.append([__.rank, __.title, __.genre, __.avail])

	print("\n| {}'s List |".format(owner))

	col_names = ['rank', 'title', 'genre', 'avail']

	x = PrettyTable(col_names)
	x.align[col_names[1]] = 'l'
	x.align[col_names[2]] = 'r'
	x.padding_width = 1
	for row in rows:
		x.add_row(row)
	print(x)
			
			
# === MENU OPTIONS ===

def add_flick():
	"""Add a flick"""
	while True:
		inp = input("Whose flick is this?  ").title()
		if inp in ('Iota', 'Phi'):
			owner_ = inp
			break
		else:
			print("I don't know that person!")
	
	title_ = input("Title:  ")
	genre_ = input("Genre:  ")
	if input("Is this flick readily available? (y/n)\n>:  ").lower() == 'y':
		avail_ = input("Source (Netflix, file, etc):  ")
	else:
		avail_ = '-'
	
	list_all()
	rank_ = input("Rank:  ")
	
	if input("Are you sure you want to add \"{}\"? (Y/n):  "
		.format(title_)).lower() != 'n':
		
		if (Flick.select()
			  .where((Flick.owner == owner_) & (Flick.rank == rank_))
			  .count() > 0):
			q = (Flick.update(rank=Flick.rank + 1)
				 .where((Flick.owner == owner_) & (Flick.rank >= rank_)))
			q.execute()
			
		Flick.create(owner=owner_,
					 title=title_,
					 genre=genre_,
					 rank=rank_,
					 avail=avail_)
		list_all()
	

def list_all():
	"""List all"""
	def query(owner):
		return ((Flick.select()
				 .where(Flick.owner == owner)
				 .order_by(Flick.rank)), owner)

	clear()
	pretty_table(*query("Phi"))
	pretty_table(*query("Iota"))


def del_flick():
	"""Delete a flick"""
	list_all()
	inp = input("Enter title of flick to delete:  ")
	d = Flick.get(Flick.title == inp)
	if input("Are you sure you want to DELETE \"{}\"? (y/N):  "
		.format(d.title)).lower() == 'y':
		q = (Flick.update(rank=Flick.rank - 1)
			 .where(Flick.rank >= d.rank))
		q.execute()
		d.delete_instance()


def edit_menu_loop():
	"""Edit flick"""
	def edit_apply(row, field):
		cur_value = getattr(row, field)
		print("Current {}: {}".format(field, cur_value))
		new_value = input("New {}:  ".format(field))
		
		if field == 'rank':
			new_value = int(new_value)
			
			if new_value > cur_value:
				q = (Flick.update(rank=Flick.rank - 1)
					 .where((Flick.owner == row.owner) & 
							(Flick.rank > cur_value) &
							(Flick.rank <= new_value)))
				q.execute()
			
			elif new_value < cur_value:
				q = (Flick.update(rank=Flick.rank + 1)
					 .where((Flick.owner == row.owner) & 
							(Flick.rank < cur_value) &
							(Flick.rank >= new_value)))
				q.execute()
		
		setattr(row, field, new_value)
		row.save()
		
	list_all()
	inp = input("Enter title of flick to edit:  ")
	row = Flick.get(Flick.title == inp)
	
	choice = None
	
	while choice not in ('x', 'exit'):
		list_all()
		print("\n === edit menu === {} ===".format(row.title))
		for key, value in edit_menu.items():
			print(" {})  {}".format(key, value))
		print(" x)  Exit to main menu")
		choice = input('\nChoice:  ').lower().strip()
		
		if choice in edit_menu:
			edit_apply(row, edit_menu[choice])


def list_selection():
	"""List selection"""
	global tq
	global gq
	global vq

	if selections['t'] == "*":
		tq = (Flick.rank != 666)
	else:
		tq = (Flick.rank <= selections['t'])

	if selections['g'] == "*":
		gq = (Flick.genre != "godisuck")
	else:
		gq = (Flick.genre == selections['g'])

	if selections['v'] == False:
		vq = (Flick.avail != "isthisreallythebestwaytodothis?")
	else:
		vq = (Flick.avail != "-")

	def query(owner):
		return ((Flick.select()
				 .where((Flick.owner == owner) &
		 				gq & tq & vq)
				 .order_by(Flick.rank)), owner)

	clear()
	pretty_table(*query("Phi"))
	pretty_table(*query("Iota"))


def flickpick_menu_loop():
	"""Flickpick Menu"""
	choice = None
	
	while choice not in ('x', 'exit'):
		list_selection()
		print("\n === flickpick menu ===")
		for key, value in flickpick_menu.items():
			print("  {}) {}  ({})".format(key, value.__doc__, selections[key]))
		print(" ------------------")
		print("  p) Pick a Flick!")
		print(" ------------------")
		print("  c) Clear all selections")
		print("  x) Exit to main menu")
		choice = input('\nChoice:  ').lower().strip()
		
		if choice in flickpick_menu:
			flickpick_menu[choice]()
		elif choice == "c":
			selections['t'] = "*"
			selections['g'] = "*"
			selections['v'] = False
		elif choice == "p":
			flickpick_go()

def choose_genre():
	"""Choose genre"""
	list_selection()
	selections['g'] = input("Pick genre ('*' for all):  ")

def choose_top():
	"""Choose top #"""
	list_selection()
	selections['t'] = input("Pick top # ('*' for all):  ")

def toggle_avail():
	"""Available"""
	if selections['v'] == False:
		selections['v'] = True
	else:
		selections['v'] = False

def test_func():
	"""Test function"""
	pass

def flickpick_go():
	"""Pick a Flick!"""

	pick = ((Flick.select()
			 .where(gq & tq & vq)
			 .order_by(fn.Random()).limit(1))
			 .get())
	clear()
	print("\n")
	for c in "=========Your pick is=========":
		sys.stdout.write( '%s' % c )
		sys.stdout.flush()
		time.sleep(0.05)
	print("\n\n" + pick.title.upper().center(30," "))
	print("\n==============================")
	input(">")


# === LISTS ===
owners = 'pass'
selections = {
	't': "*",
	'g': "*",
	'v': False
}

# === MENUS ===
menu = OrderedDict([
		('a', add_flick),
		('d', del_flick),
		('e', edit_menu_loop),
#		('la', list_all),
		('p', flickpick_menu_loop),
#		('lw', list_watched),
#		('test', test_func),
	])

edit_menu = OrderedDict([
		('r', 'rank'),
		('t', 'title'),
		('g', 'genre'),
		('a', 'avail'),
#		('w', 'watched')
	])

flickpick_menu = OrderedDict([
		('t', choose_top),
		('g', choose_genre),
		('v', toggle_avail),
	])

# === MAIN ===
if __name__ == '__main__':
	initialize()
	main_menu_loop()