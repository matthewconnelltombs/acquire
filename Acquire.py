import numpy as np
import pygame
import random
import math
import sys

random.seed()

# Constants
TILE_SIZE = 75

ROW_COUNT = 9
COLUMN_COUNT = 12 + 8

WINDOW_WIDTH = COLUMN_COUNT * TILE_SIZE
WINDOW_HEIGHT = ROW_COUNT * TILE_SIZE

# Initialize Pygame
pygame.init()
game_screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Acquire Game')

# Fonts
font_small = pygame.font.Font(None, 18)
font_medium = pygame.font.Font(None, 30)
font_large = pygame.font.Font(None, 40)

# Color
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BG_COLOR = pygame.Color('gray')
BOARD_COLOR = pygame.Color('white')
TEXT_COLOR = pygame.Color('black')

# Company Colors
PURPLE = (138, 43, 226)
ORANGE = (255, 97, 3)
GREEN = (69, 139, 0)
GOLD = (255, 185, 15)
BLUE = (30, 144, 255)
RED = (255, 48, 48)
GRAY = (128, 128, 128)
No_Company_Col = (205, 192, 176)

# Reference Card
Score_Card = np.array([[ 2,  0,  0,  200,  2000, 1000],
                       [ 3,  2,  0,  300,  3000, 1500],
                       [ 4,  3,  2,  400,  4000, 2000],
                       [ 5,  4,  3,  500,  5000, 2500],
                       [ 6,  5,  4,  600,  6000, 3000],
                       [11,  6,  5,  700,  7000, 3500],
                       [21, 11,  6,  800,  8000, 4000],
                       [31, 21, 11,  900,  9000, 4500],
                       [41, 31, 21, 1000, 10000, 5000],
                       [99, 41, 31, 1100, 11000, 5500],
                       [99, 99, 41, 1200, 12000, 6000]])
Score_Card_Str = np.array([[    "2",     "-",     "-",   "200",  "2,000", "1,000"],
                           [    "3",     "2",     "-",   "300",  "3,000", "1,500"],
                           [    "4",     "3",     "2",   "400",  "4,000", "2,000"],
                           [    "5",     "4",     "3",   "500",  "5,000", "2,500"],
                           [ "6-10",     "5",     "4",   "600",  "6,000", "3,000"],
                           ["11-20",  "6-10",     "5",   "700",  "7,000", "3,500"],
                           ["21-30", "11-20",  "6-10",   "800",  "8,000", "4,000"],
                           ["31-40", "21-20", "11-20",   "900",  "9,000", "4,500"],
                           [  "41+", "31-40", "21-30", "1,000", "10,000", "5,000"],
                           [    "-",   "41+", "31-40", "1,100", "11,000", "5,500"],
                           [    "-",     "-",   "41+", "1,200", "12,000", "6,000"]])


# Define a Tile
class Tile:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.position = str(col + 1) + "abcdefghi"[row]
        self.owner = "unplaced"

    def change_ownership(self, new_owner):
        self.owner = new_owner

    # Draws the tile on the board, merger indicates a circle draw
    def draw(self, screen, color=WHITE, merger=False):
        rect = pygame.Rect(self.col * TILE_SIZE, self.row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, pygame.Color('blue'), rect)
        pygame.draw.rect(screen, color, rect.inflate(-5, -5))
        text = font_medium.render(f'{self.position}', True, TEXT_COLOR)
        screen.blit(text, (self.col * TILE_SIZE + 35 - 5 * len(f'{self.position}'), self.row * TILE_SIZE + 28))

        if merger:
            circle_center = ((self.col + 0.5) * TILE_SIZE, (self.row + 0.5) * TILE_SIZE)
            pygame.draw.circle(screen, BLACK, circle_center, 0.45 * TILE_SIZE, 3)


# Define a Player
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.money = 6000
        self.stock = {}

    def add_tile_to_hand(self, bag):
        if len(bag) != 0:
            tile = bag.pop(random.choice(list(bag.keys())))
            self.hand.append(tile)

    def remove_tile_from_hand(self, tile):
        if tile in self.hand:
            self.hand.remove(tile)

    def increase_money(self, amount):
        self.money += amount

    def decrease_money(self, amount):
        self.money -= amount

    def add_stock(self, hotel, count):
        if hotel in self.stock:
            self.stock[hotel] += count
        else:
            self.stock[hotel] = count

    def remove_stock(self, hotel, count):
        if hotel in self.stock:
            self.stock[hotel] -= count

    def invalid_tiles(self, bag={}, replace=True):
        count = 0
        for tile in self.hand:
            touching_hotel = game.touching_hotel(tile)
            if len(touching_hotel) > 1:
                company_len = [len(hotel.tiles) for hotel in touching_hotel]
                # More than one hotel is safe
                if sum(1 if length >= 11 else 0 for length in company_len) > 1:
                    # Tile is invalid
                    if replace:
                        self.remove_tile_from_hand(tile)
                        self.add_tile_to_hand(bag)
                    else:
                        count += 1
        if not replace:
            return count

    def playable_tiles(self):
        count = len(self.hand) - self.invalid_tiles(replace=False)

        for tile in self.hand:
            touching_hotel = game.touching_hotel(tile)
            new_comp_tiles = game.touching_board(tile)
            # if the tile is not touching a hotel
            if len(touching_hotel) == 0:
                # check if a new company would be made but all 7 companies exist
                if len(new_comp_tiles) >= 1 and not game.empty_companies:
                    count -= 1

        return count == 0

    # draws the tiles to screen
    def draw_tiles(self, screen):
        for col in range(len(self.hand)):
            rectangle = pygame.Rect(5 + (13.75 + col) * TILE_SIZE, 6.75 * TILE_SIZE + 5,
                                    TILE_SIZE - 5, TILE_SIZE - 5)
            pygame.draw.rect(screen, WHITE, rectangle)

            label = font_medium.render(self.hand[col].position, True, BLACK)
            screen.blit(label, label.get_rect(center=rectangle.center))

            pygame.display.update()

    def cover_tile(self, screen, tile):
        rectangle = pygame.Rect(5 + (13.75 + self.hand.index(tile)) * TILE_SIZE, 6.75 * TILE_SIZE + 5,
                                TILE_SIZE - 5, TILE_SIZE - 5)
        pygame.draw.rect(screen, BLACK, rectangle)

        pygame.display.update()


