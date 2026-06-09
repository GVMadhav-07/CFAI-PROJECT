import streamlit as st
import chess
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# ------------------ Utility Functions ------------------
# Piece values
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0
}

# Piece-square tables (simplified)
pawn_table = [
    0, 0, 0, 0, 0, 0, 0, 0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5, 5, 10, 25, 25, 10, 5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, -5, -10, 0, 0, -10, -5, 5,
    5, 10, 10, -20, -20, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0
]
knight_table = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]
bishop_table = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]
rook_table = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, 10, 10, 10, 10, 5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    0, 0, 0, 5, 5, 0, 0, 0
]
queen_table = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
]
king_middle_game = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, 20, 0, 0, 0, 0, 20, 20,
    20, 30, 10, 0, 0, 10, 30, 20
]
king_end_game = [
    -50, -40, -30, -20, -20, -30, -40, -50,
    -30, -20, -10, 0, 0, -10, -20, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -30, 0, 0, 0, 0, -30, -30,
    -50, -30, -30, -30, -30, -30, -30, -50
]

# Helper for piece-square table
def get_piece_square_value(piece, square, endgame=False):
    if piece.piece_type == chess.PAWN:
        table = pawn_table
    elif piece.piece_type == chess.KNIGHT:
        table = knight_table
    elif piece.piece_type == chess.BISHOP:
        table = bishop_table
    elif piece.piece_type == chess.ROOK:
        table = rook_table
    elif piece.piece_type == chess.QUEEN:
        table = queen_table
    elif piece.piece_type == chess.KING:
        table = king_end_game if endgame else king_middle_game
    else:
        return 0
    # Flip for black
    if piece.color == chess.BLACK:
        square = chess.square_mirror(square)
    return table[square]

# Evaluation function
def evaluate_board(board):
    material_score = 0
    positional_score = 0
    # Material & Positional
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES[piece.piece_type]
            if piece.color == chess.WHITE:
                material_score += value
            else:
                material_score -= value
            endgame = board.is_endgame()
            positional_value = get_piece_square_value(piece, square, endgame)
            if piece.color == chess.WHITE:
                positional_score += positional_value
            else:
                positional_score -= positional_value
    # Mobility (simplified)
    mobility_score = len(list(board.legal_moves))
    # Penalty for doubled pawns
    doubled_pawn_penalty = 0
    for color in [chess.WHITE, chess.BLACK]:
        pawns = [sq for sq in board.pieces(chess.PAWN, color)]
        files = [chess.square_file(sq) for sq in pawns]
        file_counts = pd.Series(files).value_counts()
        for count in file_counts:
            if count > 1:
                doubled_pawn_penalty -= (count - 1) * 20
    total_eval = material_score + positional_score + mobility_score + doubled_pawn_penalty
    return total_eval

def is_game_over(board):
    return board.is_game_over()

# Improved move ordering: MVV-LVA + checks
def get_ordered_moves(board):
    moves = list(board.legal_moves)

    def move_score(move):
        score = 0
        # Captures prioritized with MVV-LVA
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                score += 10 * PIECE_VALUES[captured_piece.piece_type]
            # Bonus if move gives check
            temp_board = board.copy()
            temp_board.push(move)
            if temp_board.is_check():
                score += 5
        else:
            # Non-captures: prioritize checks
            temp_board = board.copy()
            temp_board.push(move)
            if temp_board.is_check():
                score += 3
            # Quiets are less prioritized
        return -score  # Negative for descending sort

    moves.sort(key=move_score)
    return moves

# Minimax with alpha-beta
def minimax(board, depth, alpha, beta, maximizing):
    if depth == 0 or is_game_over(board):
        return evaluate_board(board), None
    best_move = None
    if maximizing:
        max_eval = -np.inf
        for move in get_ordered_moves(board):
            board.push(move)
            eval_val, _ = minimax(board, depth -1, alpha, beta, False)
            board.pop()
            if eval_val > max_eval:
                max_eval = eval_val
                best_move = move
            alpha = max(alpha, eval_val)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = np.inf
        for move in get_ordered_moves(board):
            board.push(move)
            eval_val, _ = minimax(board, depth -1, alpha, beta, True)
            board.pop()
            if eval_val < min_eval:
                min_eval = eval_val
                best_move = move
            beta = min(beta, eval_val)
            if beta <= alpha:
                break
        return min_eval, best_move

# Convert move to SAN
def move_to_san(move, board):
    return board.san(move)

# ------------------ Streamlit App ------------------
st.set_page_config(layout="wide")
st.title("Interactive Chess AI Engine Demonstration")

# Initialize session state
if "board" not in st.session_state:
    st.session_state["board"] = chess.Board()
if "move_history" not in st.session_state:
    st.session_state["move_history"] = []
if "evaluations" not in st.session_state:
    st.session_state["evaluations"] = []
if "depth" not in st.session_state:
    st.session_state["depth"] = 3
if "selected_square" not in st.session_state:
    st.session_state["selected_square"] = None
if "possible_moves" not in st.session_state:
    st.session_state["possible_moves"] = []
if "engine_think" not in st.session_state:
    st.session_state["engine_think"] = False

# Sidebar controls
st.sidebar.header("Engine Settings")
depth_input = st.sidebar.slider("Search Depth", 1, 6, st.session_state["depth"])
st.session_state["depth"] = depth_input

def reset_game():
    st.session_state["board"] = chess.Board()
    st.session_state["move_history"] = []
    st.session_state["evaluations"] = []
    st.session_state["selected_square"] = None
    st.session_state["possible_moves"] = []

st.sidebar.button("Reset Game", on_click=reset_game)

