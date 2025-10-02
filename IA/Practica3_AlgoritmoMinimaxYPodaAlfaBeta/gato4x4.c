#include <ncurses.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <time.h>
#include <math.h>

// Definiciones del tablero y jugadores
#define BOARD_SIZE 4
#define HUMAN_PLAYER 'X'
#define AI_PLAYER 'O'
#define EMPTY_CELL ' '

// Prototipos de funciones
void init_game();
void draw_board(char board[BOARD_SIZE][BOARD_SIZE]);
void handle_player_input(char board[BOARD_SIZE][BOARD_SIZE]);
void ai_move(char board[BOARD_SIZE][BOARD_SIZE]);
int minimax(char board[BOARD_SIZE][BOARD_SIZE], int depth, bool is_maximizing, int alpha, int beta);
int evaluate(char board[BOARD_SIZE][BOARD_SIZE]);
char check_winner(char board[BOARD_SIZE][BOARD_SIZE]);
bool is_board_full(char board[BOARD_SIZE][BOARD_SIZE]);
void end_game(const char* message);

int main() {
    char board[BOARD_SIZE][BOARD_SIZE];
    
    // Inicialización de ncurses y configuración del juego
    initscr();
    cbreak();
    noecho();
    keypad(stdscr, TRUE);
    curs_set(0);
    srand(time(NULL)); // Semilla para números aleatorios

    // Configuración de colores
    start_color();
    init_pair(1, COLOR_CYAN, COLOR_BLACK);  // Color para la rejilla
    init_pair(2, COLOR_BLUE, COLOR_BLACK);  // Color para 'X'
    init_pair(3, COLOR_RED, COLOR_BLACK);   // Color para 'O'
    init_pair(4, COLOR_GREEN, COLOR_BLACK); // Color para el ganador
    init_pair(5, COLOR_WHITE, COLOR_BLACK); // Color por defecto

    bool running = true;
    while(running) {
        init_game(board);
        draw_board(board);
        mvprintw(BOARD_SIZE * 2 + 3, 2, "Tu turno (X). Usa las flechas y Enter.");

        int current_player = 0; // 0 para humano, 1 para IA
        while (true) {
            if (current_player == 0) { // Turno del humano
                handle_player_input(board);
            } else { // Turno de la IA
                mvprintw(BOARD_SIZE * 2 + 3, 2, "Pensando...                            ");
                refresh();
                ai_move(board);
                draw_board(board);
                mvprintw(BOARD_SIZE * 2 + 3, 2, "Tu turno (X). Usa las flechas y Enter.");
            }
            
            draw_board(board);
            refresh();
            
            char winner = check_winner(board);
            if (winner != EMPTY_CELL) {
                char msg[50];
                sprintf(msg, "¡El jugador %c ha ganado!", winner);
                end_game(msg);
                break;
            }
            if (is_board_full(board)) {
                end_game("¡Es un empate!");
                break;
            }
            
            current_player = 1 - current_player; // Cambiar de turno
        }

        mvprintw(BOARD_SIZE * 2 + 6, 2, "¿Jugar de nuevo? (s/n)");
        int ch;
        while((ch = getch()) != 's' && ch != 'n');
        if (ch == 'n') {
            running = false;
        }
        clear();
    }
    
    endwin();
    return 0;
}

// Inicializa el tablero con celdas vacías
void init_game(char board[BOARD_SIZE][BOARD_SIZE]) {
    for (int i = 0; i < BOARD_SIZE; i++) {
        for (int j = 0; j < BOARD_SIZE; j++) {
            board[i][j] = EMPTY_CELL;
        }
    }
}

// Dibuja el tablero en la terminal
void draw_board(char board[BOARD_SIZE][BOARD_SIZE]) {
    attron(COLOR_PAIR(1));
    for (int i = 0; i < BOARD_SIZE; i++) {
        for (int j = 0; j < BOARD_SIZE; j++) {
            mvprintw(i * 2, j * 4, " %c ", board[i][j] == EMPTY_CELL ? '.' : board[i][j]);
            if (j < BOARD_SIZE - 1) mvprintw(i * 2, j * 4 + 3, "|");
        }
        if (i < BOARD_SIZE - 1) {
            mvprintw(i * 2 + 1, 0, "---+---+---+---");
        }
    }
    attroff(COLOR_PAIR(1));
    refresh();
}

