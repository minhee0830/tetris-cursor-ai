import pygame
import random
import time

# 색상 정의 (메인 컬러, 하이라이트, 쉐도우)
COLORS = [
    [(0, 0, 0), (10, 10, 10), (0, 0, 0)],           # 검정
    [(86, 25, 129), (120, 37, 179), (66, 19, 99)],  # 보라
    [(70, 125, 125), (100, 179, 179), (50, 89, 89)],# 청록
    [(149, 84, 255), (179, 102, 255), (119, 67, 204)], # 라벤더
    [(80, 134, 22), (122, 204, 33), (60, 100, 16)], # 초록
    [(180, 34, 22), (255, 48, 31), (135, 25, 16)],  # 빨강
    [(180, 34, 122), (255, 48, 173), (135, 25, 91)] # 분홍
]

# 배경 그라데이션 색상
BACKGROUND_COLOR_TOP = (25, 25, 112)  # 미드나잇 블루
BACKGROUND_COLOR_BOTTOM = (72, 61, 139)  # 슬레이트 블루

# 테트리스 블록 모양 정의
SHAPES = [
    [[1, 5, 9, 13], [4, 5, 6, 7]],  # I
    [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],  # J
    [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],  # L
    [[1, 2, 5, 6]],  # O
    [[6, 7, 9, 10], [1, 5, 6, 10]],  # S
    [[4, 5, 9, 10], [2, 6, 5, 9]],  # Z
    [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]]  # T
]

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.Font(None, 30)
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        # 버튼 그림자
        shadow_rect = self.rect.copy()
        shadow_rect.y += 2
        pygame.draw.rect(surface, (0, 0, 0, 128), shadow_rect, border_radius=10)
        # 메인 버튼
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=10)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Tetris:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.field = []
        self.score = 0
        self.state = "waiting"  # waiting, playing, paused, gameover, timeout
        self.figure = None
        self.x = 0
        self.y = 0
        self.start_time = 0
        self.remaining_time = 30
        self.total_time = 30
        
        self.clear_field()
        
    def clear_field(self):
        self.field = []
        for i in range(self.height):
            new_line = []
            for j in range(self.width):
                new_line.append(0)
            self.field.append(new_line)
            
    def new_figure(self):
        self.figure = Figure(3, 0)
        
    def intersects(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if (i + self.figure.y > self.height - 1 or
                        j + self.figure.x > self.width - 1 or
                        j + self.figure.x < 0 or
                        self.field[i + self.figure.y][j + self.figure.x] > 0):
                        return True
        return False
        
    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.break_lines()
        self.new_figure()
        if self.intersects():
            self.state = "gameover"
            
    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1-1][j]
        self.score += lines ** 2
        
    def go_space(self):
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()
        
    def go_down(self):
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()
            
    def go_side(self, dx):
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x
            
    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation
            
    def reset(self):
        self.clear_field()
        self.score = 0
        self.state = "waiting"
        self.figure = None
        self.remaining_time = self.total_time
        self.start_time = 0
        
    def update_time(self):
        if self.state == "playing":
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            self.remaining_time = max(0, self.total_time - elapsed_time)
            if self.remaining_time == 0:
                self.state = "timeout"

class Figure:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(SHAPES) - 1)
        self.color = random.randint(1, len(COLORS) - 1)
        self.rotation = 0
        
    def image(self):
        return SHAPES[self.type][self.rotation]
    
    def rotate(self):
        self.rotation = (self.rotation + 1) % len(SHAPES[self.type])

# 게임 초기화
pygame.init()

# 상수 정의
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600  # 화면 높이 증가
BLOCK_SIZE = 25     # 블록 크기 증가
FIELD_WIDTH = 10
FIELD_HEIGHT = 20

# 게임 화면 설정
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

# 게임 객체 생성
game = Tetris(FIELD_HEIGHT, FIELD_WIDTH)
clock = pygame.time.Clock()
fps = 25
counter = 0
pressing_down = False

# 게임 필드의 시작 위치 계산 (화면 중앙에 배치)
game.x = (SCREEN_WIDTH - FIELD_WIDTH * BLOCK_SIZE) // 2
game.y = (SCREEN_HEIGHT - FIELD_HEIGHT * BLOCK_SIZE) // 2

# 버튼 생성 (새로운 위치와 스타일)
button_color = (70, 130, 180)  # 스틸 블루
button_hover = (100, 149, 237)  # 콘플라워 블루

start_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 50, "Start", button_color, button_hover)
pause_button = Button(SCREEN_WIDTH - 120, 10, 100, 40, "Pause", button_color, button_hover)
yes_button = Button(SCREEN_WIDTH//2 - 110, SCREEN_HEIGHT//2 + 50, 100, 40, "Yes", button_color, button_hover)
no_button = Button(SCREEN_WIDTH//2 + 10, SCREEN_HEIGHT//2 + 50, 100, 40, "No", button_color, button_hover)
restart_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 100, 200, 50, "Restart", button_color, button_hover)

def draw_gradient_background(surface):
    for y in range(SCREEN_HEIGHT):
        lerp = y / SCREEN_HEIGHT
        color = (
            BACKGROUND_COLOR_TOP[0] + (BACKGROUND_COLOR_BOTTOM[0] - BACKGROUND_COLOR_TOP[0]) * lerp,
            BACKGROUND_COLOR_TOP[1] + (BACKGROUND_COLOR_BOTTOM[1] - BACKGROUND_COLOR_TOP[1]) * lerp,
            BACKGROUND_COLOR_TOP[2] + (BACKGROUND_COLOR_BOTTOM[2] - BACKGROUND_COLOR_TOP[2]) * lerp
        )
        pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))

