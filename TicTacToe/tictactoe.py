import copy
import sys
import pygame
import pickle
import random
import numpy as np



# --- PIXELS ---

WIDTH = 700
HEIGHT = 700

ROWS = 3
COLS = 3
SQSIZE = WIDTH // COLS

LINE_WIDTH = 15
CIRC_WIDTH = 15
CROSS_WIDTH = 20

RADIUS = SQSIZE // 4

OFFSET = 50

# --- COLORS ---

BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRC_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)


# Khởi tạo Pygame và mixer
pygame.init()
pygame.mixer.init()

# Load nhạc nền
pygame.mixer.music.load("sounds/background_music.mp3")

# Chơi nhạc nền lặp lại
pygame.mixer.music.play(-1)




screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
pygame.display.set_caption('TIC TAC TOE AI')
screen.fill( BG_COLOR )

class Board:
    """
    Lớp Board đại diện cho bảng trò chơi trong trò chơi Cờ caro.

    
    """
    def __init__(self):
        """
        Khởi tạo một bàn cờ mới.

        Attributes:
            squares (ndarray): Mảng 2D đại diện cho bàn cờ.
            empty_sqrs (ndarray): Mảng 2D đại diện cho các ô trống trên bàn cờ.
            marked_sqrs (int): Số lượng ô đã được đánh dấu.
        """
        self.squares = np.zeros( (ROWS, COLS) )
        self.empty_sqrs = self.squares 
        self.marked_sqrs = 0

    def final_state(self, show=False):
        '''
        Kiểm tra trạng thái kết thúc của trò chơi.

        Args:
            show (bool): True nếu muốn hiển thị dấu hiệu chiến thắng trên màn hình.

        Returns:
            int: 0 nếu chưa có người chiến thắng, 1 nếu người chơi 1 chiến thắng, 2 nếu người chơi 2 chiến thắng.
        '''

        # Kiểm tra chiến thắng theo chiều dọc
        for col in range(COLS):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] != 0:
                if show:
                    color = CIRC_COLOR if self.squares[0][col] == 2 else CROSS_COLOR
                    iPos = (col * SQSIZE + SQSIZE // 2, 20)
                    fPos = (col * SQSIZE + SQSIZE // 2, HEIGHT - 20)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[0][col]

        # Kiểm tra chiến thắng theo chiều ngang
        for row in range(ROWS):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] != 0:
                if show:
                    color = CIRC_COLOR if self.squares[row][0] == 2 else CROSS_COLOR
                    iPos = (20, row * SQSIZE + SQSIZE // 2)
                    fPos = (WIDTH - 20, row * SQSIZE + SQSIZE // 2)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[row][0]

        # Kiểm tra chiến thắng theo đường chéo xuống
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            if show:
                color = CIRC_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, 20)
                fPos = (WIDTH - 20, HEIGHT - 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return self.squares[1][1]

        # Kiểm tra chiến thắng theo đường chéo lên
        if self.squares[2][0] == self.squares[1][1] == self.squares[0][2] != 0:
            if show:
                color = CIRC_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, HEIGHT - 20)
                fPos = (WIDTH - 20, 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return self.squares[1][1]

        # Không có người chiến thắng
        return 0

    def mark_sqr(self, row, col, player):
        """Đánh dấu một ô trên bàn cờ bằng biểu tượng của người chơi.

        Args:
            row (int): Vị trí hàng của ô.
            col (int): Vị trí cột của ô.
            player (int): Người chơi đánh dấu ô (1 hoặc 2).
        """
        self.squares[row][col] = player
        self.marked_sqrs += 1

    def empty_sqr(self, row, col):
        """Kiểm tra xem một ô có trống không.

        Args:
            row (int): Vị trí hàng của ô.
            col (int): Vị trí cột của ô.

        Returns:
            bool: True nếu ô trống, False nếu không trống.
        """
        return self.squares[row][col] == 0

    def get_empty_sqrs(self):
        """Trả về danh sách các ô trống trên bàn cờ.

        Returns:
            list: Danh sách các ô trống dưới dạng cặp (row, col).
        """
        empty_sqrs = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.empty_sqr(row, col):
                    empty_sqrs.append( (row, col) )
        
        return empty_sqrs

    def isfull(self):
        """Kiểm tra xem bàn cờ đã đầy chưa.

        Returns:
            bool: True nếu bàn cờ đã đầy, False nếu còn trống.
        """
        return self.marked_sqrs == 9

    def isempty(self):
        """Kiểm tra xem bàn cờ có trống không.

        Returns:
            bool: True nếu bàn cờ trống, False nếu đã có ít nhất một ô được đánh dấu.
        """
        return self.marked_sqrs == 0

class AI:
    """
    Lớp AI đại diện cho trí tuệ nhân tạo trong trò chơi.

    Attributes:
        level (int): Cấp độ của trí tuệ nhân tạo.
        player (int): Số người chơi mà AI đại diện (mặc định là 2).
    """
    def __init__(self, level=1, player=2):

        self.level = level
        self.player = player

    # --- RANDOM ---
    def rnd(self, board):
        """Chọn một ô trống ngẫu nhiên trên bàn cờ.

        Args:
            board (Board): Bàn cờ hiện tại.

        Returns:
            tuple: Cặp (row, col) đại diện cho vị trí ô được chọn.
        """
        empty_sqrs = board.get_empty_sqrs()
        idx = random.randrange(0, len(empty_sqrs))
        return empty_sqrs[idx] # (row, col)

    # --- MINIMAX ---
    def minimax(self, board, maximizing):
        """Thuật toán Minimax để đánh giá tốt nhất cho một nước đi.

        Args:
            board (Board): Bàn cờ hiện tại.
            maximizing (bool): True nếu đang tối đa hóa giá trị, False nếu đang tối thiểu hóa.

        Returns:
            tuple: Cặp (eval, move), trong đó eval là giá trị đánh giá của nước đi, move là ô được chọn (row, col).
        """
        # Trường hợp cơ sở
        case = board.final_state()

        # Người chơi 1 chiến thắng
        if case == 1:
            
            return 1, None # eval, move

        # Người chơi 2 chiến thắng
        if case == 2:
            
            return -1, None

        # Hòa
        elif board.isfull():
            
            return 0, None

        if maximizing:
            max_eval = -100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, 1)
                eval = self.minimax(temp_board, False)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)

            return max_eval, best_move

        elif not maximizing:
            min_eval = 100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.player)
                eval = self.minimax(temp_board, True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)

            return min_eval, best_move

    # --- MAIN EVAL ---
    def eval(self, main_board):
        """Đánh giá và chọn nước đi tốt nhất dựa trên mức độ của AI.

        Args:
            main_board (Board): Bàn cờ hiện tại.

        Returns:
            tuple: Cặp (row, col) đại diện cho ô được chọn để đánh dấu.
        """
        if self.level == 0:
            # Lựa chọn ngẫu nhiên
            eval = 'random'
            move = self.rnd(main_board)
        else:
            # Lựa chọn thông qua thuật toán Minimax
            eval, move = self.minimax(main_board, False)

        print(f'AI đã chọn ô để đánh dấu tại vị trí {move} với đánh giá: {eval}')

        return move # row, col

