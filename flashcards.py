import os
from random import choice
import shutil
from io import StringIO
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--import_from')
parser.add_argument('--export_to')
args = parser.parse_args()
import_path = args.import_from
export_path = args.export_to

log = StringIO()
def to_log(message, in_input_function=False):
	if in_input_function:
		log.write(message)
	else:
		log.write(message + '\n')
	return message


class Deck(list):
	def __str__(self):
		if self:
			return ', '.join(self)
		else:
			return 'No cards in deck'

	def __setitem__(self, key, card: 'Card'):
		if isinstance(card, Card):
			super().__setitem__(key, card)
		else:
			print(to_log('Not a Card!'))

	def get_hardest_cards(self) -> 'Deck':
		max_mistakes = 0
		hardest_cards = Deck()
		for card in self:
			if card.mistakes > max_mistakes:
				hardest_cards.clear()
				hardest_cards.append(card)
				max_mistakes = card.mistakes
			elif card.mistakes == max_mistakes and max_mistakes != 0:
				hardest_cards.append(card)
		return hardest_cards

	def print_hardest_cards(self):
		hardest_cards = self.get_hardest_cards()
		if len(hardest_cards) == 0:
			print(to_log('There are no cards with errors.'))
		elif len(hardest_cards) == 1:
			card = hardest_cards[0]
			print(to_log(f'The hardest card is "{card.term}". You have {card.mistakes} errors answering it'))
		else:
			print(to_log(f'The hardest cards are {hardest_cards}'))

	def reset_stats(self):
		for card in self:
			card.mistakes = 0
		print(to_log('Card statistics have been reset.'))

	def get_terms(self):
		return [card.term for card in self]

	def get_definitions(self):
		return [card.definition for card in self]

	def check_term(self, term):
		if term not in self.get_terms():
			return True
		else:
			return False

	def check_definition(self, definition):
		if definition not in self.get_definitions():
			return True
		else:
			return False

	def get_term_for_definition(self, definition):
		for card in self:
			if definition == card.definition:
				return card.term

	def export_all(self, path):
		for card in self:
			card.export(path)

	def import_all(self, path):
		file = open(path, 'r')
		lines = file.readlines()
		for line in lines:
			term, definition = line.split(sep='|')
			definition = definition.rstrip('\n')
			if not self.check_term(term):
				for card in self:
					if term == card.term:
						card.definition = definition
			else:
				Card(self, term=term, definition=definition)
		print(to_log(f'{len(lines)} cards have been loaded.'))
		file.close()


class Card:
	def __init__(self, deck: Deck, term='', definition=''):
		self.deck = deck
		self.term = term
		self.definition = definition
		self.mistakes = 0
		self.deck.append(self)

	def __str__(self):
		return f'"{self.term}"'

	def answer(self):
		definition = to_log(input(to_log(f'Print the definition of "{self.term}":\n> ', in_input_function=True)))
		if definition == self.definition:
			print(to_log('Correct!'))
		elif definition in self.deck.get_definitions():
			print(to_log(f'Wrong. The right answer is "{self.definition}", '
			      f'but your definition is correct for "{self.deck.get_term_for_definition(definition)}".'))
			self.mistakes += 1
		else:
			print(to_log(f'Wrong. The right answer is "{self.definition}".'))
			self.mistakes += 1

	def export(self, path):
		file = open(path, 'a')
		file.write(f'{self.term}|{self.definition}\n')
		file.close()


if __name__ == '__main__':
	deck = Deck()

	if import_path is not None and os.path.isfile(import_path):
		deck.import_all(import_path)

	while True:
		command = to_log(input(to_log('\nInput the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):\n> ', in_input_function=True)))
		command = command.lower()

		if command == 'add':
			while True:
				term = to_log(input(to_log('The card:\n> ', in_input_function=True)))
				if deck.check_term(term):
					break
				else:
					print(to_log(f'The card "{term}" already exists.'))
			while True:
				definition = to_log(input(to_log('The definition of the card:\n> ', in_input_function=True)))
				if deck.check_definition(definition):
					break
				else:
					print(to_log(f'The definition "{definition}" already exists.'))
			Card(deck, term=term, definition=definition)
			print(to_log(f'The pair ("{term}":"{definition}") has been added'))

		elif command == 'remove':
			term = to_log(input(to_log('Which card?\n> ', in_input_function=True)))
			for card in deck:
				if term == card.term:
					del deck[deck.index(card)]
					print(to_log('The card has been removed.'))
					break
			else:
				print(to_log(f'Can\'t remove "{term}": there is no such card.'))

		elif command == 'import':
			path = to_log(input(to_log('File name:\n> ', in_input_function=True)))
			if not os.path.isfile(path):
				print(to_log('File not found.'))
			else:
				deck.import_all(path)

		elif command == 'export':
			path = to_log(input(to_log('File name:\n> ', in_input_function=True)))
			deck.export_all(path)
			print(to_log(f'{len(deck)} cards have been saved.'))

		elif command == 'ask':
			if deck:
				try:
					number_of_cards = int(to_log(input(to_log('How many times to ask?\n> ', in_input_function=True))))
				except ValueError:
					print(to_log('You must input number'))
					continue
				for i in range(number_of_cards):
					choice(deck).answer()
			else:
				print('(╯°□°）╯︵ ┻━┻')

		elif command == 'exit':
			if export_path:
				deck.export_all(export_path)
				print(f'{len(deck)} cards have been saved.')
			else:
				print('Bye bye!')
			log.close()

			break

		elif command == 'log':
			path = to_log(input(to_log('File name:\n> ', in_input_function=True)))
			with open(path, "w") as new_log:
				log.seek(0)
				shutil.copyfileobj(log, new_log)
			print(to_log('The log has been saved.'))

		elif command == 'hardest card': deck.print_hardest_cards()

		elif command == 'reset stats': deck.reset_stats()
