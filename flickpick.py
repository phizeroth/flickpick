from collections import OrderedDict
from prettytable import PrettyTable
from prettytable import from_db_cursor
import datetime
import os
import random
import sys

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
		
		
def main_menu_loop():
	"""Show the menu"""
	choice = None
	
	while choice not in ('q', 'quit', 'exit'):
		print("=== main menu ===")
		for key, value in menu.items():
			print("{}) {}".format(key, value.__doc__))
		print("q) Quit")
		choice = input('Choice:  ').lower().strip()
		
		if choice in menu:
			menu[choice]()
			
			
			
# === MENU OPTIONS ===

def add_flick():
	"""Add a flick"""
	inp = input("Whose flick is this?  ").title()
	if inp in ('Amanda', 'Philip'):
		owner_ = inp
	elif inp == 'Finch':
		owner_ = 'Philip'
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
		
	if input("Add flick? (y/n):  ").lower() != 'n':
		
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
	"""List All"""
	curs = db.get_cursor()
	
	def pretty_table():
		col_names = [cn[0] for cn in curs.description]
		rows = curs.fetchall()
		pt = from_db_cursor(curs)
		
		x = PrettyTable(col_names)
		x.align[col_names[1]] = 'l'
		x.align[col_names[2]] = 'r'
		x.padding_width = 1
		for row in rows:
			x.add_row(row)
		x.sortby = "rank"
		print(x)
	
	clear()
	curs.execute('SELECT rank, title, genre, avail FROM Flick WHERE owner = "Philip"')
	print("\n| Philip's List |")
	pretty_table()
	
	curs.execute('SELECT rank, title, genre, avail FROM Flick WHERE owner = "Amanda"')
	print("\n| Amanda's List |")
	pretty_table()
	
	
def del_flick():
	"""Delete a flick"""
	list_all()
	inp = input("Enter title of flick to delete:  ")
	d = Flick.get(Flick.title == inp)
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
	
	while choice not in ('q', 'quit', 'exit'):
		list_all()
		print("=== edit menu === {} ===".format(row.title))
		for key, value in edit_menu.items():
			print("{}) {}".format(key, value))
		print("x) Exit to main menu")
		choice = input('Choice:  ').lower().strip()
		
		if choice in edit_menu:
			edit_apply(row, edit_menu[choice])
		else:
			clear()
			break
	

def test_func():
	"""Test function"""
	list_all()
	Flick.get(Flick.title == "Testing").delete_instance()
		 
		 
# === MENUS ===
menu = OrderedDict([
		('a', add_flick),
		('d', del_flick),
		('e', edit_menu_loop),
		('la', list_all),	
		#('ls', list_selection),
		#('lw', list_watched),
		#('pick', pick_flick),
		('test', test_func),
	])

edit_menu = OrderedDict([
		('r', 'rank'),
		('t', 'title'),
		('g', 'genre'),
		('a', 'avail'),
		#('w', 'watched')
	])

select_menu = OrderedDict([
#		('t', choose_top),
#		('g', choose_genre),
#		('v', toggle_avail),
	])


# === MAIN ===
if __name__ == '__main__':
	initialize()
	main_menu_loop()