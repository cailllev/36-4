from copy import deepcopy
from itertools import permutations
from random import shuffle
import logging
import sys


class Card:
    def __init__(self, suit: str, value: int):
        self._suit = suit
        self._value = value

    def __str__(self):
        return self._suit[:4] + ":" + str(self._value).rjust(2, " ")

    def lower(self, other):
        if not isinstance(other, Card):
            return False
        if self._suit != other._suit:
            return False
        return self._value < other._value


class Deck:
    cards_per_suit = 9
    min_value = 6

    def __init__(self):
        self._cards = []
        for suit in ["Schelle", "Schilte", "Eichel", "Rose"]:
            min_val = Deck.min_value
            max_val = min_val + Deck.cards_per_suit
            for value in range(min_val, max_val):
                self._cards.append(Card(suit, value))
        shuffle(self._cards)

    def draw(self):
        return self._cards.pop()


class Board:
    def __init__(self):
        self._slots = [[], [], [], []]
        self._deck = Deck()

    def __str__(self):
        s = []
        max_per_slot = max(len(slot) for slot in self._slots)
        for i in range(max_per_slot):
            sl = []
            for slot in self._slots:
                if i < len(slot):
                    sl.append(str(slot[i]))
                else:
                    sl.append("....:..")
            s.append(" - ".join(sl))
        return "\n".join(s)

    def _remove_cards(self, simulate: bool):
        if simulate:
            slots = deepcopy(self._slots)
        else:
            slots = self._slots

        # check for removals
        removed_count = 0
        to_check = True
        while to_check:
            for i1, i2 in permutations(range(len(slots)), 2):
                if not len(slots[i1]) or not len(slots[i2]):
                    continue  # ignore empty slot

                card1, card2 = slots[i1][-1], slots[i2][-1]
                if card1.lower(card2):
                    slots[i1].pop()  # remove card
                    removed_count += 1
                    break

            else:  # => no cards removed in current round
                to_check = False

        if not simulate:
            logging.debug(f"Removed {removed_count} cards.")
        return removed_count

    def _check_best_to_move(self):
        # check which slot to move to is best
        # moving a card and removing no others (max_rem_count = 0) is better than not moving (max_rem_count = -1)
        max_removed_count, slot_to_remove_card, slot_nr = -1, None, None
        to_check = True
        while to_check:
            to_check = False

            for i, slot in enumerate(self._slots):  # slot to take from
                if not len(slot) > 1:
                    continue  # cannot take from empty (impossible) or 1 card (superfluous) slot

                empty_slot = [slot.pop()]  # move top card to empty slot
                removed_count = self._remove_cards(simulate=True)  # simulate removal on new board
                slot.append(empty_slot.pop())  # move card back
                if removed_count > max_removed_count:
                    max_removed_count, slot_to_remove_card, slot_nr = removed_count, slot, i

        if max_removed_count > 0:
            logging.debug(f"Removing {max_removed_count} cards when swapping from slot nr {slot_nr}")
        return slot_to_remove_card

    def play_turn(self):
        for slot in self._slots:  # put new cards on top
            slot.append(self._deck.draw())
        logging.info(f"Played cards:\n{self}")

        # remove cards, swap if possible, remove again, swap again, until no further removals
        to_check = True
        while to_check:
            to_check = False
            _ = self._remove_cards(simulate=False)
            free_slots = [slot for slot in self._slots if len(slot) == 0]
            logging.debug(f"After removal:\n{self}")

            # check if cards were removed and empty slot exists
            if len(free_slots) > 0:
                if slot := self._check_best_to_move():  # check from which slot the top card should be moved now
                    free_slots[0].append(slot.pop())  # move top card to first free slot
                    to_check = True

    def cards_count(self):
        return sum(len(slot) for slot in self._slots)


class Game:
    def __init__(self):
        self._board = Board()
        logging.basicConfig(stream=sys.stdout, filemode='w', level=logging.ERROR)

    def play_round(self):
        for _ in range(Deck.cards_per_suit):
            self._board.play_turn()
        c = self._board.cards_count()
        logging.warning(f"Finished with {c} cards")
        return c


def simulate():
    import matplotlib.pyplot as plt

    c = 0
    y = [0] * 37
    rounds = 10**6
    for i in range(rounds):
        game = Game()
        i = game.play_round()
        y[i] += 1
        c += i
    logging.error(f"Average: {c / rounds}")  # Average: 11.858757

    x = range(37)
    fig, ax = plt.subplots()
    ax.bar(x, y, width=1, edgecolor="white", linewidth=0.7)
    plt.show()


if __name__ == "__main__":
    simulate()
