import requests
import random

number_chars = "0123456789"
card_number_chars = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
card_quality_chars = ["C", "D", "H", "S"]
word_site = "https://www.mit.edu/~ecprice/wordlist.10000"

while (True):
    choice = input("\n\n1. Gen random string of number\n2. Gen random deck of cars\n3. Gen random word\nYour choice: ")
    if (choice == "1"):
        nnumber = input("Number of number? ")
        for i in range(0, int(nnumber)):
            if (i % 10 == 0):
                print()
            print (random.randint(0, 9), end="")
    elif (choice == "2"):
        nnumber = input("Number of card? ")
        for i in range(0, int(nnumber)):
            if (i % 2 == 0):
                print()
            print (card_number_chars[random.randint(0, len(card_number_chars) - 1)] + card_quality_chars[random.randint(0, len(card_quality_chars) - 1)] + " ", end="")
    elif (choice == "3"):
        response = requests.get(word_site)
        WORDS = response.content.splitlines()
        nnumber = input("Number of word? ")
        for i in range(0, int(nnumber)):
            if (i % 10 == 0):
                print()
            print(WORDS[random.randint(0, len(WORDS) - 1)].decode() + ",", end="")
