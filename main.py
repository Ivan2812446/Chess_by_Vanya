import pygame
import sys
import time
import random
import json
import os
from datetime import datetime

# Инициализация Pygame
pygame.init()
pygame.font.init()

# Константы
WIDTH, HEIGHT = 800, 600
BOARD_SIZE = 480
SQUARE_SIZE = BOARD_SIZE // 8
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
HIGHLIGHT = (100, 249, 83, 150)
MOVE_HIGHLIGHT = (249, 166, 83, 150)
RED = (255, 0, 0)
BLUE = (0, 120, 255)
GREEN = (0, 200, 0)
GOLD = (255, 215, 0)
DARK_RED = (180, 0, 0)

# Шрифты
font_small = pygame.font.SysFont('arial', 16)
font_medium = pygame.font.SysFont('arial', 24)
font_large = pygame.font.SysFont('arial', 32)
font_title = pygame.font.SysFont('arial', 48, bold=True)

# Создаем экран
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Шахматы")
clock = pygame.time.Clock()

# Загрузка изображений фигур из файлов
def load_pieces_from_files():
    pieces = {}
    try:
        # Создаем папку для фигур, если её нет
        if not os.path.exists('pieces'):
            os.makedirs('pieces')
            print("Создана папка 'pieces'. Пожалуйста, поместите туда файлы фигур:")
            print("wK.png, wQ.png, wR.png, wB.png, wN.png, wP.png (белые)")
            print("bK.png, bQ.png, bR.png, bB.png, bN.png, bP.png (черные)")
        
        # Белые фигуры
        pieces['white_king'] = pygame.transform.scale(pygame.image.load('_internal/pieces/wK.png'), (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
        pieces['white_queen'] = pygame.transform.scale(pygame.image.load('_internal/pieces/wQ.png'), (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
        pieces['white_rook'] = pygame.transform.scale(pygame.image.load('_internal/pieces/wR.png'), (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
        pieces['white_bishop'] = pygame.transform.scale(pygame.image.load('_internal/pieces/wB.png'), (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
        pieces['white_knight'] = pygame.transform.scale(pygame.image.load('_internal/pieces/wN.png'), (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
        pieces['white_pawn'] = pygame.transform.scale(pygame.image.load('_internal/pieces/wP.png'), (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
        
        # Черные фигуры
        pieces['black_king'] = pygame.transform.scale(pygame.image.load('_internal/pieces/bK.png'), (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
        pieces['black_queen'] = pygame.transform.scale(pygame.image.load('_internal/pieces/bQ.png'), (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
        pieces['black_rook'] = pygame.transform.scale(pygame.image.load('_internal/pieces/bR.png'), (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
        pieces['black_bishop'] = pygame.transform.scale(pygame.image.load('_internal/pieces/bB.png'), (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
        pieces['black_knight'] = pygame.transform.scale(pygame.image.load('_internal/pieces/bN.png'), (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
        pieces['black_pawn'] = pygame.transform.scale(pygame.image.load('_internal/pieces/bP.png'), (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
        
        print("Фигуры успешно загружены из файлов")
    except Exception as e:
        print(f"Ошибка загрузки изображений: {e}")
        print("Создаем фигуры программно...")
        pieces = create_fallback_pieces()
    
    return pieces

# Создание фигур программно (запасной вариант)
def create_fallback_pieces():
    pieces = {}
    for color in ['white', 'black']:
        for piece in ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']:
            surf = pygame.Surface((SQUARE_SIZE - 10, SQUARE_SIZE - 10), pygame.SRCALPHA)
            
            if color == 'white':
                fill_color = WHITE
                outline_color = BLACK
            else:
                fill_color = (50, 50, 50)
                outline_color = (20, 20, 20)
            
            # Рисуем основу фигуры
            pygame.draw.circle(surf, fill_color, ((SQUARE_SIZE-10)//2, (SQUARE_SIZE-10)//2), (SQUARE_SIZE-10)//2 - 5)
            pygame.draw.circle(surf, outline_color, ((SQUARE_SIZE-10)//2, (SQUARE_SIZE-10)//2), (SQUARE_SIZE-10)//2 - 5, 2)
            
            # Добавляем букву для обозначения фигуры
            piece_letters = {
                'king': 'K', 'queen': 'Q', 'rook': 'R', 
                'bishop': 'B', 'knight': 'N', 'pawn': 'P'
            }
            
            font = pygame.font.SysFont('arial', (SQUARE_SIZE-10)//2)
            text = font.render(piece_letters[piece], True, outline_color)
            text_rect = text.get_rect(center=((SQUARE_SIZE-10)//2, (SQUARE_SIZE-10)//2))
            surf.blit(text, text_rect)
            
            pieces[f"{color}_{piece}"] = surf
    
    return pieces

# Класс для управления игрой
class ChessGame:
    def __init__(self, mode="friend", difficulty="easy", timer_enabled=False):
        self.board = [
            ['black_rook', 'black_knight', 'black_bishop', 'black_queen', 'black_king', 'black_bishop', 'black_knight', 'black_rook'],
            ['black_pawn'] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            ['white_pawn'] * 8,
            ['white_rook', 'white_knight', 'white_bishop', 'white_queen', 'white_king', 'white_bishop', 'white_knight', 'white_rook']
        ]
        self.current_player = 'white'
        self.selected_piece = None
        self.valid_moves = []
        self.mode = mode  # 'friend' или 'bot'
        self.difficulty = difficulty
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.animation = None
        self.timer_enabled = timer_enabled
        self.white_time = 600  # 10 минут в секундах
        self.black_time = 600
        self.last_time_update = time.time()
        self.pieces = load_pieces_from_files()
        self.check_position = None  # Позиция короля под шахом
    
    def get_piece(self, row, col):
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def find_king(self, color):
        """Находит позицию короля указанного цвета"""
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece == f"{color}_king":
                    return (row, col)
        return None
    
    def is_square_attacked(self, row, col, attacker_color):
        """Проверяет, атакована ли клетка фигурами указанного цвета"""
        # Проверяем атаки пешками
        direction = 1 if attacker_color == 'white' else -1
        for dc in [-1, 1]:
            r, c = row - direction, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.get_piece(r, c)
                if piece and piece.startswith(attacker_color) and piece.endswith('pawn'):
                    return True
        
        # Проверяем атаки конями
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.get_piece(r, c)
                if piece and piece.startswith(attacker_color) and piece.endswith('knight'):
                    return True
        
        # Проверяем атаки по прямым линиям (ладьи, ферзи)
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for i in range(1, 8):
                r, c = row + i*dr, col + i*dc
                if not (0 <= r < 8 and 0 <= c < 8):
                    break
                piece = self.get_piece(r, c)
                if piece:
                    if piece.startswith(attacker_color) and (piece.endswith('rook') or piece.endswith('queen')):
                        return True
                    break
        
        # Проверяем атаки по диагоналям (слоны, ферзи)
        for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            for i in range(1, 8):
                r, c = row + i*dr, col + i*dc
                if not (0 <= r < 8 and 0 <= c < 8):
                    break
                piece = self.get_piece(r, c)
                if piece:
                    if piece.startswith(attacker_color) and (piece.endswith('bishop') or piece.endswith('queen')):
                        return True
                    break
        
        # Проверяем атаки королем
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    piece = self.get_piece(r, c)
                    if piece and piece.startswith(attacker_color) and piece.endswith('king'):
                        return True
        
        return False
    
    def is_in_check(self, color):
        """Проверяет, находится ли король указанного цвета под шахом"""
        king_pos = self.find_king(color)
        if not king_pos:
            return False
        attacker_color = 'black' if color == 'white' else 'white'
        return self.is_square_attacked(king_pos[0], king_pos[1], attacker_color)
    
    def is_checkmate(self, color):
        """Проверяет, является ли позиция матом для указанного цвета"""
        # Если король не под шахом, это не мат
        if not self.is_in_check(color):
            return False
        
        # Проверяем, есть ли хоть один ход, который убирает шах
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.startswith(color):
                    # Получаем все возможные ходы для этой фигуры
                    moves = self.calculate_valid_moves(row, col)
                    for move_row, move_col in moves:
                        # Пробуем сделать ход
                        original_piece = self.get_piece(move_row, move_col)
                        self.board[move_row][move_col] = piece
                        self.board[row][col] = None
                        
                        # Проверяем, ушел ли король из-под шаха
                        still_in_check = self.is_in_check(color)
                        
                        # Возвращаем доску в исходное состояние
                        self.board[row][col] = piece
                        self.board[move_row][move_col] = original_piece
                        
                        # Если нашелся ход, убирающий шах, это не мат
                        if not still_in_check:
                            return False
        
        # Если ни один ход не убирает шах, это мат
        return True
    
    def is_stalemate(self, color):
        """Проверяет, является ли позиция патом для указанного цвета"""
        # Если король под шахом, это не пат
        if self.is_in_check(color):
            return False
        
        # Проверяем, есть ли хоть один возможный ход
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.startswith(color):
                    moves = self.calculate_valid_moves(row, col)
                    if moves:
                        return False
        
        # Если нет возможных ходов и король не под шахом, это пат
        return True
    
    def select_piece(self, row, col):
        piece = self.get_piece(row, col)
        if piece and piece.startswith(self.current_player):
            self.selected_piece = (row, col)
            self.valid_moves = self.calculate_valid_moves(row, col)
            return True
        return False
    
    def calculate_valid_moves(self, row, col):
        moves = []
        piece = self.get_piece(row, col)
        if not piece:
            return moves
        
        piece_type = piece.split('_')[1]
        
        # Пешка
        if piece_type == 'pawn':
            direction = -1 if self.current_player == 'white' else 1
            # Ход вперед
            if self.get_piece(row + direction, col) is None:
                moves.append((row + direction, col))
                # Двойной ход с начальной позиции
                if (self.current_player == 'white' and row == 6) or (self.current_player == 'black' and row == 1):
                    if self.get_piece(row + 2*direction, col) is None:
                        moves.append((row + 2*direction, col))
            # Взятие по диагонали
            for dc in [-1, 1]:
                r, c = row + direction, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    target = self.get_piece(r, c)
                    if target and not target.startswith(self.current_player):
                        moves.append((r, c))
        
        # Ладья
        elif piece_type == 'rook':
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                for i in range(1, 8):
                    r, c = row + i*dr, col + i*dc
                    if not (0 <= r < 8 and 0 <= c < 8):
                        break
                    target = self.get_piece(r, c)
                    if target is None:
                        moves.append((r, c))
                    elif not target.startswith(self.current_player):
                        moves.append((r, c))
                        break
                    else:
                        break
        
        # Конь
        elif piece_type == 'knight':
            for dr, dc in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    target = self.get_piece(r, c)
                    if target is None or not target.startswith(self.current_player):
                        moves.append((r, c))
        
        # Слон
        elif piece_type == 'bishop':
            for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                for i in range(1, 8):
                    r, c = row + i*dr, col + i*dc
                    if not (0 <= r < 8 and 0 <= c < 8):
                        break
                    target = self.get_piece(r, c)
                    if target is None:
                        moves.append((r, c))
                    elif not target.startswith(self.current_player):
                        moves.append((r, c))
                        break
                    else:
                        break
        
        # Ферзь
        elif piece_type == 'queen':
            # Комбинация ладьи и слона
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                for i in range(1, 8):
                    r, c = row + i*dr, col + i*dc
                    if not (0 <= r < 8 and 0 <= c < 8):
                        break
                    target = self.get_piece(r, c)
                    if target is None:
                        moves.append((r, c))
                    elif not target.startswith(self.current_player):
                        moves.append((r, c))
                        break
                    else:
                        break
        
        # Король
        elif piece_type == 'king':
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    r, c = row + dr, col + dc
                    if 0 <= r < 8 and 0 <= c < 8:
                        target = self.get_piece(r, c)
                        if target is None or not target.startswith(self.current_player):
                            # Проверяем, не будет ли король под шахом после хода
                            original_piece = self.get_piece(r, c)
                            self.board[r][c] = piece
                            self.board[row][col] = None
                            
                            # Если король не под шахом, добавляем ход
                            if not self.is_in_check(self.current_player):
                                moves.append((r, c))
                            
                            # Возвращаем доску в исходное состояние
                            self.board[row][col] = piece
                            self.board[r][c] = original_piece
        
        # Фильтруем ходы, которые оставляют короля под шахом
        valid_moves = []
        for move_row, move_col in moves:
            # Сохраняем исходное состояние
            original_piece = self.get_piece(move_row, move_col)
            self.board[move_row][move_col] = piece
            self.board[row][col] = None
            
            # Проверяем, не остался ли король под шахом
            if not self.is_in_check(self.current_player):
                valid_moves.append((move_row, move_col))
            
            # Возвращаем доску в исходное состояние
            self.board[row][col] = piece
            self.board[move_row][move_col] = original_piece
        
        return valid_moves
    
    def move_piece(self, from_row, from_col, to_row, to_col):
        piece = self.get_piece(from_row, from_col)
        if not piece or (to_row, to_col) not in self.valid_moves:
            return False
        
        # Запись хода в историю
        captured_piece = self.get_piece(to_row, to_col)
        move_info = {
            'piece': piece,
            'from': (from_row, from_col),
            'to': (to_row, to_col),
            'captured': captured_piece,
            'player': self.current_player,
            'time': datetime.now().strftime("%H:%M:%S")
        }
        self.move_history.append(move_info)
        
        # Анимация перемещения
        self.animation = {
            'piece': piece,
            'from_pos': (from_col * SQUARE_SIZE + 40, from_row * SQUARE_SIZE + 60),
            'to_pos': (to_col * SQUARE_SIZE + 40, to_row * SQUARE_SIZE + 60),
            'start_time': time.time(),
            'duration': 0.3  # секунды
        }
        
        # Фактическое перемещение фигуры
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # Проверка на шах и мат
        opponent = 'black' if self.current_player == 'white' else 'white'
        
        # Сначала сбрасываем состояние шаха
        self.check_position = None
        
        # Проверяем, находится ли противник под шахом
        if self.is_in_check(opponent):
            self.check_position = self.find_king(opponent)
        
        # Проверяем мат
        if self.is_checkmate(opponent):
            self.game_over = True
            self.winner = self.current_player
        # Проверяем пат
        elif self.is_stalemate(opponent):
            self.game_over = True
            self.winner = None  # Ничья
        
        # Смена игрока
        self.current_player = opponent
        self.selected_piece = None
        self.valid_moves = []
        
        # Если игра с ботом и сейчас ход бота
        if self.mode == 'bot' and self.current_player == 'black' and not self.game_over:
            self.bot_move()
        
        return True
    
    def bot_move(self):
        # Простой ИИ: случайный ход из доступных
        time.sleep(0.5)  # Задержка для реалистичности
        
        # Находим все фигуры бота
        bot_pieces = []
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.startswith('black'):
                    bot_pieces.append((row, col))
        
        if not bot_pieces:
            return
        
        # Пытаемся сделать ход
        for _ in range(100):  # Максимум 100 попыток
            row, col = random.choice(bot_pieces)
            if self.select_piece(row, col) and self.valid_moves:
                to_row, to_col = random.choice(self.valid_moves)
                self.move_piece(row, col, to_row, to_col)
                break
    
    def update_timer(self):
        if not self.timer_enabled or self.game_over:
            return
            
        current_time = time.time()
        elapsed = current_time - self.last_time_update
        self.last_time_update = current_time
        
        if self.current_player == 'white':
            self.white_time -= elapsed
            if self.white_time <= 0:
                self.white_time = 0
                self.game_over = True
                self.winner = 'black'
        else:
            self.black_time -= elapsed
            if self.black_time <= 0:
                self.black_time = 0
                self.game_over = True
                self.winner = 'white'
    
    def draw(self, screen):
        # Рисуем доску
        for row in range(8):
            for col in range(8):
                color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
                pygame.draw.rect(screen, color, (40 + col * SQUARE_SIZE, 60 + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                
                # Добавляем координаты для удобства
                if row == 7:
                    coord_text = font_small.render(chr(97 + col), True, BLACK if color == LIGHT_BROWN else WHITE)
                    screen.blit(coord_text, (40 + col * SQUARE_SIZE + SQUARE_SIZE - 15, 60 + row * SQUARE_SIZE + SQUARE_SIZE - 15))
                if col == 0:
                    coord_text = font_small.render(str(8 - row), True, BLACK if color == LIGHT_BROWN else WHITE)
                    screen.blit(coord_text, (40 + col * SQUARE_SIZE + 5, 60 + row * SQUARE_SIZE + 5))
        
        # Подсвечиваем клетку под шахом (используем Surface с альфа-каналом)
        if self.check_position:
            row, col = self.check_position
            highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            highlight_surface.fill((255, 0, 0, 100))  # Красный с прозрачностью
            screen.blit(highlight_surface, (40 + col * SQUARE_SIZE, 60 + row * SQUARE_SIZE))
        
        # Подсвечиваем возможные ходы
        if self.selected_piece:
            row, col = self.selected_piece
            highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            highlight_surface.fill((100, 249, 83, 150))  # Зеленый с прозрачностью
            screen.blit(highlight_surface, (40 + col * SQUARE_SIZE, 60 + row * SQUARE_SIZE))
            
            for move_row, move_col in self.valid_moves:
                highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                highlight_surface.fill((249, 166, 83, 150))  # Оранжевый с прозрачностью
                screen.blit(highlight_surface, (40 + move_col * SQUARE_SIZE, 60 + move_row * SQUARE_SIZE))
        
        # Рисуем фигуры
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and (not self.animation or self.animation['piece'] != piece or (row, col) != self.selected_piece):
                    piece_surface = self.pieces[piece]
                    screen.blit(piece_surface, (40 + col * SQUARE_SIZE + 5, 60 + row * SQUARE_SIZE + 5))
        
        # Рисуем анимацию
        if self.animation:
            current_time = time.time()
            elapsed = current_time - self.animation['start_time']
            progress = min(elapsed / self.animation['duration'], 1.0)
            
            if progress < 1.0:
                # Интерполяция позиции
                x = self.animation['from_pos'][0] + (self.animation['to_pos'][0] - self.animation['from_pos'][0]) * progress
                y = self.animation['from_pos'][1] + (self.animation['to_pos'][1] - self.animation['from_pos'][1]) * progress
                screen.blit(self.pieces[self.animation['piece']], (x + 5, y + 5))
            else:
                self.animation = None
        
        # Рисуем таймеры (если включены)
        if self.timer_enabled:
            white_time_str = f"{int(self.white_time // 60):02d}:{int(self.white_time % 60):02d}"
            black_time_str = f"{int(self.black_time // 60):02d}:{int(self.black_time % 60):02d}"
            
            # Используем контрастные цвета для лучшей видимости
            white_time_color = DARK_RED if self.white_time < 60 else BLACK
            black_time_color = DARK_RED if self.black_time < 60 else BLACK
            
            white_time_text = font_medium.render(white_time_str, True, white_time_color)
            black_time_text = font_medium.render(black_time_str, True, black_time_color)
            
            # Фон для таймеров для лучшей читаемости
            pygame.draw.rect(screen, LIGHT_BROWN, (35, 15, 80, 30))
            pygame.draw.rect(screen, LIGHT_BROWN, (35, 535, 80, 30))
            
            screen.blit(white_time_text, (40, 20))
            screen.blit(black_time_text, (40, 540))
        
        # Рисуем историю ходов
        history_bg = pygame.Surface((250, 480), pygame.SRCALPHA)
        history_bg.fill((255, 255, 255, 200))
        screen.blit(history_bg, (530, 60))
        
        history_title = font_medium.render("История ходов:", True, BLACK)
        screen.blit(history_title, (540, 70))
        
        # Показываем последние 10 ходов
        start_idx = max(0, len(self.move_history) - 10)
        for i, move in enumerate(self.move_history[start_idx:]):
            piece_name = move['piece'].split('_')[1]
            piece_names = {
                'pawn': 'П', 'rook': 'Л', 'knight': 'К',
                'bishop': 'С', 'queen': 'Ф', 'king': 'Кр'
            }
            move_text = f"{i+1+start_idx}. {piece_names.get(piece_name, piece_name)} {chr(97+move['from'][1])}{8-move['from'][0]}→{chr(97+move['to'][1])}{8-move['to'][0]}"
            if move['captured']:
                move_text += " ×"
            move_surface = font_small.render(move_text, True, BLACK)
            screen.blit(move_surface, (540, 110 + i * 25))
        
        # Если игра окончена, показываем результат
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            if self.winner:
                winner_text = font_large.render(f"Мат! Победили {'белые' if self.winner == 'white' else 'черные'}", True, WHITE)
            else:
                winner_text = font_large.render("Пат! Ничья", True, WHITE)
            
            screen.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, HEIGHT//2 - 50))
            
            restart_text = font_medium.render("Нажмите ESC для возврата в меню", True, WHITE)
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))
        
        # Показываем предупреждение о шаге только если есть текущий шах
        if self.check_position and not self.game_over:
            # Создаем фон для лучшей видимости текста
            text_bg = pygame.Surface((100, 40), pygame.SRCALPHA)
            text_bg.fill((255, 255, 255, 200))
            screen.blit(text_bg, (WIDTH//2 - 50, 15))
            
            check_text = font_medium.render("ШАХ!", True, RED)
            screen.blit(check_text, (WIDTH//2 - check_text.get_width()//2, 20))

# Остальной код остается без изменений...
# [Остальная часть кода без изменений - классы MainMenu, AboutScreen, AchievementsScreen, HistoryScreen и функция main]

# Класс для главного меню
class MainMenu:
    def __init__(self):
        self.buttons = [
            {"text": "Играть с другом", "rect": pygame.Rect(300, 200, 200, 50)},
            {"text": "Играть с ботом", "rect": pygame.Rect(300, 270, 200, 50)},
            {"text": "Последние игры", "rect": pygame.Rect(300, 340, 200, 50)},
            {"text": "Достижения", "rect": pygame.Rect(300, 410, 200, 50)},
            {"text": "О игре", "rect": pygame.Rect(300, 480, 200, 50)}
        ]
        self.selected_button = None
        self.difficulty_menu = False
        self.timer_menu = False
        self.game_mode = None
        self.difficulty_buttons = [
            {"text": "Легкий", "rect": pygame.Rect(300, 200, 200, 50)},
            {"text": "Средний", "rect": pygame.Rect(300, 270, 200, 50)},
            {"text": "Сложный", "rect": pygame.Rect(300, 340, 200, 50)},
            {"text": "Назад", "rect": pygame.Rect(300, 410, 200, 50)}
        ]
        self.timer_buttons = [
            {"text": "С таймером", "rect": pygame.Rect(300, 200, 200, 50)},
            {"text": "Без таймера", "rect": pygame.Rect(300, 270, 200, 50)},
            {"text": "Назад", "rect": pygame.Rect(300, 340, 200, 50)}
        ]
    
    def draw(self, screen):
        # Фон
        screen.fill(LIGHT_BROWN)
        
        # Заголовок с тенью
        title = font_title.render("Шахматы", True, DARK_BROWN)
        title_shadow = font_title.render("Шахматы", True, (100, 70, 50))
        screen.blit(title_shadow, (WIDTH//2 - title.get_width()//2 + 3, 83))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        
        # Декоративные фигуры по бокам
        piece_size = 40
        try:
            white_king = pygame.transform.scale(pygame.image.load('_internal/pieces/wK.png'), (piece_size, piece_size))
            black_king = pygame.transform.scale(pygame.image.load('_internal/pieces/bK.png'), (piece_size, piece_size))
            screen.blit(white_king, (200, 90))
            screen.blit(black_king, (560, 90))
        except:
            # Если файлы не найдены, просто пропускаем
            pass
        
        if not self.difficulty_menu and not self.timer_menu:
            # Кнопки главного меню
            for button in self.buttons:
                color = BLUE if button["rect"].collidepoint(pygame.mouse.get_pos()) else DARK_BROWN
                pygame.draw.rect(screen, color, button["rect"], border_radius=10)
                pygame.draw.rect(screen, BLACK, button["rect"], 2, border_radius=10)
                
                text = font_medium.render(button["text"], True, WHITE)
                screen.blit(text, (button["rect"].centerx - text.get_width()//2, 
                                  button["rect"].centery - text.get_height()//2))
        
        elif self.difficulty_menu:
            # Меню выбора сложности
            difficulty_title = font_large.render("Выберите сложность", True, DARK_BROWN)
            screen.blit(difficulty_title, (WIDTH//2 - difficulty_title.get_width()//2, 150))
            
            for button in self.difficulty_buttons:
                color = BLUE if button["rect"].collidepoint(pygame.mouse.get_pos()) else DARK_BROWN
                pygame.draw.rect(screen, color, button["rect"], border_radius=10)
                pygame.draw.rect(screen, BLACK, button["rect"], 2, border_radius=10)
                
                text = font_medium.render(button["text"], True, WHITE)
                screen.blit(text, (button["rect"].centerx - text.get_width()//2, 
                                  button["rect"].centery - text.get_height()//2))
        
        elif self.timer_menu:
            # Меню выбора таймера
            timer_title = font_large.render("Таймер", True, DARK_BROWN)
            screen.blit(timer_title, (WIDTH//2 - timer_title.get_width()//2, 150))
            
            for button in self.timer_buttons:
                color = BLUE if button["rect"].collidepoint(pygame.mouse.get_pos()) else DARK_BROWN
                pygame.draw.rect(screen, color, button["rect"], border_radius=10)
                pygame.draw.rect(screen, BLACK, button["rect"], 2, border_radius=10)
                
                text = font_medium.render(button["text"], True, WHITE)
                screen.blit(text, (button["rect"].centerx - text.get_width()//2, 
                                  button["rect"].centery - text.get_height()//2))
    
    def handle_click(self, pos):
        if not self.difficulty_menu and not self.timer_menu:
            for i, button in enumerate(self.buttons):
                if button["rect"].collidepoint(pos):
                    if i == 0:  # Игра с другом
                        self.game_mode = "friend"
                        self.timer_menu = True
                        return None
                    elif i == 1:  # Игра с ботом
                        self.game_mode = "bot"
                        self.difficulty_menu = True
                        return None
                    elif i == 2:  # Последние игры
                        return "history", None, None
                    elif i == 3:  # Достижения
                        return "achievements", None, None
                    elif i == 4:  # О игре
                        return "about", None, None
        
        elif self.difficulty_menu:
            for i, button in enumerate(self.difficulty_buttons):
                if button["rect"].collidepoint(pos):
                    if i == 0:  # Легкий
                        self.difficulty_menu = False
                        self.timer_menu = True
                        return None
                    elif i == 1:  # Средний
                        self.difficulty_menu = False
                        self.timer_menu = True
                        return None
                    elif i == 2:  # Сложный
                        self.difficulty_menu = False
                        self.timer_menu = True
                        return None
                    elif i == 3:  # Назад
                        self.difficulty_menu = False
                        return None
        
        elif self.timer_menu:
            for i, button in enumerate(self.timer_buttons):
                if button["rect"].collidepoint(pos):
                    if i == 0:  # С таймером
                        self.timer_menu = False
                        if self.game_mode == "friend":
                            return "game", "friend", True
                        else:
                            return "game", "medium", True  # По умолчанию средняя сложность для бота
                    elif i == 1:  # Без таймера
                        self.timer_menu = False
                        if self.game_mode == "friend":
                            return "game", "friend", False
                        else:
                            return "game", "medium", False  # По умолчанию средняя сложность для бота
                    elif i == 2:  # Назад
                        self.timer_menu = False
                        return None
        
        return None

# Класс для экрана "О игре"
class AboutScreen:
    def __init__(self):
        self.back_button = pygame.Rect(50, 500, 100, 40)
    
    def draw(self, screen):
        screen.fill(LIGHT_BROWN)
        
        title = font_large.render("О игре", True, DARK_BROWN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Информация об игре
        lines = [
            "Соцсети автора:",
            "GitHub - Ivan2812446",
            "TG - python_by_vanya",
            "Kwork - Sergeev_Ivan",
            "",
            "Функции:",
            "- Игра против бота/друга",
            "- Игра с таймером или без",
            "- Просмотр достижений",
            "- Просмотр последних игр",
            "",
            "Управление:",
            "- ЛКМ: выбор и перемещение фигур",
            "- ESC: возврат в меню",
            "",
            "Обозначения фигур в истории ходов:",
            "П - Пешка, Л - Ладья, К - Конь",
            "С - Слон, Ф - Ферзь, Кр - Король"
        ]
        
        for i, line in enumerate(lines):
            text = font_small.render(line, True, BLACK)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 120 + i * 25))
        
        # Кнопка назад
        pygame.draw.rect(screen, DARK_BROWN, self.back_button, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.back_button, 2, border_radius=5)
        back_text = font_medium.render("Назад", True, WHITE)
        screen.blit(back_text, (self.back_button.centerx - back_text.get_width()//2, 
                               self.back_button.centery - back_text.get_height()//2))
    
    def handle_click(self, pos):
        if self.back_button.collidepoint(pos):
            return "menu"
        return None

# Класс для экрана достижений
class AchievementsScreen:
    def __init__(self):
        self.back_button = pygame.Rect(50, 500, 100, 40)
        # Загрузка достижений из файла
        self.achievements = self.load_achievements()
    
    def load_achievements(self):
        try:
            with open('achievements.json', 'r') as f:
                return json.load(f)
        except:
            # Стандартные достижения
            return {
                "games_played": 0,
                "games_won": 0,
                "games_lost": 0,
                "games_vs_bot": 0,
                "wins_vs_bot": 0,
                "achievements": {
                    "first_game": False,
                    "first_win": False,
                    "10_games": False,
                    "10_wins": False,
                    "bot_beater": False,
                    "checkmate": False
                }
            }
    
    def save_achievements(self):
        with open('achievements.json', 'w') as f:
            json.dump(self.achievements, f)
    
    def draw(self, screen):
        screen.fill(LIGHT_BROWN)
        
        title = font_large.render("Достижения", True, DARK_BROWN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Статистика
        stats_title = font_medium.render("Статистика", True, BLACK)
        screen.blit(stats_title, (100, 120))
        
        win_percentage = (self.achievements["games_won"] / self.achievements["games_played"] * 100) if self.achievements["games_played"] > 0 else 0
        bot_win_percentage = (self.achievements["wins_vs_bot"] / self.achievements["games_vs_bot"] * 100) if self.achievements["games_vs_bot"] > 0 else 0
        
        stats = [
            f"Сыграно партий: {self.achievements['games_played']}",
            f"Побед: {self.achievements['games_won']} ({win_percentage:.1f}%)",
            f"Поражений: {self.achievements['games_lost']}",
            f"Партий с ботом: {self.achievements['games_vs_bot']}",
            f"Побед над ботом: {self.achievements['wins_vs_bot']} ({bot_win_percentage:.1f}%)"
        ]
        
        for i, stat in enumerate(stats):
            text = font_small.render(stat, True, BLACK)
            screen.blit(text, (100, 160 + i * 30))
        
        # Достижения
        achievements_title = font_medium.render("Достижения", True, BLACK)
        screen.blit(achievements_title, (450, 120))
        
        achievements = [
            ("Первая игра", self.achievements["achievements"]["first_game"]),
            ("Первая победа", self.achievements["achievements"]["first_win"]),
            ("10 сыгранных партий", self.achievements["achievements"]["10_games"]),
            ("10 побед", self.achievements["achievements"]["10_wins"]),
            ("Победа над ботом", self.achievements["achievements"]["bot_beater"]),
            ("Поставить мат", self.achievements["achievements"]["checkmate"])
        ]
        
        for i, (achievement, unlocked) in enumerate(achievements):
            color = GREEN if unlocked else GRAY
            text = font_small.render(achievement, True, color)
            screen.blit(text, (450, 160 + i * 30))
            
            status = "Разблокировано" if unlocked else "Заблокировано"
            status_text = font_small.render(status, True, color)
            screen.blit(status_text, (650, 160 + i * 30))
        
        # Кнопка назад
        pygame.draw.rect(screen, DARK_BROWN, self.back_button, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.back_button, 2, border_radius=5)
        back_text = font_medium.render("Назад", True, WHITE)
        screen.blit(back_text, (self.back_button.centerx - back_text.get_width()//2, 
                               self.back_button.centery - back_text.get_height()//2))
    
    def handle_click(self, pos):
        if self.back_button.collidepoint(pos):
            return "menu"
        return None

# Класс для экрана истории игр
class HistoryScreen:
    def __init__(self):
        self.back_button = pygame.Rect(50, 500, 100, 40)
        self.games = self.load_games()
    
    def load_games(self):
        try:
            with open('games_history.json', 'r') as f:
                return json.load(f)
        except:
            return []
    
    def draw(self, screen):
        screen.fill(LIGHT_BROWN)
        
        title = font_large.render("История игр", True, DARK_BROWN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        if not self.games:
            no_games = font_medium.render("Пока нет сохраненных игр", True, BLACK)
            screen.blit(no_games, (WIDTH//2 - no_games.get_width()//2, 200))
        else:
            # Показываем последние 5 игр
            recent_games = self.games[-5:]
            for i, game in enumerate(reversed(recent_games)):
                game_text = f"Игра {len(self.games) - i}: {game['result']} ({game['date']})"
                text = font_small.render(game_text, True, BLACK)
                screen.blit(text, (100, 120 + i * 40))
        
        # Кнопка назад
        pygame.draw.rect(screen, DARK_BROWN, self.back_button, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.back_button, 2, border_radius=5)
        back_text = font_medium.render("Назад", True, WHITE)
        screen.blit(back_text, (self.back_button.centerx - back_text.get_width()//2, 
                               self.back_button.centery - back_text.get_height()//2))
    
    def handle_click(self, pos):
        if self.back_button.collidepoint(pos):
            return "menu"
        return None

# Основная функция игры
def main():
    menu = MainMenu()
    about_screen = AboutScreen()
    achievements_screen = AchievementsScreen()
    history_screen = HistoryScreen()
    
    current_screen = "menu"
    game = None
    game_mode = None
    timer_enabled = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_screen == "game":
                        # Сохраняем игру при выходе
                        if game and game.move_history:
                            result = "Не завершена"
                            if game.game_over:
                                if game.winner:
                                    result = f"Мат - победили {'белые' if game.winner == 'white' else 'черные'}"
                                else:
                                    result = "Пат - ничья"
                            
                            history_screen.games.append({
                                "result": result,
                                "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
                                "moves": game.move_history
                            })
                            with open('games_history.json', 'w') as f:
                                json.dump(history_screen.games, f)
                        
                        # Обновляем достижения
                        if game_mode and game_mode != "friend":
                            achievements_screen.achievements["games_vs_bot"] += 1
                            if game.winner == "white":  # Игрок победил
                                achievements_screen.achievements["wins_vs_bot"] += 1
                                achievements_screen.achievements["achievements"]["bot_beater"] = True
                        
                        if game.winner == "white":  # Игрок поставил мат
                            achievements_screen.achievements["achievements"]["checkmate"] = True
                        
                        achievements_screen.save_achievements()
                        current_screen = "menu"
                        game = None
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                if current_screen == "menu":
                    result = menu.handle_click(pos)
                    if result:
                        if result[0] == "game":
                            current_screen = "game"
                            game_mode = result[1]
                            timer_enabled = result[2]
                            if result[1] == "friend":
                                game = ChessGame("friend", timer_enabled=timer_enabled)
                            else:
                                game = ChessGame("bot", result[1], timer_enabled)
                            
                            # Обновляем достижения
                            achievements_screen.achievements["games_played"] += 1
                            if achievements_screen.achievements["games_played"] == 1:
                                achievements_screen.achievements["achievements"]["first_game"] = True
                            if achievements_screen.achievements["games_played"] >= 10:
                                achievements_screen.achievements["achievements"]["10_games"] = True
                            
                            if game_mode != "friend":
                                achievements_screen.achievements["games_vs_bot"] += 1
                        
                        elif result[0] == "history":
                            current_screen = "history"
                            history_screen.games = history_screen.load_games()
                        
                        elif result[0] == "achievements":
                            current_screen = "achievements"
                        
                        elif result[0] == "about":
                            current_screen = "about"
                
                elif current_screen == "game" and game and not game.animation:
                    # Обрабатываем клик в игре
                    x, y = pos
                    if 40 <= x <= 40 + BOARD_SIZE and 60 <= y <= 60 + BOARD_SIZE:
                        col = (x - 40) // SQUARE_SIZE
                        row = (y - 60) // SQUARE_SIZE
                        
                        if game.selected_piece:
                            # Пытаемся сделать ход
                            if game.move_piece(game.selected_piece[0], game.selected_piece[1], row, col):
                                # Обновляем достижения при победе
                                if game.game_over and game.winner == "white":
                                    achievements_screen.achievements["games_won"] += 1
                                    if achievements_screen.achievements["games_won"] == 1:
                                        achievements_screen.achievements["achievements"]["first_win"] = True
                                    if achievements_screen.achievements["games_won"] >= 10:
                                        achievements_screen.achievements["achievements"]["10_wins"] = True
                                elif game.game_over:
                                    achievements_screen.achievements["games_lost"] += 1
                            else:
                                # Выбираем другую фигуру
                                game.select_piece(row, col)
                        else:
                            # Выбираем фигуру
                            game.select_piece(row, col)
                
                elif current_screen == "about":
                    result = about_screen.handle_click(pos)
                    if result == "menu":
                        current_screen = "menu"
                
                elif current_screen == "achievements":
                    result = achievements_screen.handle_click(pos)
                    if result == "menu":
                        current_screen = "menu"
                
                elif current_screen == "history":
                    result = history_screen.handle_click(pos)
                    if result == "menu":
                        current_screen = "menu"
        
        # Отрисовка текущего экрана
        if current_screen == "menu":
            menu.draw(screen)
        elif current_screen == "game" and game:
            game.update_timer()
            game.draw(screen)
        elif current_screen == "about":
            about_screen.draw(screen)
        elif current_screen == "achievements":
            achievements_screen.draw(screen)
        elif current_screen == "history":
            history_screen.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    # Сохраняем достижения при выходе
    achievements_screen.save_achievements()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()