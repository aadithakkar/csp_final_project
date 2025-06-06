import chess
import chess.engine
import random

STOCKFISH_PATH = "/usr/games/stockfish"

def get_user_move(board):
    while True:
        try:
            move_input = input("Your move (in UCI, e.g., e2e4): ").strip()
            move = chess.Move.from_uci(move_input)
            if move in board.legal_moves:
                return move
            else:
                print("Illegal move. Try again.")
        except Exception:
            print("Invalid format. Try again.")

def get_engine_move(engine, board):
    try:
        engine.configure({"Skill Level": 2})
        info = engine.analyse(board, chess.engine.Limit(time=0.05), multipv=3)
        moves = [entry["pv"][0] for entry in info]
        chosen = random.choice(moves)
        return chosen
    except Exception as e:
        print("Engine failed:", e)
        return random.choice(list(board.legal_moves))

def play_game():
    board = chess.Board()
    print("Welcome! You are playing White.")
    print(board)

    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        while not board.is_game_over():
            move = get_user_move(board)
            board.push(move)
            print("\nYou played:", move)
            print(board)

            if board.is_game_over():
                break

            move = get_engine_move(engine, board)
            board.push(move)
            print("\nBot plays:", move)
            print(board)

        print("\nGame over:", board.result())
        print(board.outcome().termination.name)

if __name__ == "__main__":
    play_game()
