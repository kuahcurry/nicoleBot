import discord
from discord.ext import commands
import random
import asyncio
import requests
import base64

class Games(commands.Cog):
    """Game commands including Tic-Tac-Toe, Rock-Paper-Scissors, Trivia Quiz, and Hangman."""

    def __init__(self, bot):
        self.bot = bot
        self.games = {}
        self.hangman_words = [
            "python", "discord", "bot", "hangman", "trivia",
            "computer", "programming", "algorithm", "function", "variable",
            "internet", "network", "server", "client", "database",
            "keyboard", "mouse", "monitor", "printer", "scanner",
            "software", "hardware", "application", "system", "security",
            "password", "encryption", "firewall", "malware", "virus",
            "debugging", "testing", "deployment", "integration", "development",
            "framework", "library", "module", "package", "repository",
            "version", "control", "branch", "commit", "merge",
            "pull", "push", "clone", "fork", "issue",
            "bug", "feature", "release", "update", "upgrade",
            "install", "uninstall", "configure", "setup", "build",
            "compile", "execute", "run", "script", "command",
            "terminal", "shell", "console", "prompt", "output",
            "input", "argument", "parameter", "option", "flag"
        ]
        self.categories = {
            "General Knowledge": 9,
            "Entertainment: Books": 10,
            "Entertainment: Film": 11,
            "Entertainment: Music": 12,
            "Entertainment: Musicals & Theatres": 13,
            "Entertainment: Television": 14,
            "Entertainment: Video Games": 15,
            "Entertainment: Board Games": 16,
            "Entertainment: Comics": 17,
            "Entertainment: Japanese Anime & Manga": 18,
            "Entertainment: Cartoon & Animations": 19,
            "Science & Nature": 17,
            "Science: Computers": 18,
            "Science: Mathematics": 19,
            "Science: Gadgets": 30,
            "Mythology": 20,
            "Sports": 21,
            "Geography": 22,
            "History": 23,
            "Politics": 24,
            "Art": 25,
            "Celebrities": 26,
            "Animals": 27,
            "Vehicles": 28
        }

    @commands.command(name='tictactoe')
    async def start_game(self, ctx, opponent: discord.Member):
        """Start a Tic-Tac-Toe game with an opponent."""
        if ctx.author == opponent:
            await ctx.send("You cannot play against yourself!")
            return

        if ctx.guild.id in self.games:
            await ctx.send("A game is already in progress in this server.")
            return

        self.games[ctx.guild.id] = {
            'board': [' ' for _ in range(9)],
            'turn': ctx.author,
            'players': [ctx.author, opponent]
        }
        await ctx.send(f"Tic-Tac-Toe game started between {ctx.author.mention} and {opponent.mention}!")
        await self.display_board(ctx)

    @commands.command(name='place')
    async def place_marker(self, ctx, position: int):
        """Place your marker on the board. (<prefix>place <position>) (Tick-Tack-Toe)"""
        if ctx.guild.id not in self.games:
            await ctx.send("No game in progress.")
            return

        game = self.games[ctx.guild.id]
        if ctx.author != game['turn']:
            await ctx.send("It's not your turn.")
            return

        if position < 1 or position > 9 or game['board'][position - 1] != ' ':
            await ctx.send("Invalid position. Choose a number between 1 and 9 that is not already taken.")
            return

        marker = 'X' if game['turn'] == game['players'][0] else 'O'
        game['board'][position - 1] = marker
        if self.check_winner(game['board'], marker):
            await ctx.send(f"{ctx.author.mention} wins!")
            del self.games[ctx.guild.id]
        elif ' ' not in game['board']:
            await ctx.send("It's a draw!")
            del self.games[ctx.guild.id]
        else:
            game['turn'] = game['players'][1] if game['turn'] == game['players'][0] else game['players'][0]
            await self.display_board(ctx)

    def check_winner(self, board, marker):
        """Check if the given marker has won."""
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
        return any(all(board[pos] == marker for pos in condition) for condition in win_conditions)

    async def display_board(self, ctx):
        """Display the current board."""
        game = self.games[ctx.guild.id]
        board = game['board']
        board_display = (
            f"{board[0]} | {board[1]} | {board[2]}\n"
            f"---------\n"
            f"{board[3]} | {board[4]} | {board[5]}\n"
            f"---------\n"
            f"{board[6]} | {board[7]} | {board[8]}"
        )
        await ctx.send(f"```\n{board_display}\n```")

    @commands.command(name='rps')
    async def play_rps(self, ctx, choice: str, opponent: discord.Member = None):
        """Play Rock, Paper, Scissors. (<prefix>rps <rock|paper|scissors> [opponent])"""
        choices = ['rock', 'paper', 'scissors']
        if choice.lower() not in choices:
            await ctx.send("Invalid choice! Please choose rock, paper, or scissors.")
            return

        if opponent:
            if ctx.author == opponent:
                await ctx.send("You cannot play against yourself!")
                return

            await ctx.send(f"{ctx.author.mention} challenges {opponent.mention} to Rock, Paper, Scissors!")
            await ctx.send(f"{opponent.mention}, please respond with your choice (rock, paper, or scissors).")

            def check(m):
                return m.author == opponent and m.channel == ctx.channel and m.content.lower() in choices

            try:
                response = await self.bot.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await ctx.send(f"{opponent.mention} did not respond in time. Game canceled.")
                return

            opponent_choice = response.content.lower()
            result = self.determine_winner(choice.lower(), opponent_choice)
            await ctx.send(f"{ctx.author.mention} chose {choice}, {opponent.mention} chose {opponent_choice}. {result}")
        else:
            bot_choice = random.choice(choices)
            result = self.determine_winner(choice.lower(), bot_choice)
            await ctx.send(f"You chose {choice}, I chose {bot_choice}. {result}")

    def determine_winner(self, player_choice, opponent_choice):
        if player_choice == opponent_choice:
            return "It's a tie!"
        elif (player_choice == 'rock' and opponent_choice == 'scissors') or \
             (player_choice == 'paper' and opponent_choice == 'rock') or \
             (player_choice == 'scissors' and opponent_choice == 'paper'):
            return "You win!"
        else:
            return "You lose!"

    @commands.command(name='trivia')
    async def trivia_quiz(self, ctx):
        """Start a trivia game. (<prefix>trivia)"""
        await ctx.send("Choose a mode:\n1. Singleplayer\n2. Multiplayer")

        def check_mode(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content in ['1', '2']

        try:
            response = await self.bot.wait_for('message', check=check_mode, timeout=30.0)
            mode = response.content
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")
            return

        if mode == '1':
            await self.singleplayer_trivia(ctx)
        elif mode == '2':
            await self.multiplayer_trivia(ctx)

    async def singleplayer_trivia(self, ctx):
        """Singleplayer Trivia game."""
        await ctx.send("How many questions would you like? (1-10)")
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= 10

        try:
            response = await self.bot.wait_for('message', check=check, timeout=30.0)
            amount = int(response.content)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")
            return

        await ctx.send("Choose a category:\n" + "\n".join([f"{i+1}. {category}" for i, category in enumerate(self.categories.keys())]))
        def check_category(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= len(self.categories)

        try:
            response = await self.bot.wait_for('message', check=check_category, timeout=30.0)
            category_index = int(response.content) - 1
            category = list(self.categories.values())[category_index]
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")
            return

        await ctx.send("Choose a difficulty (Easy, Medium, Hard):")
        def check_difficulty(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['easy', 'medium', 'hard']

        try:
            response = await self.bot.wait_for('message', check=check_difficulty, timeout=30.0)
            difficulty = response.content.lower()
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")
            return

        await ctx.send("Choose a type \n1. Multiple Options (multiple)\n2. True/False (boolean):")
        def check_type(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['multiple', 'boolean']

        try:
            response = await self.bot.wait_for('message', check=check_type, timeout=30.0)
            q_type = response.content.lower()
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")
            return

        url = f"https://opentdb.com/api.php?amount={amount}&category={category}&difficulty={difficulty}&type={q_type}&encode=base64"
        response = requests.get(url)
        data = response.json()

        if data['response_code'] != 0:
            await ctx.send("Failed to fetch trivia questions. Please try again later.")
            return

        correct_count = 0
        for i, question_data in enumerate(data['results']):
            question = base64.b64decode(question_data['question']).decode('utf-8')
            correct_answer = base64.b64decode(question_data['correct_answer']).decode('utf-8')
            incorrect_answers = [base64.b64decode(ans).decode('utf-8') for ans in question_data['incorrect_answers']]
            options = incorrect_answers + [correct_answer]
            random.shuffle(options)

            options_display = "\n".join([f"{i+1}. {option}" for i, option in enumerate(options)])
            await ctx.send(f"Question {i+1}: {question}\n\n{options_display}")

            def check_answer(m):
                return m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= len(options)

            try:
                response = await self.bot.wait_for('message', check=check_answer, timeout=15.0)
            except asyncio.TimeoutError:
                await ctx.send(f"Time's up! The correct answer was: {correct_answer}")
                continue

            answer_index = int(response.content) - 1
            if options[answer_index] == correct_answer:
                await ctx.send("Correct!")
                correct_count += 1
            else:
                await ctx.send(f"Wrong! The correct answer was: {correct_answer}")

        score_percentage = (correct_count / amount) * 100
        if score_percentage >= 85:
            grade = 'A'
        elif score_percentage >= 70:
            grade = 'B'
        elif score_percentage >= 45:
            grade = 'C'
        else:
            grade = 'D'

        await ctx.send(f"Trivia finished! You got {correct_count} out of {amount} correct. Your score: {grade}")

    async def multiplayer_trivia(self, ctx):
        """Multiplayer Trivia game."""
        await ctx.send("Multiplayer Trivia game started! Mention the players who will participate.")

        def check_players(m):
            return m.author == ctx.author and m.channel == ctx.channel and len(m.mentions) > 0

        try:
            response = await self.bot.wait_for('message', check=check_players, timeout=30.0)
            players = response.mentions
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")
            return

        await ctx.send("How many questions would you like? (1-10)")
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= 10

        try:
            response = await self.bot.wait_for('message', check=check, timeout=30.0)
            amount = int(response.content)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")
            return

        await ctx.send("Choose a category:\n" + "\n".join([f"{i+1}. {category}" for i, category in enumerate(self.categories.keys())]))
        def check_category(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= len(self.categories)

        try:
            response = await self.bot.wait_for('message', check=check_category, timeout=30.0)
            category_index = int(response.content) - 1
            category = list(self.categories.values())[category_index]
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")
            return

        await ctx.send("Choose a difficulty (Easy, Medium, Hard):")
        def check_difficulty(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['easy', 'medium', 'hard']

        try:
            response = await self.bot.wait_for('message', check=check_difficulty, timeout=30.0)
            difficulty = response.content.lower()
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")
            return

        await ctx.send("Choose a type \n1. Multiple Options (multiple)\n2. True/False (boolean):")
        def check_type(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['multiple', 'boolean']

        try:
            response = await self.bot.wait_for('message', check=check_type, timeout=30.0)
            q_type = response.content.lower()
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")
            return

        url = f"https://opentdb.com/api.php?amount={amount}&category={category}&difficulty={difficulty}&type={q_type}&encode=base64"
        response = requests.get(url)
        data = response.json()

        if data['response_code'] != 0:
            await ctx.send("Failed to fetch trivia questions. Please try again later.")
            return

        scores = {player: 0 for player in players}
        for i, question_data in enumerate(data['results']):
            question = base64.b64decode(question_data['question']).decode('utf-8')
            correct_answer = base64.b64decode(question_data['correct_answer']).decode('utf-8')
            incorrect_answers = [base64.b64decode(ans).decode('utf-8') for ans in question_data['incorrect_answers']]
            options = incorrect_answers + [correct_answer]
            random.shuffle(options)

            options_display = "\n".join([f"{i+1}. {option}" for i, option in enumerate(options)])
            await ctx.send(f"Question {i+1}: {question}\n\n{options_display}")

            player_answers = {}

            def check_answer(m):
                return m.author in players and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= len(options)

            try:
                while len(player_answers) < len(players):
                    response = await self.bot.wait_for('message', check=check_answer, timeout=10.0)
                    player_answers[response.author] = int(response.content) - 1
            except asyncio.TimeoutError:
                pass

            for player in players:
                if player in player_answers and options[player_answers[player]] == correct_answer:
                    await ctx.send(f"Correct! {player.mention} gets a point!")
                    scores[player] += 1
                else:
                    await ctx.send(f"Wrong or no answer! The correct answer was: {correct_answer}")

        results = "\n".join([f"{player.mention}: {score}" for player, score in scores.items()])
        await ctx.send(f"Trivia finished! Here are the scores:\n{results}")

    @commands.command(name='hangman')
    async def start_hangman(self, ctx):
        """Start a game of Hangman. (<prefix>hangman)"""
        await ctx.send("Choose a mode:\n1. Singleplayer\n2. Multiplayer")

        def check_mode(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content in ['1', '2']

        try:
            response = await self.bot.wait_for('message', check=check_mode, timeout=30.0)
            mode = response.content
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")
            return

        if mode == '1':
            await self.singleplayer_hangman(ctx)
        elif mode == '2':
            await self.multiplayer_hangman(ctx)

    async def singleplayer_hangman(self, ctx):
        """Singleplayer Hangman game."""
        word = random.choice(self.hangman_words)
        guessed = ['-'] * len(word)
        attempts = 6
        guessed_letters = []

        await ctx.send(f"Hangman game started! Word: {' '.join(guessed)}")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and len(m.content) == 1 and m.content.isalpha()

        while attempts > 0 and '-' in guessed:
            await ctx.send(f"Attempts remaining: {attempts}\nGuessed letters: {', '.join(guessed_letters)}")
            try:
                guess = await self.bot.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await ctx.send("Time's up!")
                break

            guess = guess.content.lower()
            if guess in guessed_letters:
                await ctx.send("You already guessed that letter.")
                continue

            guessed_letters.append(guess)
            if guess in word:
                for i, letter in enumerate(word):
                    if letter == guess:
                        guessed[i] = guess
                await ctx.send(f"Correct! Word: {' '.join(guessed)}")
            else:
                attempts -= 1
                await ctx.send(f"Wrong! Attempts remaining: {attempts}")

        if '-' not in guessed:
            await ctx.send(f"Congratulations! You guessed the word: {word}")
        else:
            await ctx.send(f"Game over! The word was: {word}")

    async def multiplayer_hangman(self, ctx):
        """Multiplayer Hangman game."""
        await ctx.send("Multiplayer Hangman game started! Mention the player who will guess the word.")

        def check_player(m):
            return m.author == ctx.author and m.channel == ctx.channel and len(m.mentions) == 1

        try:
            response = await self.bot.wait_for('message', check=check_player, timeout=30.0)
            player = response.mentions[0]
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")
            return

        word = random.choice(self.hangman_words)
        guessed = ['-'] * len(word)
        attempts = 6
        guessed_letters = []

        await ctx.send(f"Hangman game started! Word: {' '.join(guessed)}")

        def check(m):
            return m.author == player and m.channel == ctx.channel and len(m.content) == 1 and m.content.isalpha()

        while attempts > 0 and '-' in guessed:
            await ctx.send(f"Attempts remaining: {attempts}\nGuessed letters: {', '.join(guessed_letters)}")
            try:
                guess = await self.bot.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await ctx.send("Time's up!")
                break

            guess = guess.content.lower()
            if guess in guessed_letters:
                await ctx.send("You already guessed that letter.")
                continue

            guessed_letters.append(guess)
            if guess in word:
                for i, letter in enumerate(word):
                    if letter == guess:
                        guessed[i] = guess
                await ctx.send(f"Correct! Word: {' '.join(guessed)}")
            else:
                attempts -= 1
                await ctx.send(f"Wrong! Attempts remaining: {attempts}")

        if '-' not in guessed:
            await ctx.send(f"Congratulations! You guessed the word: {word}")
        else:
            await ctx.send(f"Game over! The word was: {word}")

async def setup(bot):
    await bot.add_cog(Games(bot))