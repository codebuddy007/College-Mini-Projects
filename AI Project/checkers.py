"""
Neon Checkers — Two Player Only
Author: ChatGPT (GPT-5 Thinking mini)
Controls:
 - Click a piece to select it (must be your color)
 - Click a highlighted square to move
 - U = Undo, R = Restart, Q = Quit
"""

import pygame
import sys
import time
from copy import deepcopy

# ----- Config -----
WIDTH, HEIGHT = 900, 820
BOARD_SIZE = 800
ROWS, COLS = 8, 8
SQ = BOARD_SIZE // COLS
PANEL_H = HEIGHT - BOARD_SIZE

BG = (8, 8, 18)
LIGHT_SQ = (28, 30, 60)
DARK_SQ = (12, 12, 34)
NEON_RED = (255, 60, 100)
NEON_BLUE = (80, 160, 255)
SELECT_GLOW = (0, 255, 160)
MOVE_GLOW = (0, 200, 255)
TEXT = (220, 220, 240)
ACCENT = (0, 255, 200)

FPS = 60
DEFAULT_TIMER = 5 * 60  # not mandatory to use

# ----- Utilities -----
def in_bounds(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS

def clone_board(b):
    return [row[:] for row in b]

# ----- Board Setup -----
def initial_board():
    b = [[0]*COLS for _ in range(ROWS)]
    # We'll use:  1 = Red (bottom),  2 = Red King
    #           -1 = Blue (top), -2 = Blue King
    for r in range(3):
        for c in range(COLS):
            if (r + c) % 2 == 1:
                b[r][c] = -1
    for r in range(5, 8):
        for c in range(COLS):
            if (r + c) % 2 == 1:
                b[r][c] = 1
    return b

# ----- Move Generation -----
def get_piece_moves(board, r, c):
    """
    Return two lists:
      - normal_moves: list of paths (each path is list of coords [(r,c), ...]) for single-step moves
      - capture_moves: list of paths for captures (multi-jump allowed)
    Each path is the list of landing squares in order (for single-step it is length 1).
    """
    piece = board[r][c]
    if piece == 0:
        return [], []

    color = 1 if piece > 0 else -1
    king = abs(piece) == 2

    # direction list
    if king:
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    else:
        directions = [(-1, -1), (-1, 1)] if color == 1 else [(1, -1), (1, 1)]

    normal_moves = []
    capture_moves = []

    # normal (simple) moves
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc) and board[nr][nc] == 0:
            normal_moves.append([(nr, nc)])

    # captures: DFS to find multi-jumps
    def dfs(bd, cr, cc, path, visited):
        found_any = False
        pc = bd[cr][cc]
        scan_dirs = [(-1,-1),(-1,1),(1,-1),(1,1)] if abs(pc)==2 else \
                    ([(-1,-1),(-1,1)] if pc>0 else [(1,-1),(1,1)])
        for dr, dc in scan_dirs:
            mr, mc = cr + dr, cc + dc  # middle
            lr, lc = cr + 2*dr, cc + 2*dc  # landing
            if in_bounds(mr, mc) and in_bounds(lr, lc):
                if bd[mr][mc] != 0 and bd[mr][mc] * pc < 0 and bd[lr][lc] == 0:
                    # perform jump on clone
                    nb = clone_board(bd)
                    nb[lr][lc] = nb[cr][cc]
                    nb[cr][cc] = 0
                    nb[mr][mc] = 0
                    # king if lands on last row
                    if nb[lr][lc] == 1 and lr == 0: nb[lr][lc] = 2
                    if nb[lr][lc] == -1 and lr == ROWS-1: nb[lr][lc] = -2
                    dfs(nb, lr, lc, path + [(lr, lc)], visited | {(mr,mc,lr,lc)})
                    found_any = True
        if not found_any and path:
            # finished sequence
            capture_moves.append(path)

    dfs(board, r, c, [], set())
    return normal_moves, capture_moves

def get_all_moves(board, player):
    """Return moves for player: list of (sr,sc,path) where path is list of landings.
       Enforce forced captures: if any capture exists anywhere, return only captures."""
    captures = []
    normals = []
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] * player > 0:
                nm, cm = get_piece_moves(board, r, c)
                for p in cm:
                    captures.append((r, c, p))
                for p in nm:
                    normals.append((r, c, p))
    return captures if captures else normals