# Define a Hotel
class Hotel:
    def __init__(self, name, tier, color):
        self.name = name
        self.tier = tier
        self.color = color
        self.tiles = []
        self.available_stock = 25
        self.stock_choice_amount = 0

    @property
    def size(self):
        return len(self.tiles)

    @property
    def stock_price(self):
        return Score_Card[next((i for i, val in enumerate(Score_Card[:, self.tier - 1])
                                if val > self.size), - 1) - 1][3] if self.size >= 2 else 0

    @property
    def major_bonus(self):
        return Score_Card[next((i for i, val in enumerate(Score_Card[:, self.tier - 1])
                                if val > self.size), - 1) - 1][4] if self.size >= 2 else 0

    @property
    def minor_bonus(self):
        return Score_Card[next((i for i, val in enumerate(Score_Card[:, self.tier - 1])
                                if val > self.size), - 1) - 1][5] if self.size >= 2 else 0

    def add_tile(self, tile):
        self.tiles.append(tile)

    def clear_tiles(self):
        self.tiles = []

    def increase_stock(self, count):
        self.available_stock += count

    def decrease_stock(self, count):
        self.available_stock -= count

    # keeps track of players purchasing
    def stock_choice(self, choice):
        if choice == self.stock_choice_amount:
            self.stock_choice_amount = 0
        elif choice <= self.available_stock:
            self.stock_choice_amount = choice


# Define the Board
class Board:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.tiles = []

    def place_tile(self, tile):
        self.tiles.append(tile)

    def remove_tile(self, tile):
        if tile in self.tiles:
            self.tiles.remove(tile)


# Define the Game