// Maneja la entrada del jugador con las flechas del teclado
void handle_player_input(char board[BOARD_SIZE][BOARD_SIZE]) {
    int x = 0, y = 0, ch;
    while (true) {
        mvprintw(y * 2, x * 4, "[%c]", board[y][x] == EMPTY_CELL ? ' ' : board[y][x]);
        refresh();
        ch = getch();
        mvprintw(y * 2, x * 4, " %c ", board[y][x] == EMPTY_CELL ? '.' : board[y][x]); // Restaurar

        switch (ch) {
            case KEY_UP:    y = (y == 0) ? BOARD_SIZE - 1 : y - 1; break;
            case KEY_DOWN:  y = (y == BOARD_SIZE - 1) ? 0 : y + 1; break;
            case KEY_LEFT:  x = (x == 0) ? BOARD_SIZE - 1 : x - 1; break;
            case KEY_RIGHT: x = (x == BOARD_SIZE - 1) ? 0 : x + 1; break;
            case 10: // Enter
                if (board[y][x] == EMPTY_CELL) {
                    board[y][x] = HUMAN_PLAYER;
                    return;
                }
        }
    }
}

// Lógica para que la IA elija su movimiento
void ai_move(char board[BOARD_SIZE][BOARD_SIZE]) {
    int best_score = INT_MIN;
    int move_row = -1, move_col = -1;

    for (int i = 0; i < BOARD_SIZE; i++) {
        for (int j = 0; j < BOARD_SIZE; j++) {
            if (board[i][j] == EMPTY_CELL) {
                board[i][j] = AI_PLAYER;
                int score = minimax(board, 0, false, INT_MIN, INT_MAX);
                board[i][j] = EMPTY_CELL;
                if (score > best_score) {
                    best_score = score;
                    move_row = i;
                    move_col = j;
                }
            }
        }
    }
    if (move_row != -1) {
        board[move_row][move_col] = AI_PLAYER;
    }
}

// Algoritmo Minimax con poda alfa-beta
int minimax(char board[BOARD_SIZE][BOARD_SIZE], int depth, bool is_maximizing, int alpha, int beta) {
    int score = evaluate(board);
    if (score == 10) return score - depth;
    if (score == -10) return score + depth;
    if (is_board_full(board) || depth > 4) return 0; // Limitar profundidad

    if (is_maximizing) {
        int best = INT_MIN;
        for (int i = 0; i < BOARD_SIZE; i++) {
            for (int j = 0; j < BOARD_SIZE; j++) {
                if (board[i][j] == EMPTY_CELL) {
                    board[i][j] = AI_PLAYER;
                    best = fmax(best, minimax(board, depth + 1, !is_maximizing, alpha, beta));
                    board[i][j] = EMPTY_CELL;
                    alpha = fmax(alpha, best);
                    if (beta <= alpha) break;
                }
            }
            if (beta <= alpha) break;
        }
        return best;
    } else {
        int best = INT_MAX;
        for (int i = 0; i < BOARD_SIZE; i++) {
            for (int j = 0; j < BOARD_SIZE; j++) {
                if (board[i][j] == EMPTY_CELL) {
                    board[i][j] = HUMAN_PLAYER;
                    best = fmin(best, minimax(board, depth + 1, !is_maximizing, alpha, beta));
                    board[i][j] = EMPTY_CELL;
                    beta = fmin(beta, best);
                    if (beta <= alpha) break;
                }
            }
            if (beta <= alpha) break;
        }
        return best;
    }
}

// Evalúa el estado del tablero
int evaluate(char board[BOARD_SIZE][BOARD_SIZE]) {
    char winner = check_winner(board);
    if (winner == AI_PLAYER) return 10;
    if (winner == HUMAN_PLAYER) return -10;
    return 0;
}

// Verifica si hay un ganador
char check_winner(char board[BOARD_SIZE][BOARD_SIZE]) {
    // Verificar filas y columnas
    for (int i = 0; i < BOARD_SIZE; i++) {
        if (board[i][0] != EMPTY_CELL && board[i][0] == board[i][1] && board[i][1] == board[i][2] && board[i][2] == board[i][3]) return board[i][0];
        if (board[0][i] != EMPTY_CELL && board[0][i] == board[1][i] && board[1][i] == board[2][i] && board[2][i] == board[3][i]) return board[0][i];
    }
    // Verificar diagonales
    if (board[0][0] != EMPTY_CELL && board[0][0] == board[1][1] && board[1][1] == board[2][2] && board[2][2] == board[3][3]) return board[0][0];
    if (board[0][3] != EMPTY_CELL && board[0][3] == board[1][2] && board[1][2] == board[2][1] && board[2][1] == board[3][0]) return board[0][3];
    return EMPTY_CELL;
}

// Verifica si el tablero está lleno
bool is_board_full(char board[BOARD_SIZE][BOARD_SIZE]) {
    for (int i = 0; i < BOARD_SIZE; i++) {
        for (int j = 0; j < BOARD_SIZE; j++) {
            if (board[i][j] == EMPTY_CELL) return false;
        }
    }
    return true;
}

// Muestra el mensaje de fin de juego
void end_game(const char* message) {
    mvprintw(BOARD_SIZE * 2 + 5, 2, "                                      ");
    attron(COLOR_PAIR(4));
    mvprintw(BOARD_SIZE * 2 + 5, 2, "%s", message);
    attroff(COLOR_PAIR(4));
    refresh();
}