import discord
from discord.ext import commands

# Crée une instance d'intents pour activer tous les événements (messages, membres, etc.)
intents = discord.Intents.all()

# Initialise le bot avec les intents et le préfixe de commande '!'
bot = commands.Bot(command_prefix='!', intents=intents)

# Variable globale pour stocker le salon vocal sélectionné
selected_voice_channel = None

# ID du salon texte où les logs et les commandes seront détectés (remplace par l'ID correct)
LOG_CHANNEL_ID = 1289902584920014898  # Remplace avec l'ID du salon de log où tu veux envoyer les messages

# Fonction pour envoyer un message dans le canal de log
async def send_log_message(guild, content):
    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(content)
    else:
        print(f"Le salon de log avec l'ID {LOG_CHANNEL_ID} n'a pas été trouvé.")

# Fonction pour détecter les salons vocaux actifs et demander de choisir si plusieurs sont disponibles
async def detect_and_select_vocal_channel(guild):
    global selected_voice_channel

    # Lister tous les salons vocaux avec des membres
    voice_channels = [channel for channel in guild.voice_channels if channel.members]
    
    # Si aucun salon vocal n'a de membres
    if not voice_channels:
        await send_log_message(guild, "Aucun salon vocal avec des membres n'est disponible.")
        return

    # Si un seul salon vocal est actif, le sélectionner automatiquement
    if len(voice_channels) == 1:
        selected_voice_channel = voice_channels[0]
        await send_log_message(guild, f"Salon vocal sélectionné automatiquement : {selected_voice_channel.name}")
        return

    # Si plusieurs salons sont disponibles, demander à l'utilisateur de choisir
    channel_list = "\n".join([f"{i+1}. {channel.name}" for i, channel in enumerate(voice_channels)])
    await send_log_message(guild, f"Choisis un salon vocal parmi les suivants en tapant son numéro :\n{channel_list}")

    def check(m):
        return m.channel.id == LOG_CHANNEL_ID and m.content.isdigit()

    # Attendre que l'utilisateur réponde avec un numéro
    try:
        msg = await bot.wait_for("message", check=check, timeout=30)
    except TimeoutError:
        await send_log_message(guild, "Temps écoulé. Veuillez réessayer.")
        return

    # Vérifier que la réponse correspond à un salon vocal valide
    choice = int(msg.content)
    if 1 <= choice <= len(voice_channels):
        selected_voice_channel = voice_channels[choice - 1]
        await send_log_message(guild, f"Salon vocal sélectionné : {selected_voice_channel.name}")
    else:
        await send_log_message(guild, "Choix invalide. Veuillez réessayer.")

# Événement lorsque le bot se connecte
@bot.event
async def on_ready():
    # Lorsque le bot est prêt, détecter les salons et demander la sélection si nécessaire
    for guild in bot.guilds:
        await send_log_message(guild, f"{bot.user.name} est connecté. Détection des salons vocaux avec des membres.")
        await detect_and_select_vocal_channel(guild)

# Événement pour traiter tous les messages dans un salon spécifique (y compris les webhooks et bots)
@bot.event
async def on_message(message):
    # Ne traiter que les messages dans le salon LOG_CHANNEL_ID
    if message.channel.id != LOG_CHANNEL_ID:
        return

    # Vérifier si le message est une commande pour mute_all ou unmute_all
    if message.content == "!mute_all":
        await mute_all(message)
    elif message.content == "!unmute_all":
        await unmute_all(message)

# Commande pour mute tout le monde dans le salon vocal sélectionné
async def mute_all(message):
    global selected_voice_channel

    # Vérifier si un salon vocal a été sélectionné
    if not selected_voice_channel:
        await send_log_message(message.guild, "Aucun salon vocal sélectionné. Utilise `!choisir_salon` pour en choisir un.")
        return
    
    muted_members = []

    # Parcourt les membres dans le salon vocal sélectionné et mute les membres
    for member in selected_voice_channel.members:
        if not member.bot:  # Mute uniquement les membres, pas les bots
            await member.edit(mute=True)
            muted_members.append(member.name)

    # Si des membres ont été mute, afficher les logs dans le salon de log
    if muted_members:
        member_names = ', '.join(muted_members)
        await send_log_message(message.guild, f"Les membres suivants ont été mute dans {selected_voice_channel.name} : {member_names}")
    else:
        await send_log_message(message.guild, f"Il n'y a aucun membre en vocal à mute dans {selected_voice_channel.name}.")

# Commande pour démute tout le monde dans le salon vocal sélectionné
async def unmute_all(message):
    global selected_voice_channel

    # Vérifier si un salon vocal a été sélectionné
    if not selected_voice_channel:
        await send_log_message(message.guild, "Aucun salon vocal sélectionné. Utilise `!choisir_salon` pour en choisir un.")
        return
    
    unmuted_members = []

    # Parcourt les membres dans le salon vocal sélectionné et démute les membres
    for member in selected_voice_channel.members:
        if not member.bot:  # Démute uniquement les membres, pas les bots
            await member.edit(mute=False)
            unmuted_members.append(member.name)

    # Si des membres ont été démute, afficher les logs dans le salon de log
    if unmuted_members:
        member_names = ', '.join(unmuted_members)
        await send_log_message(message.guild, f"Les membres suivants ont été démute dans {selected_voice_channel.name} : {member_names}")
    else:
        await send_log_message(message.guild, f"Il n'y a aucun membre en vocal à démute dans {selected_voice_channel.name}.")

# Commande pour choisir un nouveau salon vocal manuellement
@bot.command()
async def choisir_salon(ctx):
    await detect_and_select_vocal_channel(ctx.guild)

# Lancer le bot avec le token de votre bot Discord
bot.run('Token à changé ici')
