from game import Game
import sys

if __name__ == "__main__":
    # for debugging
    if "-f" in sys.argv:
        fast = True
    else:
        fast = False

    nplayer = input("Enter the number of players: ")
    if nplayer not in ['2', '3', '4']:
        print("Invalid number of players. Please enter a number between 2 and 4.")
        exit()
    game = Game(int(nplayer), fast)