class AcquireGame:
    def __init__(self, game_items):
        self.screen = game_items["screen"]
        self.board = game_items["game_board"]
        self.tile_bag = game_items["tile_bag"]
        self.lst_players = game_items["players"]
        self.lst_hotels = game_items["hotels"]
        self.turn_counter = random.randint(0, len(self.lst_players) - 1)
        self.game_state = 0

    # True if empty company exists
    @property
    def empty_companies(self):
        counter = 0

        for hotel in self.lst_hotels:
            if not hotel.tiles:
                counter += 1

        return True if counter > 0 else False

    @property
    def active_player(self):
        return self.lst_players[self.turn_counter]

    def next_game_state(self, num=1):
        self.game_state = (self.game_state + num) % 5

    def next_turn(self):
        self.turn_counter = (self.turn_counter + 1) % len(self.lst_players)

    def reset_stock_picks(self):
        for hotel in self.lst_hotels:
            hotel.stock_choice(0)

    # checks what tiles on board would form a hotel with new tile
    def touching_board(self, tile):
        list_of_tiles = [tile]
        prev_list = []

        while list_of_tiles != prev_list:
            prev_list = list_of_tiles.copy()

            for c_tile in list_of_tiles:
                for b_tile in self.board.tiles:
                    if abs(c_tile.row - b_tile.row) == 1 and abs(c_tile.col - b_tile.col) == 0 or \
                       abs(c_tile.row - b_tile.row) == 0 and abs(c_tile.col - b_tile.col) == 1:
                        if b_tile not in list_of_tiles:
                            list_of_tiles.append(b_tile)

        list_of_tiles.remove(tile)

        return list_of_tiles

    # checks if places tile is touching any hotels
    def touching_hotel(self, tile):
        temp_list = []

        for hotel in self.lst_hotels:
            for each_tile in hotel.tiles:
                if abs(tile.row - each_tile.row) == 1 and abs(tile.col - each_tile.col) == 0 or \
                   abs(tile.row - each_tile.row) == 0 and abs(tile.col - each_tile.col) == 1:
                    if hotel not in temp_list:
                        temp_list.append(hotel)

        return temp_list

    # checks endgame conditions
    def endgame_con(self):
        length_41 = False
        all_hotels_safe = True
        companies_exist = False

        # 41 or more in length
        for hotel in self.lst_hotels:
            if len(hotel.tiles) >= 41:
                length_41 = True

            # all hotels are safe
            elif 0 < len(hotel.tiles) < 11:
                all_hotels_safe = False

            # at least one hotel exists
            if 0 < len(hotel.tiles):
                companies_exist = True

        return length_41 or (all_hotels_safe and companies_exist)

    # draw active player name
    def active_player_name(self):
        label = font_medium.render(self.active_player.name + "'s Turn", True, WHITE)
        self.screen.blit(label, (15.75 * TILE_SIZE - 6 * len(self.active_player.name), 32.5 + 6 * TILE_SIZE))
        pygame.display.update()

    # draw active player info -> stocks, money
    def active_player_info(self):
        # Stocks
        for iter, hotel in enumerate(self.lst_hotels):
            rectangle = pygame.Rect(3 + 12.1 * TILE_SIZE, 7 + (20 + iter) / 3 * TILE_SIZE,
                                    TILE_SIZE - 6, 1 / 3 * TILE_SIZE - 9)
            pygame.draw.rect(self.screen, hotel.color, rectangle)

            label = font_small.render(hotel.name, True, WHITE)
            self.screen.blit(label, label.get_rect(center=rectangle.center))

            rectangle = pygame.Rect(3 + 13.1 * TILE_SIZE, 7 + (20 + iter) / 3 * TILE_SIZE,
                                    0.5 * (TILE_SIZE - 6), 1 / 3 * TILE_SIZE - 9)
            pygame.draw.rect(self.screen, WHITE, rectangle)
            label = font_small.render(str(self.active_player.stock.get(hotel.name, 0)), True, BLACK)
            self.screen.blit(label, label.get_rect(center=rectangle.center))

        # Money
        rectangle = pygame.Rect(3 + 13.75 * TILE_SIZE, 7 + (8 + 1 / 5) * TILE_SIZE,
                                TILE_SIZE - 6, 2 / 3 * TILE_SIZE - 9)
        pygame.draw.rect(self.screen, WHITE, rectangle)

        label = font_small.render("MONEY", True, BLACK)
        self.screen.blit(label, label.get_rect(center=pygame.Rect(5 + 13.75 * TILE_SIZE, 7 + (8 + 1 / 5) * TILE_SIZE,
                                                                  TILE_SIZE - 9, 1 / 2 * TILE_SIZE - 9).center))
        label = font_small.render(str(self.active_player.money), True, BLACK)
        self.screen.blit(label, label.get_rect(center=pygame.Rect(5 + 13.75 * TILE_SIZE, 7 + (8 + 2 / 5) * TILE_SIZE,
                                                                  TILE_SIZE - 9, 1 / 2 * TILE_SIZE - 9).center))

        pygame.display.update()

    # draw the game board
    def draw_board(self):
        for tile in self.board.tiles:
            tile.draw(self.screen, No_Company_Col)

        for player in self.lst_players:
            for tile in player.hand:
                tile.draw(self.screen)

        for hotel in self.lst_hotels:
            for tile in hotel.tiles:
                tile.draw(self.screen, hotel.color)

        for key, value in self.tile_bag.items():
            value.draw(self.screen)

        pygame.display.update()

    # draw the reference card
    def draw_ref_card(self):
        # Draws the white and black squares on the reference card
        for col in range(6):
            rect = pygame.Rect((13 + col) * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.screen, BLACK, rect)
            pygame.draw.rect(self.screen, WHITE, rect.inflate(-6, -6))
            for row in range(3, 14):
                rect = pygame.Rect((13 + col) * TILE_SIZE, row * 1/3 * TILE_SIZE, TILE_SIZE, 1/3 * TILE_SIZE)
                pygame.draw.rect(self.screen, BLACK, rect)
                pygame.draw.rect(self.screen, WHITE, rect.inflate(-6, -6))

        rect = pygame.Rect((13 + 4) * TILE_SIZE, 0, TILE_SIZE * 2, TILE_SIZE * 0.7)
        pygame.draw.rect(self.screen, BLACK, rect)
        pygame.draw.rect(self.screen, WHITE, rect.inflate(-6, -6))

        # Inserts the reference information - TOP
        hotel_names = []
        hotel_colors = []
        for hotel in self.lst_hotels:
            hotel_names.append(hotel.name)
            hotel_colors.append(hotel.color)

        for index, (name, color) in enumerate(zip(hotel_names, hotel_colors)):

            rectangle = pygame.Rect(3 + (13 + (index+1)//3) * TILE_SIZE,
                                    7 + ((index+1) % 3 + ((index+1)//3 - 1)/2) * (1/3 * TILE_SIZE - 4),
                                    TILE_SIZE - 6, 1 / 3 * TILE_SIZE - 7)
            pygame.draw.rect(self.screen, color, rectangle)

            label = font_small.render(name, True, WHITE)
            self.screen.blit(label, label.get_rect(center=rectangle.center))

        for i in range(3):
            label_str = ["STOCK", "BUY/SELL", "PRICE"][i]
            self.screen.blit(font_small.render(label_str, True, BLACK),
                        ((13.16 + 3.36) * TILE_SIZE - 4 * (len(label_str)),
                        12 + i / 5 * TILE_SIZE))

        label = font_small.render("SHAREHOLDERS", True, BLACK)
        self.screen.blit(label, label.get_rect(center=pygame.Rect((13 + 4) * TILE_SIZE, 0,
                                                                  TILE_SIZE * 2, TILE_SIZE * 0.5).center))
        label = font_small.render("BONUS", True, BLACK)
        self.screen.blit(label, label.get_rect(center=pygame.Rect((13 + 4) * TILE_SIZE, TILE_SIZE * 0.1,
                                                                  TILE_SIZE * 2, TILE_SIZE * 0.7).center))
        label = font_small.render("MAJORITY", True, BLACK)
        self.screen.blit(label, label.get_rect(center=pygame.Rect((13 + 4) * TILE_SIZE, TILE_SIZE * 0.7,
                                                                  TILE_SIZE, TILE_SIZE * 0.3).center))
        label = font_small.render("MINORITY", True, BLACK)
        self.screen.blit(label, label.get_rect(center=pygame.Rect((13 + 5) * TILE_SIZE, TILE_SIZE * 0.7,
                                                                  TILE_SIZE, TILE_SIZE * 0.3).center))


        # Inserts the reference information - Bottom
        for c in range(6):
            for r in range(11):
                rect = pygame.Rect((13 + c) * TILE_SIZE, (3 + r) * 1 / 3 * TILE_SIZE, TILE_SIZE, 1 / 3 * TILE_SIZE)
                label_str = Score_Card_Str[r][c]
                label = font_small.render(label_str, True, BLACK)
                # self.screen.blit(label, (65 - 5 * len(label_str) + (12.75 + c) * TILE_SIZE,
                #                          33 + (r + 2) * 1/3 * TILE_SIZE))
                self.screen.blit(label, label.get_rect(center=rect.center))
        pygame.display.update()

    # draw the stock purchasing buttons
    def stock_button(self):
        for index, hotel in enumerate(self.lst_hotels):
            # Hotel Name
            rectangle = pygame.Rect(3 + (12.5 + index) * TILE_SIZE, 7 + 14 / 3 * TILE_SIZE,
                                    TILE_SIZE - 6, 1 / 3 * TILE_SIZE - 9)
            pygame.draw.rect(self.screen, hotel.color, rectangle)

            label = font_small.render(hotel.name, True, WHITE)
            self.screen.blit(label, label.get_rect(center=rectangle.center))

            # Hotel Remaining Stock
            rectangle = pygame.Rect(3 + (12.5 + index) * TILE_SIZE, 7 + 15 / 3 * TILE_SIZE,
                                    TILE_SIZE - 6, 1 / 3 * TILE_SIZE - 9)
            pygame.draw.rect(self.screen, WHITE, rectangle)

            label = font_small.render(str(hotel.available_stock) + " Left", True, BLACK)
            self.screen.blit(label, label.get_rect(center=rectangle.center))

        for row in range(3):
            for col, hotel in enumerate(self.lst_hotels):
                rectangle = pygame.Rect(3 + (12.5 + col) * TILE_SIZE, 7 + (16 + row)/3 * TILE_SIZE,
                                        TILE_SIZE - 6, 1 / 3 * TILE_SIZE - 9)

                if hotel.stock_choice_amount == row + 1:
                    pygame.draw.rect(self.screen, (0, 255, 0), rectangle)
                else:
                    pygame.draw.rect(self.screen, (160, 160, 160), rectangle)

                label = font_small.render(str(row + 1), True, BLACK)
                self.screen.blit(label, label.get_rect(center=rectangle.center))

                if hotel.available_stock < row + 1:
                    pygame.draw.rect(self.screen, BLACK, rectangle)
        pygame.display.update()

    # draws button in bottom right with given text
    def button(self, text):
        rectangle = pygame.Rect(18 * TILE_SIZE, 8 * TILE_SIZE, 1.9 * TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(self.screen, WHITE, rectangle)

        label = font_large.render(text, True, BLACK)
        self.screen.blit(label, label.get_rect(center=rectangle.center))
        pygame.display.update()

    # trade/sell/keep buttons for given hotel
    def tsk_button(self, hotel):
        rect = pygame.Rect(15 * TILE_SIZE, 8 * TILE_SIZE, 4 * TILE_SIZE, 2 * TILE_SIZE)
        pygame.draw.rect(self.screen, BLACK, rect)

        options = ["TRADE", "SELL", "KEEP"]

        if self.active_player.stock[hotel.name] < 2:
            options.pop(0)

        for index, text in enumerate(options[::-1]):
            rectangle = pygame.Rect((18.32 - 1.66 * index) * TILE_SIZE, 8 * TILE_SIZE, 1.6 * TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.screen, WHITE, rectangle)

            label = font_large.render(text, True, BLACK)
            self.screen.blit(label, label.get_rect(center=rectangle.center))

        pygame.display.update()

    # offers end game option
    def endgame_button(self):
        label = font_large.render("End Game?", True, WHITE)
        self.screen.blit(label, (15.3 * TILE_SIZE, 7.85 * TILE_SIZE))

        for index, text in enumerate(["Yes", "No"]):
            rectangle = pygame.Rect((15 + 1.3 * index) * TILE_SIZE, 8.25 * TILE_SIZE, 1.2 * TILE_SIZE, 0.75 * TILE_SIZE)
            pygame.draw.rect(self.screen, WHITE, rectangle)

            label = font_large.render(text, True, BLACK)
            self.screen.blit(label, label.get_rect(center=rectangle.center))
        pygame.display.update()

    # displays which hotel is being absorbed
    def hotel_choice(self, hotels):
        for index, hotel in enumerate(hotels):
            rectangle = pygame.Rect(3 + (15.25 + index % 2) * TILE_SIZE, 7 + (24 + index//2) / 3 * TILE_SIZE,
                                    TILE_SIZE - 6, 1 / 3 * TILE_SIZE - 9)
            pygame.draw.rect(self.screen, hotel.color, rectangle)

            label = font_small.render(hotel.name, True, WHITE)
            self.screen.blit(label, label.get_rect(center=rectangle.center))
        pygame.display.update()

    def clear_info(self):
        rectangle = pygame.Rect(12 * TILE_SIZE, 6.45 * TILE_SIZE, 8 * TILE_SIZE, 3 * TILE_SIZE)
        pygame.draw.rect(self.screen, BLACK, rectangle)
        pygame.display.update()

    def winner(self):
        player_money = {}

        for player in self.lst_players:
            player_money[player.name] = player.money

        sorted_players = sorted(player_money, key=lambda x: player_money[x], reverse=True)

        rectangle = pygame.Rect(12 * TILE_SIZE, 14/3 * TILE_SIZE, 8 * TILE_SIZE, 5 * TILE_SIZE)
        pygame.draw.rect(self.screen, BLACK, rectangle)

        rectangle = pygame.Rect(5 + 13 * TILE_SIZE, 7 + 14 / 3 * TILE_SIZE,
                                6 * TILE_SIZE - 9, 3.1 * TILE_SIZE)
        pygame.draw.rect(self.screen, WHITE, rectangle)

        places = ["Winner", "Second", "Third", "Fourth", "Fifth", "Sixth"]

        counts = {}
        finish_place = [counts.setdefault(item, index) for index, item
                        in enumerate(sorted(list(player_money.values()), reverse=True))]

        for iter, (player, finish) in enumerate(zip(sorted_players, finish_place)):

            label = font_large.render(places[finish], True, BLACK)
            self.screen.blit(label, label.get_rect(
                center=pygame.Rect(7 + 13 * TILE_SIZE, 7 + (14.5 / 3 + iter / 2.5) * TILE_SIZE,
                                   2 * TILE_SIZE, 0.5 * TILE_SIZE).center))

            label = font_large.render(sorted_players[iter], True, BLACK)
            self.screen.blit(label, label.get_rect(
                center=pygame.Rect(7 + 15 * TILE_SIZE, 7 + (14.5 / 3 + iter / 2.5) * TILE_SIZE,
                                   2 * TILE_SIZE, 0.5 * TILE_SIZE).center))

            label = font_large.render(str(player_money[sorted_players[iter]]), True, BLACK)
            self.screen.blit(label, label.get_rect(
                center=pygame.Rect(7 + 17 * TILE_SIZE, 7 + (14.5 / 3 + iter / 2.5) * TILE_SIZE,
                                   2 * TILE_SIZE, 0.5 * TILE_SIZE).center))

        pygame.display.update()

    def shareholder_bonus(self, a_hotel):
        player_stocks = {}
        for player in self.lst_players:
            if a_hotel.name in player.stock:
                if player.stock[a_hotel.name] != 0:
                    player_stocks[player] = player.stock[a_hotel.name]

        max_amount = max(list(player_stocks.values()))
        count_max_player = list(player_stocks.values()).count(max_amount)
        total_bonus = a_hotel.major_bonus + a_hotel.minor_bonus

        if count_max_player > 1:
            money_split = math.ceil((total_bonus / count_max_player) / 100) * 100

            for player, stock in player_stocks.items():
                if stock == max_amount:
                    player.increase_money(money_split)

        else:
            for player, stock in player_stocks.items():
                if stock == max_amount:
                    player.increase_money(a_hotel.major_bonus)

            if len(player_stocks) == 1:
                list(player_stocks.keys())[0].increase_money(a_hotel.minor_bonus)

            else:
                second_max_amount = sorted(set(list(player_stocks.values())))[-2]
                count_sec_max_player = list(player_stocks.values()).count(second_max_amount)

                money_split = math.ceil((a_hotel.minor_bonus / count_sec_max_player) / 100) * 100

                for player, stock in player_stocks.items():
                    if stock == second_max_amount:
                        player.increase_money(money_split)


def new_game():
    # Tile Creation
    tile_bag = {}
    for row in range(9): #9
        for col in range(12): #12
            name = str(col + 1) + "abcdefghi"[row]
            tile_bag[name] = Tile(row, col)

    # Game initialization
    game_board = Board(9, 12)

    # Player Names
    with open("player_name.txt", "r") as file:
        player_name = file.read()

    player_name = player_name.strip().split('\n')

    # Check if correct number of players
    if len(player_name) < 2 or len(player_name) > 6:
        print("The number of players is not allowed.")
        pygame.quit()
        sys.exit()

    player_list = []

    for iter, player in enumerate(player_name):
        player_list.append(Player(player_name[iter]))

    # Adding tiles to players hands
    for player in player_list:
        for iter in range(6):
            player.add_tile_to_hand(tile_bag)

    for iter in range(len(player_list)):
        if len(tile_bag) != 0:
            tile = tile_bag.pop(random.choice(list(tile_bag.keys())))
            game_board.place_tile(tile)

    Worldwide = Hotel("Worldwide", 1, PURPLE)
    Sackson = Hotel("Sackson", 1, ORANGE)
    Festival = Hotel("Festival", 2, GREEN)
    Imperial = Hotel("Imperial", 2, GOLD)
    American = Hotel("American", 2, BLUE)
    Continental = Hotel("Continental", 3, RED)
    Tower = Hotel("Tower", 3, GRAY)
    Company_List = [Worldwide, Sackson, Festival, Imperial, American, Continental, Tower]

    game = AcquireGame({"game_board": game_board,
                        "players": player_list,
                        "hotels": Company_List,
                        "tile_bag": tile_bag,
                        "screen": game_screen})

    # Board Setup
    game.screen.fill(BLACK)
    game.draw_board()
    game.draw_ref_card()
    game.stock_button()
    game.button("START")
    game.active_player_name()

    return game


game = new_game()

# Main game loop
game_over = False
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            posx = event.pos[0]
            posy = event.pos[1]

            # Display Player Information
            if game.game_state == 0 and \
                    TILE_SIZE * 18 <= posx <= TILE_SIZE * 20 and TILE_SIZE * 8 <= posy <= TILE_SIZE * 9:

                game.active_player.draw_tiles(game_screen)
                game.active_player_info()
                game.button("TILE")

                game.next_game_state()

            # Tile Selection
            if game.game_state == 1:
                # checks if player has no playable tiles
                if game.active_player.playable_tiles():
                    rectangle = pygame.Rect(15.75 * TILE_SIZE, 7.75 * TILE_SIZE + 5,
                                            TILE_SIZE * 2, 0.2 * TILE_SIZE)
                    label = font_small.render("No Playable Tiles", True, WHITE)
                    game.screen.blit(label, label.get_rect(center=rectangle.center))
                    game.button("NEXT")
                    while True:
                        event = pygame.event.wait()
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if TILE_SIZE * 18 <= event.pos[0] <= TILE_SIZE * 20 and \
                                    TILE_SIZE * 8 <= event.pos[1] <= TILE_SIZE * 9:
                                pygame.draw.rect(game.screen, BLACK, rectangle)
                                game.next_game_state(2)
                                game.button("BUY")
                                break
                else:
                    for c in range(len(game.active_player.hand)):
                        if TILE_SIZE * (13.75 + c) <= posx <= TILE_SIZE * (14.75 + c) and \
                                TILE_SIZE * (6 + 5/6) <= posy <= TILE_SIZE * (7 + 5/6):

                            selected_tile = game.active_player.hand[c]
                            touch_hotel = game.touching_hotel(selected_tile)
                            new_company_tiles = game.touching_board(selected_tile)

                            # if the placed tile is not touching a hotel
                            if len(touch_hotel) == 0:

                                # check if a new company would be made but all 7 companies exist
                                if len(new_company_tiles) >= 1 and not game.empty_companies:
                                    pass

                                else:
                                    game.active_player.cover_tile(game.screen, selected_tile)
                                    game.active_player.remove_tile_from_hand(selected_tile)
                                    game.board.place_tile(selected_tile)

                                    # Check if a company is created
                                    if len(new_company_tiles) >= 1:
                                        game.next_game_state()
                                        game.button("COMPANY")

                                    # Move to buy
                                    elif sum([len(hotel.tiles) for hotel in game.lst_hotels]) > 0:
                                        game.next_game_state(2)
                                        game.button("BUY")

                                    # Skip to next turn if no company exists to buy stocks from
                                    else:
                                        game.next_game_state(3)

                            # if the placed tile is touching exactly hotel
                            elif len(touch_hotel) == 1:
                                game.active_player.cover_tile(game.screen, selected_tile)
                                game.active_player.remove_tile_from_hand(selected_tile)

                                if new_company_tiles:
                                    for tile in new_company_tiles:
                                        game.board.remove_tile(tile)
                                        touch_hotel[0].add_tile(tile)

                                touch_hotel[0].add_tile(selected_tile)

                                game.next_game_state(2)
                                game.button("BUY")

                            # if the placed tile is touching more than one hotel
                            elif len(touch_hotel) > 1:
                                selected_tile.draw(game_screen, merger=True)
                                company_length = [len(hotel.tiles) for hotel in touch_hotel]

                                # More than one hotel is safe
                                if sum(1 if length >= 11 else 0 for length in company_length) > 1:
                                    pass

                                else:
                                    max_length = max(company_length)
                                    sorted_hotel = []

                                    for size in sorted(set(company_length), reverse=True):
                                        if company_length.count(size) == 1:
                                            sorted_hotel.append(touch_hotel[company_length.index(size)])
                                        else:
                                            indices = [i for i, num in enumerate(company_length) if num == size]
                                            temp_hotel = [touch_hotel[i] for i in indices]

                                            while len(temp_hotel) > 1:
                                                outer_loop_flag = False
                                                game.hotel_choice(temp_hotel)

                                                for event in pygame.event.get():
                                                    if event.type == pygame.QUIT:
                                                        pygame.quit()
                                                        sys.exit()

                                                    if event.type == pygame.MOUSEBUTTONDOWN:
                                                        posx = event.pos[0]
                                                        posy = event.pos[1]

                                                        # Selected Hotel
                                                        for index, hotel in enumerate(temp_hotel):
                                                            if 7 + (15.25 + index % 2) * TILE_SIZE <= posx \
                                                                    <= (16.25 + index % 2) * TILE_SIZE - 2 and \
                                                                    7 + (24 + index//2) / 3 * TILE_SIZE <= posy \
                                                                    <= (25 + index//2) / 3 * TILE_SIZE - 2:
                                                                sorted_hotel.append(hotel)
                                                                temp_hotel.remove(hotel)

                                                                outer_loop_flag = True
                                                                break

                                                    if outer_loop_flag:
                                                        break

                                            sorted_hotel.append(temp_hotel[0])

                                    large_hotel = sorted_hotel[0]
                                    sorted_hotel.remove(large_hotel)

                                    for acquired_hotel in sorted_hotel:
                                        # Shareholder Bonus
                                        game.shareholder_bonus(acquired_hotel)

                                        game.active_player_info()

                                        # Trade/Sell/Keep
                                        for iter_turn in range(len(game.lst_players)):
                                            if game.active_player.stock[acquired_hotel.name] != 0:
                                                while True:
                                                    game.tsk_button(acquired_hotel)

                                                    # Show which hotel is being acquired
                                                    rectangle = pygame.Rect(3 + 13.75 * TILE_SIZE, 10 + 7.8 * TILE_SIZE,
                                                                            TILE_SIZE - 6, 1 / 3 * TILE_SIZE - 9)
                                                    pygame.draw.rect(game.screen, acquired_hotel.color, rectangle)
                                                    label = font_small.render(acquired_hotel.name, True, WHITE)
                                                    game.screen.blit(label, label.get_rect(center=rectangle.center))

                                                    event = pygame.event.wait()
                                                    if event.type == pygame.MOUSEBUTTONDOWN:
                                                        if event.type == pygame.QUIT:
                                                            pygame.quit()
                                                            sys.exit()

                                                        posx = event.pos[0]
                                                        posy = event.pos[1]

                                                        # Trade
                                                        if TILE_SIZE * 15 <= posx <= TILE_SIZE * (15 + 1.6) and \
                                                                TILE_SIZE * 8 <= posy <= TILE_SIZE * 9:
                                                            if game.active_player.stock[acquired_hotel.name] >= 2 and \
                                                                    large_hotel.available_stock > 0:

                                                                large_hotel.decrease_stock(1)
                                                                game.active_player.add_stock(large_hotel.name, 1)
                                                                game.active_player.remove_stock(acquired_hotel.name, 2)
                                                                acquired_hotel.increase_stock(2)

                                                                game.active_player_info()

                                                        # Sell
                                                        elif TILE_SIZE * (15 + 1.66) <= posx <= TILE_SIZE * (15 + 3.26) and \
                                                                TILE_SIZE * 8 <= posy <= TILE_SIZE * 9:
                                                            if game.active_player.stock[acquired_hotel.name] > 0:

                                                                acquired_hotel.increase_stock(1)
                                                                game.active_player.remove_stock(acquired_hotel.name, 1)
                                                                game.active_player.increase_money(acquired_hotel.stock_price)

                                                                game.active_player_info()

                                                        # Keep
                                                        elif TILE_SIZE * (15 + 3.32) <= posx <= TILE_SIZE * (15 + 4.92) and \
                                                                TILE_SIZE * 8 <= posy <= TILE_SIZE * 9:
                                                            break

                                                        if game.active_player.stock[acquired_hotel.name] == 0:
                                                            break

                                            game.next_turn()

                                            if game.active_player.stock[acquired_hotel.name] != 0:

                                                game.clear_info()
                                                game.stock_button()
                                                game.button("START")
                                                game.active_player_name()

                                                while True:
                                                    event = pygame.event.wait()
                                                    if event.type == pygame.QUIT:
                                                        pygame.quit()
                                                        sys.exit()

                                                    if event.type == pygame.MOUSEBUTTONDOWN:
                                                        if TILE_SIZE * 18 <= event.pos[0] <= TILE_SIZE * 20 and \
                                                                TILE_SIZE * 8 <= event.pos[1] <= TILE_SIZE * 9:
                                                            break

                                                game.active_player.draw_tiles(game_screen)
                                                game.active_player_info()

                                        game.clear_info()
                                        game.stock_button()
                                        game.button("START")
                                        game.active_player_name()

                                        while True:
                                            event = pygame.event.wait()
                                            if event.type == pygame.QUIT:
                                                pygame.quit()
                                                sys.exit()

                                            if event.type == pygame.MOUSEBUTTONDOWN:
                                                if TILE_SIZE * 18 <= event.pos[0] <= TILE_SIZE * 20 and \
                                                        TILE_SIZE * 8 <= event.pos[1] <= TILE_SIZE * 9:
                                                    break

                                        game.active_player.draw_tiles(game_screen)
                                        game.active_player_info()

                                        # Move tiles to new hotel
                                        large_hotel.tiles.extend(acquired_hotel.tiles)
                                        acquired_hotel.clear_tiles()

                                    # Remove played Tile
                                    game.active_player.cover_tile(game.screen, selected_tile)
                                    game.active_player.remove_tile_from_hand(selected_tile)
                                    large_hotel.add_tile(selected_tile)

                                    # Move tiles on board next to played tile
                                    if new_company_tiles:
                                        for tile in new_company_tiles:
                                            game.board.remove_tile(tile)
                                            large_hotel.add_tile(tile)

                                    game.button("BUY")
                                    game.next_game_state(2)

                            game.draw_board()

            # Company Creation
            elif game.game_state == 2:
                for row, hotel in enumerate(game.lst_hotels):
                    if len(hotel.tiles) == 0 and \
                            TILE_SIZE * 12.1 + 3 <= posx <= TILE_SIZE * 13.2 - 3 and \
                            TILE_SIZE * (20 + row) / 3 + 7 <= posy <= TILE_SIZE * (21 + row) / 3 - 2:

                        for tile in new_company_tiles:
                            game.board.remove_tile(tile)

                        game.board.remove_tile(selected_tile)

                        hotel.tiles = new_company_tiles + [selected_tile]

                        if hotel.available_stock > 0:
                            game.active_player.add_stock(hotel.name, 1)
                            hotel.decrease_stock(1)
                            game.active_player_info()
                            game.stock_button()

                        game.draw_board()
                        game.next_game_state()
                        game.button("BUY")

            # Selecting which stocks to buy
            elif game.game_state == 3:
                for row in range(3):
                    for col, hotel in enumerate(game.lst_hotels):
                        if hotel.tiles:
                            if (12.5 + col) * TILE_SIZE + 3 <= posx <= (13.5 + col) * TILE_SIZE - 3 and \
                                    TILE_SIZE * (16 + row)/3 + 7 <= posy <= TILE_SIZE * (17 + row)/3 - 2:

                                cur_stock_amount = hotel.stock_choice_amount
                                hotel.stock_choice(row + 1)

                                cost_of_purchase = 0
                                purchase_count = 0
                                for c_hotel in game.lst_hotels:
                                    cost_of_purchase += c_hotel.stock_price * c_hotel.stock_choice_amount
                                    purchase_count += c_hotel.stock_choice_amount

                                if cost_of_purchase > game.active_player.money or purchase_count > 3:
                                    hotel.stock_choice(cur_stock_amount)

                                game.stock_button()

                if TILE_SIZE * 18 <= posx <= TILE_SIZE * 20 and \
                        TILE_SIZE * 8 <= posy <= TILE_SIZE * 9:
                    for hotel in game.lst_hotels:
                        game.active_player.add_stock(hotel.name, hotel.stock_choice_amount)
                        game.active_player.decrease_money(hotel.stock_price * hotel.stock_choice_amount)
                        hotel.decrease_stock(hotel.stock_choice_amount)
                        hotel.stock_choice(0)

                    game.reset_stock_picks()
                    game.stock_button()
                    game.next_game_state()

        if game.game_state == 4:
            # Check For Game Ending Conditions
            if game.endgame_con():
                game.endgame_button()

                while True:
                    event = pygame.event.wait()
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if 15 * TILE_SIZE <= event.pos[0] <= 16.2 * TILE_SIZE and \
                                8.25 * TILE_SIZE <= event.pos[1] <= 9 * TILE_SIZE:
                            game_over = True
                            break
                        elif 16.3 * TILE_SIZE <= event.pos[0] <= 17.5 * TILE_SIZE and \
                                8.25 * TILE_SIZE <= event.pos[1] <= 9 * TILE_SIZE:
                            break

            if not game_over:
                # Next Players Turn
                game.active_player.add_tile_to_hand(game.tile_bag)
                game.active_player.invalid_tiles(game.tile_bag, replace=True)

                game.next_game_state()
                game.next_turn()
                game.clear_info()
                game.button("START")
                game.active_player_name()

        # Game Over
        if game_over:
            # Scoring

            # Shareholder Bonuses
            for hotel in game.lst_hotels:
                if hotel.available_stock != 25:
                    game.shareholder_bonus(hotel)

                    # Stock Payout
                    for player in game.lst_players:
                        player.increase_money(hotel.stock_price * player.stock[hotel.name])

            # Final Scores
            game.winner()

            # Play Again
            while True:
                game.button("Play Again")
                event = pygame.event.wait()
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if TILE_SIZE * 18 <= event.pos[0] <= TILE_SIZE * 20 and \
                            TILE_SIZE * 8 <= event.pos[1] <= TILE_SIZE * 9:
                        game = new_game()
                        game_over = False
                        break

