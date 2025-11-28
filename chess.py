import chess
import chessengine
import chess.pgn
import os
import time

# Optional: Simple Stockfish integration (uncomment if you have Stockfish installed)
# ENGINE_PATH = "/usr/games/stockfish"  # Linux
# ENGINE_PATH = "stockfish"              # macOS with stockfish installed via brew
# ENGINE_PATH = "stockfish.exe"          # Windows

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_board(board):
    print("\n   +---+---+---+---+---+---+---+---+")
    for rank in range(7, -1, -1):
        row = f" {rank+1} "
        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            symbol = piece.symbol() if piece else "."
            row += f"| {symbol} "
        row += "|"
        print(row)
        print("   +---+---+---+---+---+---+---+---+")
    print("     a   b   c   d   e   f   g   h  \n")

def get_player_move(board):
    while True:
        try:
            move_uci = input(f"\n{'White' if board.turn else 'Black'} to move (e.g. e2e4, O-O, e7e8=Q): ").strip()
            if move_uci == "quit" or move_uci == "exit":
                return None
            if move_uci == "undo" and len(board.move_stack) > 0:
                board.pop()
                if len(board.move_stack) > 0:
                    board.pop()  # remove opponent's move too for fair undo
                print("Undone last move.")
                print_board(board)
                continue

            move = board.parse_san(move_uci) if move_uci.replace("-", "").replace("O", "").isalnum() else None
            if not move:
                move = board.parse_uci(move_uci)

            if move in board.legal_moves:
                return move
            else:
                print("Illegal move. Try again.")
        except Exception as e:
            print("Invalid input. Use SAN (e.g. Nf3) or UCI (e.g. g1f3).")

def play_chess_vs_human():
    board = chess.Board()
    print("Welcome to Chess!")
    print("Enter moves in algebraic notation: e2e4, Nf3, O-O, e7e8=Q")
    print("Type 'quit' to exit, 'undo' to take back a move.\n")
    
    while not board.is_game_over():
        clear_screen()
        print_board(board)
        
        if board.is_check():
            print("CHECK!")
        
        print(f"Move history: {len(board.move_stack) // 2 + 1}. {'White' if board.turn else 'Black'} to move")
        
        move = get_player_move(board)
        if move is None:
            print("Goodbye!")
            break
            
        board.push(move)
        
        # Show result if game over
        if board.is_game_over():
            clear_screen()
            print_board(board)
            print("\n=== GAME OVER ===")
            outcome = board.outcome()
            if outcome.winner is True:
                print("White wins!")
            elif outcome.winner is False:
                print("Black wins!")
            else:
                print("Draw!")
            print(f"Reason: {outcome.termination.name}")
            print(f"Final position FEN: {board.fen()}")

def play_chess_vs_computer(difficulty_seconds=1.0):
    board = chess.Board()
    try:
        engine = chessengine.SimpleEngine.popen_uci(ENGINE_PATH)
        engine.configure({"Skill Level": 10})  # 0-20, or adjust as needed
    except:
        print("Stockfish not found. Falling back to random legal moves.")
        engine = None

    print(f"Chess vs Computer! You are {'White' if board.turn else 'Black'}")
    print("Type 'quit' to exit\n")
    
    while not board.is_game_over():
        clear_screen()
        print_board(board)
        
        if board.is_check():
            print("CHECK!")

        if board.turn == chess.WHITE:  # Human plays White by default
            print("Your move (White):")
            move = get_player_move(board)
            if move is None:
                break
            board.push(move)
        else:
            print(f"Computer is thinking... ({difficulty_seconds}s)")
            if engine:
                result = engine.play(board, chessengine.Limit(time=difficulty_seconds))
                move = result.move
            else:
                move = chessengine.play_random(board).move
            
            print(f"Computer plays: {board.san(move)}")
            board.push(move)
            time.sleep(0.5)

    if board.is_game_over():
        clear_screen()
        print_board(board)
        outcome = board.outcome()
        print("\n=== GAME OVER ===")
        if outcome.winner == chess.WHITE:
            print("You win!" if board.turn == chess.BLACK else "You lose!")
        elif outcome.winner == chess.BLACK:
            print("You win!" if board.turn == chess.WHITE else "You lose!")
        else:
            print("Draw!")

    if engine:
        engine.quit()

# === MAIN MENU ===
if __name__ == "__main__":
    while True:
        clear_screen()
        print("═" * 40)
        print("     PYTHON CHESS - INTERACTIVE")
        print("═" * 40)
        print("1. Human vs Human")
        print("2. Human (White) vs Computer")
        print("3. Quit")
        choice = input("\nChoose mode: ").strip()

        if choice == "1":
            play_chess_vs_human()
        elif choice == "2":
            sec = input("Thinking time in seconds (0.1-5, default 1.0): ").strip()
            try:
                sec = float(sec) if sec else 1.0
            except:
                sec = 1.0
            play_chess_vs_computer(difficulty_seconds=sec)
        elif choice in ["3", "quit", "exit"]:
            print("Thanks for playing!")
            break
        else:
            print("Invalid choice.")
            time.sleep(1)