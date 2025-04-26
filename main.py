import discord
from discord.ext import commands
from discord import app_commands
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

# ─── Commands ───────────────────────────────────────────────────
@bot.tree.command(name="gen_webhooks", description="Regenerate server with channels and webhooks inside a red embed.")
async def gen_webhooks(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    guild = interaction.guild

    if not guild:
        await interaction.followup.send("❌ This command can only be used in a server.", ephemeral=True)
        return

    # ─ Delete all old channels ─
    for channel in guild.channels:
        try:
            await channel.delete()
        except Exception as e:
            print(f"❗ Failed to delete {channel.name}: {e}")

    # ─ Create structure ─
    structure = {
        ".": [
            "〔🕸️〕saved webhook",
            "〔🌐〕site"
        ],
        ".2": [
            "〔🚪〕visit"
        ],
        ".3": [
            "〔🔓〕nbc",
            "〔🔓〕premium",
            "〔🔐〕v-nbc",
            "〔🔐〕v-premium"
        ],
        ".4": [
            "〔📈〕success",
            "〔📉〕failed"
        ],
        ".5": [
            "〔📜〕acc-with-group",
            "〔📜〕acc-for-spam"
        ]
    }

    created_channels = {}
    saved_webhook_channel = None

    for category_name, channels in structure.items():
        category = await guild.create_category(category_name if category_name != "." else ".")
        for chan_name in channels:
            channel = await guild.create_text_channel(chan_name, category=category)
            created_channels[chan_name] = channel
            if chan_name == "〔🕸️〕saved webhook":
                saved_webhook_channel = channel

    if not saved_webhook_channel:
        await interaction.followup.send("❌ Failed to create saved webhook channel.", ephemeral=True)
        return

    # ─ Create webhooks and collect them into an embed ─
    webhook_embed = discord.Embed(
        title="🕸️ Saved Webhooks",
        description="Here are your generated webhooks.",
        color=discord.Color.red()  # Red color
    )

    for chan_name, channel in created_channels.items():
        if channel.id == saved_webhook_channel.id:
            continue
        try:
            webhook = await channel.create_webhook(name=f"Webhook - {chan_name}")
            webhook_embed.add_field(
                name=f"#{chan_name}",
                value=f"{webhook.url}",
                inline=False
            )
        except Exception as e:
            print(f"❗ Failed to create webhook in {chan_name}: {e}")

    # ─ Add GIF at bottom ─
    webhook_embed.set_image(
        url="https://media1.giphy.com/media/TIj8cbzWYKnE9ul3ab/giphy.gif?cid=6c09b9523m9bfr9o5es92kw9oyygwxxvj2bberdf31fevlhb&ep=v1_internal_gif_by_id&rid=giphy.gif&ct=s"
    )

    await saved_webhook_channel.send(embed=webhook_embed)
    await interaction.followup.send("✅ Server reset and webhooks generated successfully!", ephemeral=True)
    print(f"✅ All webhooks sent inside embed to {saved_webhook_channel.name}.")

# ─── Run Bot ────────────────────────────────────────────────────
bot.run(os.getenv("TOKEN"))
