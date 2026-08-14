import discord
from discord.ext import commands
from logic import DB_Manager
from config import DATABASE, TOKEN

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='~', intents=intents)
manager = DB_Manager(DATABASE)

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

@bot.command(name='start') # Perintah untuk memulai percakapan
async def start_command(ctx): # Kode yang akan dijalankan begitu perintah '~start' dikirim user
    await ctx.send("Halo! Saya adalah bot manajer proyek\nSaya akan membantu kamu menyimpan proyek dan informasi tentangnya!)")
    await info_command(ctx)

@bot.command(name='info') # Perintah untuk nyari command yang ada apa saja
async def info_command(ctx):
    await ctx.send("""
Berikut adalah perintah yang dapat membantu kamu:

~play - gunakan untuk bermain tanya-jawabnya
~add_cards - gunakan untuk menambahkan flashcard baru
~library - gunakan untuk menampilkan card/pertanyaan apa saja yang sudah dibuat
~add_folder - gunakan untuk membuat kategori & mengoorganisir card-card

Kamu juga dapat memasukkan nama proyek untuk mengetahui informasi tentangnya!""")

@bot.command(name='add_folder')
async def add_folder_command(ctx, *, folder_name):
    manager.add_folder(folder_name)
    await ctx.send(f"Folder '{folder_name}' sukses ditambahkan!")

@bot.command(name='library')
async def library_command(ctx):
    folders = manager.get_folders()
    if folders:
        folder_list = "\n".join([f"{folder[0]}: {folder[1]}" for folder in folders])
        await ctx.send(f"Berikut adalah folder yang tersedia:\n{folder_list}")
    else:
        await ctx.send("Belum ada folder yang tersedia. Silakan tambahkan folder terlebih dahulu.")

class SaveButton(discord.ui.View):
    def __init__(self, folder_id, question, answer):
        super().__init__()
        self.folder_id = folder_id
        self.question = question
        self.answer = answer

    @discord.ui.button(label="Save", style=discord.ButtonStyle.green)
    async def save_button(self, interaction, button):
        manager.add_card(
            self.folder_id,
            self.question,
            self.answer
        )

        await interaction.response.edit_message(
            content="✅ Flashcard berhasil disimpan!",
            view=None
        )

@bot.command(name='add_cards')
async def add_cards_command(ctx, folder_id: int):

    await ctx.send("Masukkan pertanyaan flashcard:")

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    question_message = await bot.wait_for(
        "message",
        check=check
    )

    question = question_message.content

    await ctx.send("Masukkan jawaban flashcard:")

    answer_message = await bot.wait_for(
        "message",
        check=check
    )

    answer = answer_message.content

    await ctx.send(
        f"**Pertanyaan:** {question}\n"
        f"**Jawaban:** {answer}\n\n"
        "Apakah flashcard ini ingin disimpan?",
        view=SaveButton(folder_id, question, answer)
    )

class QuizView(discord.ui.View):
    def __init__(self, ctx, folder_id):
        super().__init__()
        self.ctx = ctx
        self.folder_id = folder_id

    @discord.ui.button(label="Next Question", style=discord.ButtonStyle.primary)
    async def next_question(self, interaction, button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                "Kamu bukan orang yang sedang mengikuti quiz ini.",
                ephemeral=True
            )
            return

        card = manager.get_random_card(self.folder_id)

        if not card:
            await interaction.response.edit_message(
                content="Tidak ada flashcard di folder ini.",
                view=None
            )
            return

        await interaction.response.edit_message(
            content=f"Pertanyaan: berikutnya:",
            view=None
        )

        await ask_question(self.ctx, self.folder_id, card)

    @discord.ui.button(label="Quit Answering", style=discord.ButtonStyle.danger)
    async def quit_answering(self, interaction, button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                "Kamu bukan orang yang sedang mengikuti quiz ini.",
                ephemeral=True
            )
            return

        await interaction.response.edit_message(
            content="Quiz dihentikan.",
            view=None
        )

async def ask_question(ctx, folder_id, card):

    question = card[2]
    correct_answer = card[3]

    await ctx.send(f"Pertanyaan: **{question}**")

    def check(message):
        return (
            message.author == ctx.author
            and message.channel == ctx.channel
        )

    answer_message = await bot.wait_for(
        "message",
        check=check
    )

    user_answer = answer_message.content

    if user_answer.lower().strip() == correct_answer.lower().strip():
        result = "✅ Jawaban benar!"
    else:
        result = (
            f"❌ Jawaban salah!\n"
            f"Jawaban yang benar: **{correct_answer}**"
        )

    await ctx.send(
        result,
        view=QuizView(ctx, folder_id)
    )

@bot.command(name='play')
async def play_command(ctx, folder_id: int):

    card = manager.get_random_card(folder_id)

    if not card:
        await ctx.send("Belum ada flashcard di folder ini.")
        return

    await ask_question(ctx, folder_id, card)


bot.run(TOKEN)