def draw_block(surface, x, y, color):
    # 메인 블록
    pygame.draw.rect(surface, color[0],
                    [x, y, BLOCK_SIZE, BLOCK_SIZE])
    # 하이라이트 (위, 왼쪽)
    pygame.draw.polygon(surface, color[1],
                       [(x, y), (x + BLOCK_SIZE, y),
                        (x + BLOCK_SIZE - 4, y + 4),
                        (x + 4, y + 4),
                        (x + 4, y + BLOCK_SIZE - 4),
                        (x, y + BLOCK_SIZE)])
    # 쉐도우 (오른쪽, 아래)
    pygame.draw.polygon(surface, color[2],
                       [(x + BLOCK_SIZE, y),
                        (x + BLOCK_SIZE, y + BLOCK_SIZE),
                        (x, y + BLOCK_SIZE),
                        (x + 4, y + BLOCK_SIZE - 4),
                        (x + BLOCK_SIZE - 4, y + BLOCK_SIZE - 4),
                        (x + BLOCK_SIZE - 4, y + 4)])

while True:
    if game.figure is None and game.state == "playing":
        game.new_figure()
    counter += 1
    if counter > 100000:
        counter = 0

    if counter % (fps // 2) == 0 or pressing_down:
        if game.state == "playing":
            game.go_down()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
            
        if event.type == pygame.KEYDOWN:
            if game.state == "playing":
                if event.key == pygame.K_UP:
                    game.rotate()
                if event.key == pygame.K_DOWN:
                    pressing_down = True
                if event.key == pygame.K_LEFT:
                    game.go_side(-1)
                if event.key == pygame.K_RIGHT:
                    game.go_side(1)
                if event.key == pygame.K_SPACE:
                    game.go_space()
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
                
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                pressing_down = False
                
        # 버튼 이벤트 처리
        if start_button.handle_event(event) and game.state == "waiting":
            game.state = "playing"
            game.start_time = time.time()
        elif pause_button.handle_event(event):
            if game.state == "playing":
                game.state = "paused"
            elif game.state == "paused":
                game.state = "playing"
        elif yes_button.handle_event(event) and game.state == "timeout":
            game.total_time += 30
            game.remaining_time = 30
            game.start_time = time.time()
            game.state = "playing"
        elif no_button.handle_event(event) and game.state == "timeout":
            game.state = "gameover"
        elif restart_button.handle_event(event) and game.state == "gameover":
            game.reset()

    # 시간 업데이트
    game.update_time()

    # 배경 그리기
    draw_gradient_background(screen)

    # 게임 필드 그리기
    pygame.draw.rect(screen, (0, 0, 0, 50),
                    [game.x - 4, game.y - 4,
                     FIELD_WIDTH * BLOCK_SIZE + 8,
                     FIELD_HEIGHT * BLOCK_SIZE + 8], border_radius=10)
    
    for i in range(game.height):
        for j in range(game.width):
            if game.field[i][j] > 0:
                draw_block(screen,
                          game.x + j * BLOCK_SIZE,
                          game.y + i * BLOCK_SIZE,
                          COLORS[game.field[i][j]])

    # 현재 블록 그리기
    if game.figure is not None and game.state == "playing":
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in game.figure.image():
                    draw_block(screen,
                             game.x + (j + game.figure.x) * BLOCK_SIZE,
                             game.y + (i + game.figure.y) * BLOCK_SIZE,
                             COLORS[game.figure.color])

    # 버튼 그리기
    if game.state == "waiting":
        start_button.draw(screen)
    elif game.state in ["playing", "paused"]:
        pause_button.draw(screen)
        
    # 점수와 시간 표시
    font = pygame.font.Font(None, 36)
    font1 = pygame.font.Font(None, 72)
    
    # 점수 패널
    score_panel = pygame.Surface((200, 80))
    score_panel.set_alpha(128)
    score_panel.fill((0, 0, 0))
    screen.blit(score_panel, (10, 10))
    
    score_text = font.render(f"Score: {game.score}", True, (255, 255, 255))
    time_text = font.render(f"Time: {int(game.remaining_time)}s", True, (255, 255, 255))
    
    screen.blit(score_text, [20, 20])
    screen.blit(time_text, [20, 50])

    # 게임 상태 메시지 표시
    if game.state == "waiting":
        text = font1.render("TETRIS", True, (255, 255, 255))
        text_shadow = font1.render("TETRIS", True, (0, 0, 0))
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        screen.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
        screen.blit(text, text_rect)
    elif game.state == "paused":
        text = font1.render("PAUSED", True, (255, 255, 255))
        screen.blit(text, [SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//3])
    elif game.state == "timeout":
        text = font1.render("Time's Up!", True, (255, 255, 255))
        screen.blit(text, [SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//3])
        text = font.render("Add 30 seconds?", True, (255, 255, 255))
        screen.blit(text, [SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2])
        yes_button.draw(screen)
        no_button.draw(screen)
    elif game.state == "gameover":
        text = font1.render("Game Over", True, (255, 255, 255))
        screen.blit(text, [SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//3])
        text = font.render(f"Final Score: {game.score}", True, (255, 255, 255))
        screen.blit(text, [SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2])
        restart_button.draw(screen)

    pygame.display.flip()
    clock.tick(fps) 