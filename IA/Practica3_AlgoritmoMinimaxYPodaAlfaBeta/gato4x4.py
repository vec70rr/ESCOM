import tkinter as tk
from tkinter import messagebox
import math

class TicTacToe4x4:
    def __init__(self, root):
        self.root = root
        self.root.title("Gato 4x4")
        self.root.resizable(False, False)

        self.board = [['' for _ in range(4)] for _ in range(4)]
        self.human_player = 'X'
        self.ai_player = 'O'
        self.current_player = self.human_player

        self.buttons = [[None for _ in range(4)] for _ in range(4)]
        self.create_widgets()
        self.update_status("Tu turno (X)")

    def create_widgets(self):
        """Crea y organiza los widgets de la interfaz gráfica."""
        main_frame = tk.Frame(self.root, padx=10, pady=10, bg="#2c3e50")
        main_frame.pack()

        board_frame = tk.Frame(main_frame, bg="#34495e")
        board_frame.grid(row=0, column=0, pady=(0, 10))

        for i in range(4):
            for j in range(4):
                self.buttons[i][j] = tk.Button(
                    board_frame, text='', font=('Helvetica', 24, 'bold'),
                    width=4, height=2,
                    bg="#ecf0f1", activebackground="#bdc3c7",
                    fg="#2c3e50",
                    command=lambda i=i, j=j: self.player_move(i, j)
                )
                self.buttons[i][j].grid(row=i, column=j, padx=2, pady=2)

        self.status_label = tk.Label(
            main_frame, text="", font=('Helvetica', 14),
            pady=5, bg="#2c3e50", fg="white"
        )
        self.status_label.grid(row=1, column=0, sticky="ew")

        restart_button = tk.Button(
            main_frame, text="Reiniciar Juego", font=('Helvetica', 12),
            command=self.reset_game, bg="#e74c3c", fg="white",
            activebackground="#c0392b"
        )
        restart_button.grid(row=2, column=0, sticky="ew", pady=(5,0))

    def update_status(self, message):
        """Actualiza la etiqueta de estado del juego."""
        self.status_label.config(text=message)

    def player_move(self, i, j):
        """Maneja el movimiento del jugador humano."""
        if self.board[i][j] == '' and self.current_player == self.human_player:
            self.make_move(i, j, self.human_player)
            if not self.check_game_over():
                self.current_player = self.ai_player
                self.update_status("Turno de la computadora (O)...")
                self.root.after(500, self.ai_move)

    def ai_move(self):
        """Ejecuta el movimiento de la IA usando Minimax."""
        if self.is_board_empty():
            # Para el primer movimiento, la IA elige una esquina al azar.
            # Esto mejora la velocidad inicial sin necesidad de calcular todo el árbol.
            import random
            i, j = random.choice([(0,0), (0,3), (3,0), (3,3)])
        else:
            best_score = -math.inf
            best_move = None
            for i in range(4):
                for j in range(4):
                    if self.board[i][j] == '':
                        self.board[i][j] = self.ai_player
                        score = self.minimax(0, False, -math.inf, math.inf)
                        self.board[i][j] = ''
                        if score > best_score:
                            best_score = score
                            best_move = (i, j)
        
        if best_move:
            self.make_move(best_move[0], best_move[1], self.ai_player)
            self.check_game_over()
            self.current_player = self.human_player
            self.update_status("Tu turno (X)")

    def make_move(self, i, j, player):
        """Realiza un movimiento en el tablero y actualiza la GUI."""
        self.board[i][j] = player
        self.buttons[i][j].config(text=player, state='disabled', disabledforeground=("#e74c3c" if player == 'O' else "#3498db"))

    def check_winner(self):
        """Verifica si hay un ganador."""
        # Verificar filas y columnas
        for i in range(4):
            if all(self.board[i][j] == self.human_player for j in range(4)) or \
               all(self.board[j][i] == self.human_player for j in range(4)):
                return self.human_player
            if all(self.board[i][j] == self.ai_player for j in range(4)) or \
               all(self.board[j][i] == self.ai_player for j in range(4)):
                return self.ai_player
        
        # Verificar diagonales
        if all(self.board[i][i] == self.human_player for i in range(4)) or \
           all(self.board[i][3-i] == self.human_player for i in range(4)):
            return self.human_player
        if all(self.board[i][i] == self.ai_player for i in range(4)) or \
           all(self.board[i][3-i] == self.ai_player for i in range(4)):
            return self.ai_player

        return None

    def is_board_full(self):
        """Verifica si el tablero está lleno."""
        return all(self.board[i][j] != '' for i in range(4) for j in range(4))

    def check_game_over(self):
        """Comprueba el estado del juego (victoria, empate o continuación)."""
        winner = self.check_winner()
        if winner:
            self.highlight_winner(winner)
            self.end_game(f"¡El jugador {winner} ha ganado!")
            return True
        elif self.is_board_full():
            self.end_game("¡Es un empate!")
            return True
        return False
        
    def highlight_winner(self, winner):
        """Resalta la línea ganadora."""
        color = "#2ecc71"
        # Filas
        for i in range(4):
            if all(self.board[i][j] == winner for j in range(4)):
                for j in range(4): self.buttons[i][j].config(bg=color)
        # Columnas
        for j in range(4):
            if all(self.board[i][j] == winner for i in range(4)):
                for i in range(4): self.buttons[i][j].config(bg=color)
        # Diagonales
        if all(self.board[i][i] == winner for i in range(4)):
            for i in range(4): self.buttons[i][i].config(bg=color)
        if all(self.board[i][3-i] == winner for i in range(4)):
            for i in range(4): self.buttons[i][3-i].config(bg=color)

    def end_game(self, message):
        """Finaliza el juego mostrando un mensaje y deshabilitando los botones."""
        self.update_status(message)
        for i in range(4):
            for j in range(4):
                self.buttons[i][j].config(state='disabled')
        messagebox.showinfo("Juego Terminado", message)

    def reset_game(self):
        """Reinicia el juego a su estado inicial."""
        self.board = [['' for _ in range(4)] for _ in range(4)]
        self.current_player = self.human_player
        for i in range(4):
            for j in range(4):
                self.buttons[i][j].config(text='', state='normal', bg="#ecf0f1")
        self.update_status("Tu turno (X)")

    def is_board_empty(self):
        """Verifica si el tablero está completamente vacío."""
        return all(self.board[i][j] == '' for i in range(4) for j in range(4))

    def minimax(self, depth, is_maximizing, alpha, beta):
        """
        Algoritmo Minimax con poda Alfa-Beta.
        Retorna la mejor puntuación para el estado actual del tablero.
        """
        winner = self.check_winner()
        if winner == self.ai_player:
            return 10 - depth  # Premiar victorias más rápidas
        if winner == self.human_player:
            return depth - 10  # Castigar derrotas más rápidas
        if self.is_board_full():
            return 0
        
        # Un límite de profundidad es crucial en un tablero 4x4 para evitar
        # que el cálculo sea demasiado lento.
        if depth > 4: 
            return 0

        if is_maximizing:
            max_eval = -math.inf
            for i in range(4):
                for j in range(4):
                    if self.board[i][j] == '':
                        self.board[i][j] = self.ai_player
                        evaluation = self.minimax(depth + 1, False, alpha, beta)
                        self.board[i][j] = ''
                        max_eval = max(max_eval, evaluation)
                        alpha = max(alpha, evaluation)
                        if beta <= alpha:
                            break
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for i in range(4):
                for j in range(4):
                    if self.board[i][j] == '':
                        self.board[i][j] = self.human_player
                        evaluation = self.minimax(depth + 1, True, alpha, beta)
                        self.board[i][j] = ''
                        min_eval = min(min_eval, evaluation)
                        beta = min(beta, evaluation)
                        if beta <= alpha:
                            break
                if beta <= alpha:
                    break
            return min_eval

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe4x4(root)
    root.mainloop()