# ----- Apply Move -----
def apply_move(board, move):
    """move = (sr, sc, path), path is list of landing coordinates (one or more)"""
    sr, sc, path = move
    nb = clone_board(board)
    piece = nb[sr][sc]
    nb[sr][sc] = 0
    cr, cc = sr, sc
    for (nr, nc) in path:
        # if jumped
        if abs(nr - cr) == 2 or abs(nc - cc) == 2:
            mr, mc = (nr + cr)//2, (nc + cc)//2
            nb[mr][mc] = 0
        cr, cc = nr, nc
    nb[cr][cc] = piece
    # kinging
    if nb[cr][cc] == 1 and cr == 0: nb[cr][cc] = 2
    if nb[cr][cc] == -1 and cr == ROWS-1: nb[cr][cc] = -2
    return nb

# ----- Terminal / Winner -----
def is_terminal(board):
    red = any(board[r][c] > 0 for r in range(ROWS) for c in range(COLS))
    blue = any(board[r][c] < 0 for r in range(ROWS) for c in range(COLS))
    return not red or not blue

def winner(board):
    red = any(board[r][c] > 0 for r in range(ROWS) for c in range(COLS))
    blue = any(board[r][c] < 0 for r in range(ROWS) for c in range(COLS))
    if red and not blue: return "Red"
    if blue and not red: return "Blue"
    return None

# ----- Drawing helpers -----
def glow_circle(surface, color, pos, radius, intensity=8):
    for i in range(intensity, 0, -1):
        alpha = max(8, int(24 * (i/intensity)))
        s = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
        c = (*color, alpha)
        pygame.draw.circle(s, c, (radius*2, radius*2), radius + i*2)
        surface.blit(s, (pos[0]-radius*2, pos[1]-radius*2))

def draw_board(surface, board, selected=None, moves=None, trails=None):
    # background
    surface.fill(BG)
    # squares
    for r in range(ROWS):
        for c in range(COLS):
            col = LIGHT_SQ if (r+c)%2==0 else DARK_SQ
            pygame.draw.rect(surface, col, (c*SQ, r*SQ, SQ, SQ))
    # move highlights
    if moves:
        for (r,c) in moves:
            s = pygame.Surface((SQ, SQ), pygame.SRCALPHA)
            pygame.draw.rect(s, (*MOVE_GLOW, 90), (0,0,SQ,SQ))
            surface.blit(s, (c*SQ, r*SQ))
    # pieces
    for r in range(ROWS):
        for c in range(COLS):
            v = board[r][c]
            if v != 0:
                color = NEON_RED if v>0 else NEON_BLUE
                center = (c*SQ + SQ//2, r*SQ + SQ//2)
                glow_circle(surface, color, center, SQ//4)
                pygame.draw.circle(surface, color, center, SQ//3)
                if abs(v) == 2:
                    # king symbol
                    font = pygame.font.SysFont(None, 36)
                    txt = font.render("★", True, (255,255,255))
                    surface.blit(txt, (center[0]-12, center[1]-16))
    # selected
    if selected:
        r,c = selected
        s = pygame.Surface((SQ, SQ), pygame.SRCALPHA)
        pygame.draw.rect(s, (*SELECT_GLOW, 160), (0,0,SQ,SQ), 6)
        surface.blit(s, (c*SQ, r*SQ))

def draw_panel(surface, red_score, blue_score, player):
    pygame.draw.rect(surface, (6,6,12), (0, BOARD_SIZE, WIDTH, PANEL_H))
    font_big = pygame.font.SysFont("Arial", 26, bold=True)
    font_sm = pygame.font.SysFont("Arial", 16)
    m_txt = font_sm.render(f"Mode: Human vs Human", True, TEXT)
    surface.blit(m_txt, (16, BOARD_SIZE + 8))
    rt = font_big.render(f"Red (Bottom) Score: {red_score}", True, NEON_RED)
    bt = font_big.render(f"Blue (Top) Score: {blue_score}", True, NEON_BLUE)
    surface.blit(rt, (16, BOARD_SIZE + 36))
    surface.blit(bt, (320, BOARD_SIZE + 36))
    turn_txt = font_big.render(f"Turn: {'Red' if player==1 else 'Blue'}", True, TEXT)
    surface.blit(turn_txt, (16, BOARD_SIZE + 72))
    help_txt = font_sm.render("U = Undo   R = Restart   Q = Quit", True, (180,180,200))
    surface.blit(help_txt, (16, BOARD_SIZE + 104))

# ----- Win popup -----
def show_win_popup(screen, winner_name):
    font_big = pygame.font.SysFont("Arial", 48, bold=True)
    font_sm = pygame.font.SysFont("Arial", 22)
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return "restart"
                if e.key == pygame.K_q:
                    pygame.quit(); sys.exit()
        screen.fill((0,0,0))
        msg = font_big.render(f"{winner_name} Wins!", True, ACCENT)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 80))
        hint = font_sm.render("Press R to Restart or Q to Quit", True, (200,200,200))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 10))
        pygame.display.flip()

