from game import Game
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fast", action="store_true", help="Enable fast mode for debugging.")
    parser.add_argument("-a", "--autoroll", action="store_true", help="Enable autoroll mode.")
    args = parser.parse_args()

    nplayer = input("Enter the number of players: ")
    if nplayer not in ['2', '3', '4']:
        print("Invalid number of players. Please enter a number between 2 and 4.")
        exit()
    game = Game(int(nplayer), args.fast, args.autoroll)
    game.run_game()