# Draw the chess board
def draw_board():
    board = st.session_state["board"]
    selected = st.session_state["selected_square"]
    legal_moves = st.session_state["possible_moves"]
    square_size = 50

    cols = st.columns(8)
    for rank in range(7, -1, -1):
        row_cols = st.columns(8)
        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            symbol = piece.symbol() if piece else ""
            color = "white" if (rank + file) % 2 == 0 else "lightgray"
            label = symbol
            # Highlight selection
            if selected == square:
                style = "background-color: yellow;"
            elif square in legal_moves:
                style = "background-color: lightgreen;"
            else:
                style = f"background-color: {color};"

            def make_callback(sq=square):
                def callback():
                    on_square_click(sq)
                return callback

            btn = row_cols[file].button(
                label if symbol else " ",
                key=str(square),
                on_click=make_callback()
            )
            btn.markdown(
                f"<div style='width:{square_size}px; height:{square_size}px; {style} display:flex; align-items:center; justify-content:center;'>{label}</div>",
                unsafe_allow_html=True
            )

def on_square_click(square):
    board = st.session_state["board"]
    if st.session_state["selected_square"] is None:
        piece = board.piece_at(square)
        if piece and piece.color == board.turn:
            st.session_state["selected_square"] = square
            st.session_state["possible_moves"] = [
                move.to_square for move in board.legal_moves if move.from_square == square
            ]
        else:
            st.session_state["selected_square"] = None
            st.session_state["possible_moves"] = []
    else:
        move = None
        for m in board.legal_moves:
            if m.from_square == st.session_state["selected_square"] and m.to_square == square:
                move = m
                break
        if move:
            board.push(move)
            st.session_state["move_history"].append(move)
            # Clear selection
            st.session_state["selected_square"] = None
            st.session_state["possible_moves"] = []
            if not is_game_over(board):
                st.session_state["engine_think"] = True
        else:
            st.session_state["selected_square"] = None
            st.session_state["possible_moves"] = []

def engine_move():
    board = st.session_state["board"]
    depth = st.session_state["depth"]
    eval_score, best_move = minimax(board, depth, -np.inf, np.inf, board.turn)
    if best_move:
        board.push(best_move)
        st.session_state["move_history"].append(best_move)
        st.session_state["engine_think"] = False

# Run engine move if needed
if st.session_state["engine_think"]:
    with st.spinner("Engine thinking..."):
        engine_move()

st.subheader("Chess Board")
draw_board()

# Move list
st.subheader("Move History")
temp_board = chess.Board()
move_texts = []
for idx, move in enumerate(st.session_state["move_history"], start=1):
    san = temp_board.san(move)
    move_texts.append(f"{idx}. {san}")
    temp_board.push(move)
st.write(", ".join(move_texts))

# Suggestion & evaluation
if not is_game_over(st.session_state["board"]):
    st.subheader("Engine Move Suggestions")
    move_evals = []
    for move in get_ordered_moves(st.session_state["board"]):
        st.session_state["board"].push(move)
        eval_val, _ = minimax(st.session_state["board"], st.session_state["depth"], -np.inf, np.inf, st.session_state["board"].turn)
        st.session_state["board"].pop()
        move_evals.append((move, eval_val))
    # Sort moves by evaluation
    move_evals.sort(key=lambda x: x[1], reverse=st.session_state["board"].turn==chess.WHITE)

    suggestions_data = []
    for move, score in move_evals[:5]:
        san = st.session_state["board"].san(move)
        suggestions_data.append({
            "Move": san,
            "Evaluation": score / 100,
            "Strength": abs(score),
            "Color": "green" if score > 0 else "red"
        })
    df = pd.DataFrame(suggestions_data)

    def style_move(row):
        color = row["Color"]
        return [f"color:{color}"] * len(row)

    styled_df = df.style.apply(style_move, axis=1)
    st.write(styled_df.to_html(), unsafe_allow_html=True)

    # Show top move with reasoning
    top_move, eval_score = move_evals[0]
    reason = ""
    if board.is_capture(top_move):
        captured = board.piece_at(top_move.to_square)
        reason = f"Captures {captured.symbol()}"
    elif board.gives_check(top_move):
        reason = "Gives check"
    else:
        reason = "Develops or improves position"

    st.markdown(f"**Best Move:** {st.session_state['board'].san(top_move)}")
    st.markdown(f"**Reasoning:** {reason}")

# Evaluation bar
if st.session_state["move_history"]:
    last_eval = evaluate_board(st.session_state["board"])
    eval_display = last_eval / 100
    color = "green" if eval_display > 0 else "red" if eval_display < 0 else "gray"
    st.markdown(
        f"<div style='background-color:#ddd; width:100%; height:30px; border-radius:5px; overflow:hidden;'>"
        f"<div style='width:{abs(eval_display)*50}%; background-color:{color}; height:100%;'></div></div>",
        unsafe_allow_html=True
    )
    st.write(f"Evaluation: {last_eval} centipawns ({eval_display:.2f} pawns)")

# Plot evaluation over game
if st.session_state["evaluations"]:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=st.session_state["evaluations"],
        mode='lines+markers'
    ))
    fig.update_layout(title="Evaluation over Game", yaxis_title="Evaluation (cp)")
    st.plotly_chart(fig)

# Material balance
def material_balance():
    white_material = 0
    black_material = 0
    for square in chess.SQUARES:
        piece = st.session_state["board"].piece_at(square)
        if piece:
            value = PIECE_VALUES[piece.piece_type]
            if piece.color == chess.WHITE:
                white_material += value
            else:
                black_material += value
    df = pd.DataFrame({
        "White": [white_material],
        "Black": [black_material]
    })
    st.bar_chart(df)

material_balance()
