# ATTRIBUTIONS:
# Pygame (python library) used for handling graphics
# Stockfish (chess engine) used for determining computer chess moves
# python-chess (python library) used for managing chess board data, legal moves, etc.
# Wikimedia (chess piece images)
# itch.io user IvoryRed (playing card images)

import pygame, time, random, sys, chess, chess.engine
pygame.init()

WIDTH = 1200
HEIGHT = 1300

screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Final Project")
clock = pygame.time.Clock()

HALF = WIDTH / 2

all_sprites = pygame.sprite.LayeredUpdates()
game_sprites = pygame.sprite.Group()
buttons = pygame.sprite.Group()

engine = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
engine.configure({"Skill Level": 0})

piece_image = pygame.image.load("final_project/800px-Chess_Pieces_Sprite.svg.png")
WID = 3 / 4 * HALF
piece_image = pygame.transform.smoothscale(piece_image, (WID, WID / 3))

card_image = pygame.image.load("final_project/playingcardimages.png")
scalar = 1.25
card_image = pygame.transform.scale(card_image, (1888 * scalar, 770 * scalar))

class Timer(pygame.sprite.Sprite):
  def __init__(self, x, y, total_time, fatal=1, game=None):
      self._layer = 4
      self.groups = all_sprites
      pygame.sprite.Sprite.__init__(self, self.groups)
      self.image = pygame.Surface([HALF, 15])
      self.image.fill((100, 0, 0))
      self.rect = self.image.get_rect()
      self.x, self.y = x, y
      self.rect.x = x
      self.rect.y = y
      self.total_time = total_time
      self.fatal = fatal
      self.game = game
      self.stime = time.monotonic()

  def update(self):
        if not self.game.proj.in_game:
            return
        self.image.fill((250, 250, 250))
        current = time.monotonic()
        # if current < self.stime:
        #     self.stime = current
        rectwidth = HALF - ((current - self.stime) / self.total_time) * HALF
        if rectwidth <= 0:
            self.kill()
            self.game.kill()
            if isinstance(self.game, Blackjack):
                game = self.game
                for card in game.player + game.dealer:
                    card.kill()
                if game.winner == 2:
                    return
                if game.winner == 0:
                    game.winner = -1
                units = game.winner if game.bet <= 15 else game.winner * 5
                self.game.proj.gen_points(game.x, game.y, game.bet * game.winner, units)
            return
        pygame.draw.rect(self.image, (100, 0, 0), pygame.Rect(0, 0, rectwidth, 15))

