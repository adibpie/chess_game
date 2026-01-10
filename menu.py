# Menu system for chess game
import pygame
from constants import *

class Menu:
    def __init__(self):
        self.selected_mode = None
        self.ai_type = None
        self.ai_difficulty = 3
        self.room_code = ""
        self.entering_room_code = False
        self.showing_ai_selection = False
        
    def draw_pixel_text(self, text, font, color, pos, pixel_size=2):
        """Draw pixelated text effect"""
        # Create a larger surface for pixelation
        large_surface = pygame.Surface((font.size(text)[0] * pixel_size, font.size(text)[1] * pixel_size))
        large_surface.fill((0, 0, 0, 0))  # Transparent
        text_surf = font.render(text, True, color)
        # Scale up
        large_surface = pygame.transform.scale(text_surf, (font.size(text)[0] * pixel_size, font.size(text)[1] * pixel_size))
        # Scale down for pixelation
        final_surf = pygame.transform.scale(large_surface, font.size(text))
        screen.blit(final_surf, pos)
        return final_surf
    
    def draw_pixel_button(self, rect, text, font, base_color, hover_color=None, hover=False):
        """Draw a pixelated retro-style button"""
        # Pixelated border effect
        border_color = (0, 0, 0)
        highlight_color = (255, 255, 255)
        shadow_color = (100, 100, 100)
        
        # Main button
        color = hover_color if hover and hover_color else base_color
        pygame.draw.rect(screen, color, rect)
        
        # 3D effect - highlight top/left, shadow bottom/right
        pygame.draw.line(screen, highlight_color, (rect.left, rect.top), (rect.right, rect.top), 3)
        pygame.draw.line(screen, highlight_color, (rect.left, rect.top), (rect.left, rect.bottom), 3)
        pygame.draw.line(screen, shadow_color, (rect.right, rect.top), (rect.right, rect.bottom), 3)
        pygame.draw.line(screen, shadow_color, (rect.left, rect.bottom), (rect.right, rect.bottom), 3)
        
        # Outer border
        pygame.draw.rect(screen, border_color, rect, 2)
        
        # Text with pixelation
        text_surf = self.draw_pixel_text(text, font, border_color, (0, 0), pixel_size=3)
        text_rect = text_surf.get_rect(center=rect.center)
        # Offset for 3D effect
        screen.blit(text_surf, (text_rect.x + 2, text_rect.y + 2))
        text_surf = self.draw_pixel_text(text, font, (255, 255, 255), (0, 0), pixel_size=3)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)
    
    def draw_main_menu(self):
        # Retro pixelated background
        screen.fill((20, 20, 40))  # Dark blue background
        
        # Draw pixelated grid pattern
        grid_color = (30, 30, 50)
        for x in range(0, WIDTH, 20):
            pygame.draw.line(screen, grid_color, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 20):
            pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y), 1)
        
        # Pixelated title
        title_y = 100
        title_text = 'CHESS GAME'
        title_surf = self.draw_pixel_text(title_text, big_font, (255, 255, 0), (0, 0), pixel_size=4)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, title_y))
        screen.blit(title_surf, title_rect)
        
        # Subtitle
        subtitle = self.draw_pixel_text('RETRO EDITION', medium_font, (200, 200, 200), (0, 0), pixel_size=3)
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, title_y + 60))
        screen.blit(subtitle, subtitle_rect)
        
        # Button dimensions
        button_width = 450
        button_height = 90
        button_x = (WIDTH - button_width) // 2
        button_spacing = 110
        
        # Local PvP button
        pvp_y = 280
        pvp_rect = pygame.Rect(button_x, pvp_y, button_width, button_height)
        mouse_pos = pygame.mouse.get_pos()
        pvp_hover = pvp_rect.collidepoint(mouse_pos)
        self.draw_pixel_button(pvp_rect, 'LOCAL PVP', medium_font, 
                              (100, 150, 255), (150, 200, 255), pvp_hover)
        
        # Play vs AI button
        ai_y = pvp_y + button_spacing
        ai_rect = pygame.Rect(button_x, ai_y, button_width, button_height)
        ai_hover = ai_rect.collidepoint(mouse_pos)
        self.draw_pixel_button(ai_rect, 'PLAY VS AI', medium_font,
                              (100, 255, 100), (150, 255, 150), ai_hover)
        
        # Online Multiplayer button
        online_y = ai_y + button_spacing
        online_rect = pygame.Rect(button_x, online_y, button_width, button_height)
        online_hover = online_rect.collidepoint(mouse_pos)
        self.draw_pixel_button(online_rect, 'ONLINE MULTIPLAYER', medium_font,
                              (255, 200, 100), (255, 230, 150), online_hover)
        
        # Pixelated border around screen
        border_color = (255, 255, 0)
        pygame.draw.rect(screen, border_color, (0, 0, WIDTH, HEIGHT), 5)
        
        return {'pvp': pvp_rect, 'ai': ai_rect, 'online': online_rect}
    
    def draw_ai_selection(self):
        # Retro background
        screen.fill((20, 20, 40))
        grid_color = (30, 30, 50)
        for x in range(0, WIDTH, 20):
            pygame.draw.line(screen, grid_color, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 20):
            pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y), 1)
        
        # Title
        title_surf = self.draw_pixel_text('SELECT AI OPPONENT', big_font, (255, 255, 0), (0, 0), pixel_size=4)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 150))
        screen.blit(title_surf, title_rect)
        
        button_width = 450
        button_height = 90
        button_x = (WIDTH - button_width) // 2
        button_spacing = 110
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Minimax AI button
        minimax_y = 300
        minimax_rect = pygame.Rect(button_x, minimax_y, button_width, button_height)
        minimax_hover = minimax_rect.collidepoint(mouse_pos)
        self.draw_pixel_button(minimax_rect, 'MINIMAX AI', medium_font,
                              (100, 150, 255), (150, 200, 255), minimax_hover)
        
        # Stockfish AI button
        stockfish_y = minimax_y + button_spacing
        stockfish_rect = pygame.Rect(button_x, stockfish_y, button_width, button_height)
        stockfish_hover = stockfish_rect.collidepoint(mouse_pos)
        self.draw_pixel_button(stockfish_rect, 'STOCKFISH AI', medium_font,
                              (100, 255, 100), (150, 255, 150), stockfish_hover)
        
        # Back button
        back_y = stockfish_y + button_spacing
        back_rect = pygame.Rect(button_x, back_y, button_width, button_height)
        back_hover = back_rect.collidepoint(mouse_pos)
        self.draw_pixel_button(back_rect, 'BACK', medium_font,
                              (150, 150, 150), (200, 200, 200), back_hover)
        
        # Difficulty selector for Minimax
        if self.ai_type == 'minimax':
            diff_text = f'DIFFICULTY (DEPTH): {self.ai_difficulty}'
            diff_surf = self.draw_pixel_text(diff_text, font, (255, 255, 255), (0, 0), pixel_size=2)
            diff_rect = diff_surf.get_rect(center=(WIDTH // 2, back_y + button_height + 40))
            screen.blit(diff_surf, diff_rect)
            
            left_arrow = self.draw_pixel_text('<', font, (255, 255, 0), (0, 0), pixel_size=3)
            right_arrow = self.draw_pixel_text('>', font, (255, 255, 0), (0, 0), pixel_size=3)
            screen.blit(left_arrow, (button_x - 50, back_y + button_height + 30))
            screen.blit(right_arrow, (button_x + button_width + 20, back_y + button_height + 30))
        
        pygame.draw.rect(screen, (255, 255, 0), (0, 0, WIDTH, HEIGHT), 5)
        
        return {'minimax': minimax_rect, 'stockfish': stockfish_rect, 'back': back_rect}
    
    def draw_online_menu(self):
        # Retro background
        screen.fill((20, 20, 40))
        grid_color = (30, 30, 50)
        for x in range(0, WIDTH, 20):
            pygame.draw.line(screen, grid_color, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 20):
            pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y), 1)
        
        # Title
        title_surf = self.draw_pixel_text('ONLINE MULTIPLAYER', big_font, (255, 255, 0), (0, 0), pixel_size=4)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 150))
        screen.blit(title_surf, title_rect)
        
        button_width = 450
        button_height = 90
        button_x = (WIDTH - button_width) // 2
        button_spacing = 110
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Create Room button
        create_y = 300
        create_rect = pygame.Rect(button_x, create_y, button_width, button_height)
        create_hover = create_rect.collidepoint(mouse_pos)
        self.draw_pixel_button(create_rect, 'CREATE ROOM', medium_font,
                              (100, 150, 255), (150, 200, 255), create_hover)
        
        # Join Room button
        join_y = create_y + button_spacing
        join_rect = pygame.Rect(button_x, join_y, button_width, button_height)
        join_hover = join_rect.collidepoint(mouse_pos)
        self.draw_pixel_button(join_rect, 'JOIN ROOM', medium_font,
                              (100, 255, 100), (150, 255, 150), join_hover)
        
        # Back button
        back_y = join_y + button_spacing
        back_rect = pygame.Rect(button_x, back_y, button_width, button_height)
        back_hover = back_rect.collidepoint(mouse_pos)
        self.draw_pixel_button(back_rect, 'BACK', medium_font,
                              (150, 150, 150), (200, 200, 200), back_hover)
        
        # Room code input
        if self.entering_room_code:
            input_text = f'ENTER ROOM CODE: {self.room_code}'
            input_surf = self.draw_pixel_text(input_text, font, (255, 255, 255), (0, 0), pixel_size=2)
            input_rect = input_surf.get_rect(center=(WIDTH // 2, back_y + button_height + 40))
            screen.blit(input_surf, input_rect)
        
        pygame.draw.rect(screen, (255, 255, 0), (0, 0, WIDTH, HEIGHT), 5)
        
        return {'create': create_rect, 'join': join_rect, 'back': back_rect}
    
    def handle_click(self, pos, buttons):
        for key, rect in buttons.items():
            if rect.collidepoint(pos):
                return key
        return None
    
    def reset(self):
        self.selected_mode = None
        self.ai_type = None
        self.ai_difficulty = 3
        self.room_code = ""
        self.entering_room_code = False
        self.showing_ai_selection = False
