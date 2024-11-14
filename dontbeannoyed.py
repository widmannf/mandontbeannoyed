from game import Game

if __name__ == "__main__":

    nplayer = input("Enter the number of players: ")
    if nplayer not in ['2', '3', '4']:
        print("Invalid number of players. Please enter a number between 2 and 4.")
        exit()
    game = Game(int(nplayer))