# ----- Main -----
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Neon Checkers — Two Player")
    clock = pygame.time.Clock()

    board = initial_board()
    turn = 1  # 1 = Red(bottom), -1 = Blue(top)
    selected = None
    legal_paths_for_selected = []  # list of paths
    undo_stack = []
    red_score = 0
    blue_score = 0

    running = True
    while running:
        # check terminal
        if is_terminal(board):
            w = winner(board)
            if w == "Red":
                red_score += 1
            elif w == "Blue":
                blue_score += 1
            ans = show_win_popup(screen, w)
            if ans == "restart":
                board = initial_board(); turn = 1; selected=None; legal_paths_for_selected=[]
                undo_stack.clear()
                continue

        # draw
        board_surface = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
        move_highlights = [p[-1] for p in legal_paths_for_selected] if legal_paths_for_selected else None
        draw_board(board_surface, board, selected, move_highlights)
        screen.blit(board_surface, (0,0))
        draw_panel(screen, red_score, blue_score, turn)
        pygame.display.flip()
        clock.tick(FPS)

        # events
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
                break
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q:
                    running = False
                    break
                if e.key == pygame.K_r:
                    board = initial_board(); turn = 1; selected=None; legal_paths_for_selected=[]
                    undo_stack.clear()
                    continue
                if e.key == pygame.K_u:
                    if undo_stack:
                        board, turn = undo_stack.pop()
                        selected = None
                        legal_paths_for_selected = []
                    continue
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                if mx < 0 or mx >= BOARD_SIZE or my < 0 or my >= BOARD_SIZE:
                    continue
                r = my // SQ
                c = mx // SQ
                piece = board[r][c]

                # build all captures for current player to enforce forced captures
                all_captures = []
                for rr in range(ROWS):
                    for cc in range(COLS):
                        if board[rr][cc] * turn > 0:
                            _, cm = get_piece_moves(board, rr, cc)
                            for p in cm:
                                all_captures.append((rr, cc, p))

                if selected is None:
                    # select only own pieces
                    if piece * turn > 0:
                        selected = (r, c)
                        nm, cm = get_piece_moves(board, r, c)
                        # If there are global captures, only show capture moves for this piece
                        legal_paths_for_selected = cm if all_captures else nm
                    else:
                        # clicked empty or opponent piece -> no select
                        selected = None
                        legal_paths_for_selected = []
                else:
                    # see if clicked one of the legal destinations
                    chosen_path = None
                    for p in legal_paths_for_selected:
                        if p[-1] == (r, c):
                            chosen_path = p
                            break
                    if chosen_path:
                        # save undo
                        undo_stack.append((clone_board(board), turn))
                        # apply move
                        board = apply_move(board, (selected[0], selected[1], chosen_path))
                        # after capture, check if that same piece has further captures (multi-jump)
                        end_r, end_c = chosen_path[-1]
                        _, further_caps = get_piece_moves(board, end_r, end_c)
                        # Only allow multi-jump if a capture happened and further caps exist
                        jumped = any(abs(chosen_path[i][0] - (selected[0] if i==0 else chosen_path[i-1][0])) == 2 or
                                     abs(chosen_path[i][1] - (selected[1] if i==0 else chosen_path[i-1][1])) == 2
                                     for i in range(len(chosen_path)))
                        if jumped and further_caps:
                            # continue with same player's turn, but only that piece may move
                            selected = (end_r, end_c)
                            legal_paths_for_selected = further_caps
                        else:
                            # switch turn
                            turn *= -1
                            selected = None
                            legal_paths_for_selected = []
                    else:
                        # reselect if user clicked own piece
                        if piece * turn > 0:
                            selected = (r, c)
                            nm, cm = get_piece_moves(board, r, c)
                            legal_paths_for_selected = cm if all_captures else nm
                        else:
                            selected = None
                            legal_paths_for_selected = []

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