# Tạo danh sách các file âm thanh
sound_files = {
    "click": "sounds/click.wav",  # Thay đổi tên file nếu cần
    "win": "sounds/win.wav",
    "lose": "sounds/lose.wav"
}

# Load các âm thanh
sounds = {}
for name, file in sound_files.items():
    sounds[name] = pygame.mixer.Sound(file)

class Game:
    """
    Lớp Game đại diện cho trò chơi tic-tac-toe.

    Attributes:
        board (Board): Bảng trò chơi.
        ai (AI): Trí tuệ nhân tạo trong trò chơi.
        player (int): Số người chơi hiện tại.
        gamemode (str): Chế độ chơi ('ai' hoặc 'pvp').
        running (bool): Trạng thái của trò chơi (True nếu đang chạy).
    """
    def __init__(self,n):
        """Khởi tạo một trò chơi mới.

        Args:
            n (int): Cấp độ của trí tuệ nhân tạo (AI).
        """
        self.board = Board()
        self.ai = AI(n)
        self.player = 1   #1-cross  #2-circles
        self.gamemode = 'ai' # pvp or ai
        self.running = True
        self.show_lines()

    # --- DRAW METHODS ---
    def __init__(self, n, mode='ai'):

        self.board = Board()
        self.ai = AI(n)
        self.player = 1
        self.gamemode = mode  # 'ai' hoặc 'pvp' (player vs player)
        self.running = True
        self.show_lines()
    def show_lines(self):
        """Vẽ các đường kẻ trên màn hình."""
        # Nền
        screen.fill( BG_COLOR )

        # Dọc
        pygame.draw.line(screen, LINE_COLOR, (SQSIZE, 0), (SQSIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (WIDTH - SQSIZE, 0), (WIDTH - SQSIZE, HEIGHT), LINE_WIDTH)

        # Ngang
        pygame.draw.line(screen, LINE_COLOR, (0, SQSIZE), (WIDTH, SQSIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (0, HEIGHT - SQSIZE), (WIDTH, HEIGHT - SQSIZE), LINE_WIDTH)

    def draw_fig(self, row, col):
        """Vẽ biểu tượng (X hoặc O) trên màn hình.

        Args:
            row (int): Vị trí hàng của ô.
            col (int): Vị trí cột của ô.
        """
        player = self.board.squares[row][col]
        if player == 1:
            # Vẽ X
            start_desc = (col * SQSIZE + OFFSET, row * SQSIZE + OFFSET)
            end_desc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_desc, end_desc, CROSS_WIDTH)

            start_asc = (col * SQSIZE + OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            end_asc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_asc, end_asc, CROSS_WIDTH)

        elif player == 2:
            # Vẽ O
            center = (col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2)
            pygame.draw.circle(screen, CIRC_COLOR, center, RADIUS, CIRC_WIDTH)

    # --- OTHER METHODS ---
    def make_move(self, row, col):
        """Đánh dấu ô được chọn và thực hiện nước đi.

        Args:
            row (int): Vị trí hàng của ô.
            col (int): Vị trí cột của ô.
        """
        self.board.mark_sqr(row, col, self.player)
        self.draw_fig(row, col)
        sounds["click"].play()  # Phát âm thanh click
        self.next_turn()

    def next_turn(self):
        """Chuyển lượt chơi cho người chơi tiếp theo."""
        self.player = self.player % 2 + 1

    def change_gamemode(self):
        """Thay đổi chế độ chơi (PvP hoặc AI)."""
        self.gamemode = 'ai' if self.gamemode == 'pvp' else 'pvp'

    def isover(self):
        """Kiểm tra xem trò chơi đã kết thúc chưa.

        Returns:
            bool: True nếu trò chơi đã kết thúc, False nếu chưa.
        """
        result = self.board.final_state(show=True)
        if result != 0:  # Kiểm tra nếu có người chiến thắng
            if result == self.player:
                sounds["win"].play()  # Phát âm thanh thắng
            else:
                sounds["lose"].play()  # Phát âm thanh thua
        return result != 0 or self.board.isfull()  # Trả về True nếu game kết thúc

    def reset(self):
        """Đặt lại trạng thái ban đầu của trò chơi."""
        self.__init__()

    def save_game(self):
        """Lưu trạng thái hiện tại của trò chơi."""
        data = {
            "board": self.board.squares.tolist(),  # Chuyển mảng thành danh sách để serialize
            "player": self.player,
            "gamemode": self.gamemode,
            "ai_level": self.ai.level
        }
        try:
            with open("savegame.dat", "wb") as f:
                pickle.dump(data, f)
            print("Trò chơi đã được lưu!")
        except Exception as e:
            print(f"Lỗi khi lưu trò chơi: {e}")

    def load_game(self):
        """Tải trạng thái trò chơi đã lưu trước đó."""
        try:
            with open("savegame.dat", "rb") as f:
                data = pickle.load(f)
        except FileNotFoundError:
            print("Không tìm thấy tệp lưu trữ.")
            return
        except Exception as e:
            print(f"Lỗi khi tải trò chơi: {e}")
            return

        self.board.squares = np.array(data["board"])
        self.player = data["player"]
        self.gamemode = data["gamemode"]
        self.ai.level = data["ai_level"]

        # Vẽ lại bàn cờ với các nước đã đi
        self.show_lines()
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.squares[row][col] != 0:
                    self.draw_fig(row, col)  # Vẽ lại dấu X/O dựa trên giá trị hiện tại của ô

        print("Trò chơi đã được tải!")

def main(mode='ai'):

    game = Game(n, mode)
    board = game.board
    ai = game.ai

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                row = pos[1] // SQSIZE
                col = pos[0] // SQSIZE

                if board.empty_sqr(row, col) and game.running:
                    game.make_move(row, col)
                    if game.isover():
                        game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.reset()
                    game.running = True
                if event.key == pygame.K_g:
                    game.change_gamemode()
                if event.key == pygame.K_s:
                    game.save_game()
                if event.key == pygame.K_l:
                    game.load_game()

        if game.gamemode == 'ai' and game.player == ai.player and game.running:
            pygame.display.update()
            row, col = ai.eval(board)
            game.make_move(row, col)
            if game.isover():
                game.running = False

        pygame.display.update()

if __name__ == '__main__':
    print("------------- HUONG DAN -------------")
    print("    Muon luu game nhan phim S")
    print("    Muon choi lai van cu: Chon che do choi bat kì roi nhan phim L")
    print("    Muon thoat game nhan phim R")
    print("------------- PYGAME SETUP -------------")
   
    print("    Nhap 'ai' de choi voi AI")
    print("    Nhap 'pvp' de choi voi nguoi choi khac")
    mode = input()
    if mode=="pvp":
        n=0
        main(mode)
    else:
        print("    Nhap 0 de choi voi AI level 0")
        print("    Nhap 1 de choi voi AI level 1")
        n = int(input())
    
        main(mode)