class TimerAdder(pygame.sprite.Sprite):
    def __init__(self, x, y, amount, col, delay, proj):
        self.groups = all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface([40, 40], pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        write("+" + str(amount) if amount > 0 else amount, (20, 20), col, 40, self.image)
        self.rect = self.image.get_rect()
        self.x, self.y = x, y
        self.rect.centerx = x
        self.rect.centery = y
        self.updates = 75
        self.dx = (HALF - x) / self.updates
        self.dy = (50 - y) / self.updates
        self.alpha = 255
        self.amount = amount
        self.delay = delay * 10
        self.image.set_alpha(0)
        self.proj = proj
    def update(self):
        global start_time
        if self.delay > 0:
            self.delay -= 1
            return
        self.image.set_alpha(255)
        if self.updates > 0:
            self.updates -= 1
            self.x += self.dx
            self.y += self.dy
            self.rect.centerx, self.rect.centery = self.x, self.y
        else:
            if self.alpha == 255:
                self.proj.start_time += self.amount
            self.alpha -= 25
            if self.alpha > 0:
                self.image.set_alpha(self.alpha)
            else:
                self.kill()

class Game(pygame.sprite.Sprite):
  def __init__(self, x, y, proj):
    self.groups = all_sprites, game_sprites
    pygame.sprite.Sprite.__init__(self, self.groups)
    self.image = pygame.Surface((HALF, HALF))
    self.rect = self.image.get_rect()
    self.x, self.y = x, y
    self.rect.x = x
    self.rect.y = y
    self.image.fill((180, 180, 180))
    self.selected = None
    self.tilesize = HALF / 8
    self.proj = proj

class Card(pygame.sprite.Sprite):
    def __init__(self, x, y, number, hidden, order):
        self.groups = all_sprites
        self._layer = 1
        if hidden:
            self._layer = 0
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.wid = 12 * 10
        self.height = 16 * 10
        self.image = pygame.Surface([self.wid, self.height])
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - self.wid / 2
        self.num = number
        self.val = min(self.num, 10)
        self.hidden = hidden
        self.alpha = 255
        if not hidden:
            self.paint()
        self.order = order
        self.rearr(2)
    def rearr(self, total):
        xdist = (total - 1) * 60 + 120
        self.rect.x = (HALF - xdist) / 2 + self.order * 60
    def paint(self):
        self.image.blit(card_image, (0, 0), ((self.num - 1) * self.wid, random.randint(0, 3) * self.height, self.wid, self.height))


class BlackjackIntro(Game):
    def __init__(self, px, py, proj):
        Game.__init__(self, px, py, proj)
        self.image.fill((0, 50, 0))
        pygame.draw.rect(self.image, (0, 120, 0), pygame.Rect(10, 10, HALF - 20, HALF - 20), border_radius=15)
        elapsed = time.monotonic() - proj.start_time
        if elapsed >= 40:
            self.bets = [[10, 20], [30, 60]]
        elif elapsed >= 30:
            self.bets = [[5, 15], [20, 30]]
        else:
            self.bets = [[5, 15], [15, 20]]
        margin = 100
        for y in range(2):
            for x in range(2):
                xc = (HALF - margin) * (x / 2 + 0.25) + margin / 2
                yc = (HALF - margin) * (y / 2 + 0.25) + margin / 2
                pygame.draw.rect(self.image, (0, 110, 0), pygame.Rect(xc - 100, yc - 100, 200, 200))
                write(self.bets[y][x], (xc, yc), (0, 0, 0), 60, self.image)
        self.timer = Timer(px, py + HALF - 15, 8, 0, self)
    def respond(self, mx, my):
        Blackjack(self.x, self.y, self.bets[int(my // (HALF / 2))][int(mx // (HALF / 2))], self.proj)
        self.kill()
        self.timer.kill()

class NumberGuesser(Game):
    def __init__(self, x, y, proj):
        Game.__init__(self, x, y, proj)
        self.number = random.randint(1, 100)
        self.typed = ""
        self.paint()
        self.timer = Timer(x, y + HALF - 15, 30, 0, self)
    def paint(self):
        self.image.fill((170, 150, 0))
        pygame.draw.rect(self.image, (220, 200, 150), pygame.Rect(10, 10, HALF - 20, HALF - 20), border_radius=15)
        write(self.typed, (HALF / 2, HALF / 2), (0, 0, 0), 50, self.image)
        if self.typed != "":
            typed = int(self.typed)
            if typed < self.number:
                text = "HIGHER"
                col = (0, 200, 0)
            elif typed > self.number:
                text = "LOWER"
                col = (200, 0, 0)
            else:
                self.kill()
                self.timer.kill()
                self.proj.gen_points(self.x, self.y, random.randint(10, 18), 1)
                return
            write(text, (HALF / 2, HALF * 3 / 4), col, 50, self.image)
        else:
            write("Guess a number 1 - 100", (HALF / 2, HALF * 1 / 4), (0, 0, 0), 50, self.image)
    def response(self, ev):
        if ev.key == pygame.K_BACKSPACE:
            if self.typed != "":
                self.typed = self.typed[:-1]
        elif len(self.typed) < 3:
            self.typed += ev.unicode
        self.paint()

class Blackjack(Game):
    def __init__(self, x, y, bet, proj):
        Game.__init__(self, x, y, proj)
        print(bet)
        pygame.draw.rect(self.image, (0, 100, 0), pygame.Rect(10, 10, HALF - 20, HALF - 20), border_radius=15)
        self.dealer = [Card(0, y + 100, random.randint(1, 13), 0, 1), Card(0, y + 100, random.randint(1, 13), 1, 0)]
        self.player = [Card(0, y + 450, random.randint(1, 13), 0, 0), Card(0, y + 450, random.randint(1, 13), 0, 1)]
        self.revealedTime = None
        self.bet = bet
        self.playertotal = self.best_total(self.player)
        self.dealertotal = ""
        self.timer = Timer(x, y + HALF - 15, 20, 0, self)
        self.winner = 0
        self.paint()
    def paint(self):
        self.image.fill((0, 50, 0))
        pygame.draw.rect(self.image, (0, 100, 0), pygame.Rect(10, 10, HALF - 20, HALF - 20), border_radius=15)
        write(self.playertotal, (HALF / 2, HALF / 2 + 50), (0, 50, 0) if self.winner != -1 else (50, 0, 0), 50, self.image)
        write(self.dealertotal, (HALF / 2, HALF / 2 - 50), (0, 50, 0) if self.winner != 1 else (50, 0, 0), 50, self.image)
    def response(self, resp):
        if self.winner != 0:
            return
        if resp in "h ":
            self.player.append(Card(0, self.y + 450, random.randint(1, 13), 0, len(self.player)))
            for card in self.player:
                card.rearr(len(self.player))
            playertotal = self.best_total(self.player)
            self.playertotal = playertotal
            if playertotal > 21:
                self.winner = -1
                self.dealertotal = self.best_total(self.dealer)
                
                self.timer.stime = time.monotonic() - (20 - 2)
                self.dealer[1].paint()
            self.paint()
        elif resp == "s":
            hidden = self.dealer[1]
            self.dealertotal = self.best_total(self.dealer)
            if self.revealedTime is None:
                hidden.paint()
                self.revealedTime = time.monotonic()
            self.paint()
    def best_total(self, hand):
        total = 0
        ace = 0
        for card in hand:
            total += card.val
            if card.val == 1:
                ace = 1
        if ace and total <= 11:
            total += 10
        return total
    def update(self):
        if self.revealedTime is not None:
            if time.monotonic() - self.revealedTime >= 1:
                self.revealedTime = time.monotonic()
                # dealer_total = self.best_total(self.dealer)
                self.paint()
                if self.dealertotal < 16:
                    self.dealer.append(Card(0, self.y + 100, random.randint(1, 13), 0, len(self.dealer)))
                    for card in self.dealer:
                        card.rearr(len(self.dealer))
                    self.dealertotal = self.best_total(self.dealer)
                    self.paint()
                else:
                    self.revealedTime = None
                    self.timer.stime = time.monotonic() - (20 - 2)
                    # self.dealertotal = self.playertotal
                    if self.dealertotal < self.playertotal or self.dealertotal > 21:
                        self.winner = 1
                    elif self.dealertotal == self.playertotal:
                        self.winner = 2
                    else:
                        self.winner = -1
                    self.paint()
                    
class Button(pygame.sprite.Sprite):
    def __init__(self, cx, cy, wid, height, txt, proc, col, altcol, proj):
        self.groups = all_sprites, buttons
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface([wid, height])
        self.rect = self.image.get_rect()
        self.wid = wid
        self.height = height
        self.txt = txt
        self.col = col
        self.rect.x = cx - wid / 2
        self.rect.y = cy - height / 2
        self.proc = proc
        self.proj = proj
        self.altcol = altcol
    def respond(self, mx, my):
        if self.hovering(mx, my):
            self.proc()
    def hovering(self, mx, my):
        return self.rect.x < mx < self.rect.right and self.rect.y < my < self.rect.bottom
    def update(self):
        mx, my = pygame.mouse.get_pos()
        self.paint(self.col if not self.hovering(mx, my) else self.altcol)
    def paint(self, col):
        self.image.fill((18, 18, 18))
        pygame.draw.rect(self.image, col, pygame.Rect(5, 5, self.wid - 10, self.height - 10), border_radius=15)
        pygame.draw.rect(self.image, (18, 18, 18), pygame.Rect(10, 10, self.wid - 20, self.height - 20), border_radius=10)
        write(self.txt, (self.wid / 2, self.height / 2), col, 65, self.image)

class Chess(Game):
    def __init__(self, x, y, proj):
        Game.__init__(self, x, y, proj)
        self.board = chess.Board()
        diff = self.proj.diff
        match diff:
            case 1:
                # engine.configure({"Skill Level": 0})
                self.board.remove_piece_at(chess.D8)
            case 2:
                # engine.configure({"Skill Level": 5})
                self.board.set_piece_at(chess.D8, chess.Piece(chess.ROOK, chess.BLACK))
            case 3:
                engine.configure({"Skill Level": 5})
        self.paint()

    def paint(self):
        for y in range(8):
            for x in range(8):
                rx = x * WIDTH / 16
                ry = y * WIDTH / 16
                tileid = (7 - y) * 8 + x
                piece = self.board.piece_at(tileid)
                if self.selected == tileid:
                    col = (255, 255, 0)
                elif piece is not None and piece.piece_type == chess.KING and piece.color == self.board.turn and self.board.is_check():
                    col = (255, 150, 150)
                else:
                    col = [(235, 236, 208), (115, 149, 82)][(x + y) % 2]
                draw_circle = 0
                for mv in self.board.legal_moves:
                    if mv.from_square == self.selected and mv.to_square == tileid:
                        draw_circle = 1
                print(x, y)
                pygame.draw.rect(self.image, col, pygame.Rect(rx, ry, WIDTH / 16, WIDTH / 16))
                if piece is not None:
                    piece = piece.symbol()
                    color = piece == piece.upper()
                    factor = WIDTH / 16
                    self.image.blit(piece_image, (rx, ry), ("KQBNRP".index(piece.upper()) * factor, (1 - color) * factor, factor, factor))
                if draw_circle:
                    pygame.draw.circle(self.image, (200, 200, 200), (rx + HALF / 16, ry + HALF / 16), 7)

    def respond(self, mx, my):
        if not self.proj.in_game:
            return
        if self.selected is None:
            self.selected = int((7 - my // self.tilesize) * 8 + mx // self.tilesize)
            self.paint()
        else:
            new = int((7 - my // self.tilesize) * 8 + mx // self.tilesize)
            if self.selected == new:
                self.selected = None
            else:
                piece = self.board.piece_at(new)
                if piece is not None and piece.color:
                    self.selected = new
                else:
                    if new >= 56 and self.board.piece_at(self.selected).piece_type == chess.PAWN:
                        move = chess.Move(self.selected, new, promotion=chess.QUEEN)
                    else:
                        move = chess.Move(self.selected, new)
                    if move in self.board.legal_moves:
                        self.board.push(move)
                        if self.board.is_checkmate():
                            self.selected = None
                            self.paint()
                            self.proj.end_game(1)
                            return
                        self.board.push(engine.play(self.board, chess.engine.Limit(time=0.001)).move)
                    self.selected = None
                    if self.board.is_checkmate():
                        self.proj.end_game()
            self.paint()

class Fade(pygame.sprite.Sprite):
    def __init__(self, winning, proj):
        self.groups = all_sprites
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface([WIDTH, WIDTH + 100])
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.alpha = 0
        self.phase = 0
        self.image.fill((0, 0, 0))
        self.image.set_alpha(0)
        self.winning = winning
        self.proj = proj
    def update(self):
        self.proj.in_game = 0
        if self.phase == 0:
            self.alpha += 1
            if self.alpha >= 255:
                self.phase = 1
                self.proj.mode = self.winning + 2
                for spr in all_sprites:
                    if not isinstance(spr, Fade):
                        spr.kill()
        else:
            self.alpha -= 3
            if self.alpha <= 0:
                self.kill()
        self.image.set_alpha(self.alpha)

class MathGame(Game):
  def __init__(self, x, y, proj):
      Game.__init__(self, x, y, proj)
      self.answer = None
      self.mathtimer = Timer(x, y + HALF - 15, 5, 0, self)
      self.paint()

  def paint(self):
      if self.answer is None:
          self.a = random.randint(100, 1000)
          self.b = random.randint(100, 1000)
          self.answer = self.a + self.b
          self.question = f"{self.a} + {self.b}?"
          self.options = [self.answer]
          for _ in range(2):
              newopt = self.answer
              while newopt in self.options:
                  newopt = self.answer + random.randint(-20, 20)
              self.options.append(newopt)
          random.shuffle(self.options)
      self.image.fill((0, 100, 150))
      pygame.draw.rect(self.image, (0, 150, 170), pygame.Rect(10, 10, HALF - 20, HALF - 20), border_radius=15)
      write(self.question, (HALF / 2, 125 / 400 * HALF), (0, 0, 0), 60, self.image)
      for i, opt in enumerate(self.options):
          write(f"{'ABC'[i]}) {opt}", (HALF / 2, 200 / 400 * HALF + i * WIDTH / 16), (0, 0, 0), 60, self.image)

  def response(self, resp):
      global score, gamemode, start_time
      if self.options["abc".index(resp)] == self.answer:
          self.proj.gen_points(self.x, self.y, random.randint(3, 6), 1)
      else:
          self.proj.gen_points(self.x, self.y, -5, -1)
      self.kill()
      self.mathtimer.kill()

class FinalProject:
    def __init__(self):
        self.start_time = None
        self.running = True
        self.in_game = 0
        self.mode = 0
        self.diff = 1
        self.ctrls = [
            "ABC - Answer (Math Questions)",
            "SPACE / H - Hit (Blackjack)",
            "ENTER / S - Stand (Blackjack)",
            "0-9 - Type (Number Guessing)",
            "SHIFT + R - Reset To Title"
        ]

    def run(self):
        self.title_screen()
        while self.running:
            # print(all_sprites)
            # print(time.monotonic())
            # print(time.monotonic())
            current = time.monotonic()
            if self.in_game:
                if self.nextmath < current:
                    self.nextmath = current + 10
                    MathGame(HALF, 100, self)
                if self.nextbj < current:
                    self.nextbj = current + 35
                    BlackjackIntro(0, HALF + 100, self)
                if self.nextnum < current:
                    self.nextnum = current + 40
                    NumberGuesser(HALF, HALF + 100, self)
                if round(60 - time.monotonic() + self.start_time) < 0:
                    self.end_game()
            self.draw_board()
            all_sprites.update()
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.unicode != "":
                        if event.unicode in "abc":
                            for spr in game_sprites:
                                if isinstance(spr, MathGame):
                                    spr.response(event.unicode)
                                    break
                        elif event.unicode in "sh ":
                            for spr in game_sprites:
                                if isinstance(spr, Blackjack):
                                    spr.response(event.unicode)
                                    break
                        elif event.unicode == "R":
                            self.title_screen()
                        elif event.unicode in "0123456789" or event.key == pygame.K_BACKSPACE:
                            for spr in game_sprites:
                                if isinstance(spr, NumberGuesser):
                                    spr.response(event)
                                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if self.mode == 0:
                        for button in buttons:
                            button.respond(mx, my)
                    elif self.mode == 4:
                        self.title_screen()
                    elif self.mode in (2, 3) and not all_sprites:
                        self.title_screen()
                    else:
                        if mx < self.chess_game.rect.right and 100 < my < self.chess_game.rect.bottom + 100:
                            self.chess_game.respond(mx, my - 100)
                        else:
                            for spr in game_sprites:
                                if isinstance(spr, BlackjackIntro):
                                    if spr.rect.x < mx < spr.rect.right and spr.rect.y < my < spr.rect.bottom:
                                        spr.respond(mx - spr.rect.x, my - spr.rect.y)
                                        break
            clock.tick(60)

    def start_game(self):
        self.chess_game = Chess(0, 100, self)
        self.start_time = time.monotonic()
        self.nextmath = time.monotonic() + 5
        self.nextbj = time.monotonic() + 10
        self.nextnum = time.monotonic() + 15
        self.mode = 1
        self.in_game = 1
        for button in buttons:
            button.kill()

    def draw_board(self):
        screen.fill((70, 70, 70))
        if self.mode == 0:
            screen.fill((18, 18, 18))
            write("Beat the Bot", (HALF, HALF / 2 - 100), (250, 250, 250), 100, screen)
            write("Aadi Thakkar & Donaven Wang", (HALF, WIDTH + 20), (250, 250, 250), 60, screen)
        elif self.mode == 1:
            pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(0, 0, WIDTH, 100))
            time_left = round(60 - time.monotonic() + self.start_time)
            col = (255, 255, 255)
            if time_left <= 10:
                col = (200, 0, 0)
            write(max(time_left, 0), (HALF, 50), col, 60, screen)
        elif self.mode == 2:
            screen.fill((18, 18, 18))
            write("GAME OVER", (HALF, HALF + 50), (255, 255, 255), 100, screen)
        elif self.mode == 3:
            screen.fill((18, 18, 18))
            write("YOU WIN", (HALF, HALF + 50), (255, 255, 255), 100, screen)
        elif self.mode == 4:
            screen.fill((18, 18, 18))
            amountOfControls = len(self.ctrls)
            gap = HEIGHT / (amountOfControls + 1)
            for i in range(amountOfControls):
                write(self.ctrls[i], (HALF, i * gap + gap), (255, 255, 255), 70, screen)
        all_sprites.draw(screen)

    def end_game(proj, winning=0):
        Fade(winning, proj)

    def gen_points(self, x, y, total, units):
        amount = int(total / units)
        for i in range(amount):
            TimerAdder(x + HALF / 2, y + HALF / 2, units, (0, 200, 0) if units > 0 else (200, 0, 0), i, self)
    
    def controls(self):
        for spr in all_sprites:
            spr.kill()
        self.mode = 4

    def title_screen(self):
        self.mode = 0
        self.in_game = 0
        for spr in all_sprites:
            spr.kill()
        Button(HALF, HALF - 70, 420, 144, "PLAY", self.start_game, (0, 120, 170), (0, 180, 200), self)
        Button(HALF, HALF + 100, 420, 144, "CONTROLS", self.controls, (0, 120, 0), (0, 170, 0), self)
        self.diff_button = Button(HALF, HALF + 270, 420, 144, f"DIFFICULTY: {self.diff}", self.modify_difficulty, (150, 120, 0), (200, 180, 0), self)

    def modify_difficulty(self):
        self.diff = (self.diff) % 3 + 1
        self.diff_button.txt = f"DIFFICULTY: {self.diff}"

def write(txt, pos, col, size, surf):
    font = pygame.font.Font(None, size)
    textimg = font.render(str(txt), True, col)
    isize = textimg.get_size()
    surf.blit(textimg, (pos[0]-isize[0]/2, pos[1]-isize[1]/2))

def main():
    FinalProject().run()

try:
    main()
finally:
    engine.quit()
