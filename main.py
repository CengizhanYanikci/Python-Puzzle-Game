import pygame
import sys
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import random

# ---------------------------------------------
# Initialize Tkinter (for file dialog) and variables
# ---------------------------------------------
root = tk.Tk()
root.withdraw()
pieces = []             # List to hold puzzle pieces
GRID_SIZE = 4           # Number of rows and columns
frame_rect = None       # Rectangle for the border frame
SNAP_THRESHOLD = 20     # Distance in pixels for automatic snapping
# ---------------------------------------------

# ---------------------------------------------
# Function to upload image and create puzzle pieces
# ---------------------------------------------
def upload_image():
    global pieces, frame_rect
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        img = Image.open(file_path)
        img = img.resize((400, 400))
        loaded_image = pygame.image.fromstring(img.tobytes(), img.size, img.mode)

        # Clear any previous puzzle pieces and split new image
        pieces.clear()
        pieces.extend(split_image(loaded_image))

        # Define the border frame in the center of the screen
        start_x = (SCREEN_WIDTH - loaded_image.get_width()) // 2
        start_y = (SCREEN_HEIGHT - loaded_image.get_height()) // 2
        frame_rect = pygame.Rect(start_x, start_y, loaded_image.get_width(), loaded_image.get_height())

# ---------------------------------------------
# Function to split image into grid pieces
# ---------------------------------------------
def split_image(surface):
    piece_list = []
    img_width = surface.get_width()
    img_height = surface.get_height()
    piece_width = img_width // GRID_SIZE
    piece_height = img_height // GRID_SIZE

    start_x = (SCREEN_WIDTH - img_width) // 2
    start_y = (SCREEN_HEIGHT - img_height) // 2

    # Create each piece and store its position
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pygame.Rect(col * piece_width, row * piece_height, piece_width, piece_height)
            piece_surface = surface.subsurface(rect).copy()
            piece_list.append({
                "image": piece_surface,
                "pos": (start_x + col * piece_width, start_y + row * piece_height),
                "current_pos": (start_x + col * piece_width, start_y + row * piece_height)
            })
    return piece_list

# ---------------------------------------------
# Initialize Pygame
# ---------------------------------------------
pygame.init()
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Puzzle Game")

# Colors
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
BROWN = (200, 100, 50)
BLACK = (0, 0, 0)

# Font for buttons
font = pygame.font.Font(None, 50)

# ----------------------------
# Button definitions
# ----------------------------
play_button = pygame.Rect((SCREEN_WIDTH-200)//2, (SCREEN_HEIGHT-100)//2, 200, 100)
play_visible = True

distribute_button = pygame.Rect((SCREEN_WIDTH-200)//2, play_button.bottom+20, 200, 60)
distribute_visible = True

dragging_piece = None
offset_x = 0
offset_y = 0

# ---------------------------------------------
# Function to randomly distribute pieces on screen
# ---------------------------------------------
def distribute_pieces():
    padding = 10
    for i, piece in enumerate(pieces):
        max_attempts = 100
        for _ in range(max_attempts):
            rand_x = random.randint(0, SCREEN_WIDTH - piece["image"].get_width())
            rand_y = random.randint(0, SCREEN_HEIGHT - piece["image"].get_height())
            rect = pygame.Rect(rand_x, rand_y, piece["image"].get_width(), piece["image"].get_height())

            # Check overlap with other pieces
            overlap = False
            for j, other in enumerate(pieces):
                if i != j:
                    other_rect = pygame.Rect(other["current_pos"][0], other["current_pos"][1],
                                             other["image"].get_width(), other["image"].get_height())
                    if rect.colliderect(other_rect.inflate(padding, padding)):
                        overlap = True
                        break
            if not overlap:
                piece["current_pos"] = (rand_x, rand_y)
                break

# ---------------------------------------------
# Main game loop
# ---------------------------------------------
running = True
while running:
    screen.fill(WHITE)

    # Draw border frame (only the outline)
    if frame_rect:
        pygame.draw.rect(screen, BLACK, frame_rect, 4)

    # Draw puzzle pieces
    for piece in pieces:
        screen.blit(piece["image"], piece["current_pos"])

    # Draw Play button
    if play_visible:
        pygame.draw.rect(screen, BLUE, play_button)
        text = font.render("Play", True, WHITE)
        screen.blit(text, text.get_rect(center=play_button.center))

    # Draw Distribute button
    if distribute_visible and frame_rect:
        pygame.draw.rect(screen, BROWN, distribute_button)
        text2 = font.render("Distribute", True, WHITE)
        screen.blit(text2, text2.get_rect(center=distribute_button.center))

    # ---------------------------------------------
    # Event handling
    # ---------------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if play_visible and play_button.collidepoint(event.pos):
                upload_image()
                play_visible = False
            elif distribute_visible and frame_rect and distribute_button.collidepoint(event.pos):
                distribute_pieces()
                distribute_visible = False
            else:
                # Check if any piece is clicked for dragging
                for piece in reversed(pieces):
                    px, py = piece["current_pos"]
                    w, h = piece["image"].get_size()
                    rect = pygame.Rect(px, py, w, h)
                    if rect.collidepoint(event.pos):
                        dragging_piece = piece
                        offset_x = event.pos[0] - px
                        offset_y = event.pos[1] - py
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging_piece:
                # Snap to original position if close enough
                tx, ty = dragging_piece["pos"]
                cx, cy = dragging_piece["current_pos"]
                if abs(cx - tx) < SNAP_THRESHOLD and abs(cy - ty) < SNAP_THRESHOLD:
                    dragging_piece["current_pos"] = (tx, ty)

                # Snap to nearby pieces if close enough (anywhere in frame)
                for other_piece in pieces:
                    if dragging_piece is other_piece:
                        continue
                    ox, oy = other_piece["current_pos"]
                    dx = cx - ox
                    dy = cy - oy
                    if abs(dx) < SNAP_THRESHOLD and abs(dy) < SNAP_THRESHOLD:
                        dragging_piece["current_pos"] = (ox, oy)
                        break
            dragging_piece = None

        elif event.type == pygame.MOUSEMOTION:
            if dragging_piece:
                dragging_piece["current_pos"] = (event.pos[0]-offset_x, event.pos[1]-offset_y)

        elif event.type == pygame.MOUSEWHEEL:
            for piece in pieces:
                w, h = piece["image"].get_size()
                factor = 1.1 if event.y>0 else 0.9
                new_w = max(10, int(w*factor))
                new_h = max(10, int(h*factor))
                piece["image"] = pygame.transform.scale(piece["image"], (new_w, new_h))

    pygame.display.flip()

pygame.quit()
sys.exit()
