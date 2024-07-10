import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import asyncio
import re
import json
import os

data_file = "data/user_data.json"

class WBTB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Charger les données depuis le fichier JSON
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                self.user_data = json.load(f)
        else:
            self.user_data = {}

        self.alarms = self.user_data.get('alarms', {})

        # Planifier les alarmes déjà présentes
        for user_id, target_time_str in self.alarms.items():
            target_time = datetime.fromisoformat(target_time_str)
            now = datetime.now(timezone.utc)
            if target_time > now:
                wait_time = (target_time - now).total_seconds()
                self.bot.loop.call_later(wait_time, self.wake_user, int(user_id), target_time)

    def save_user_data(self):
        self.user_data['alarms'] = self.alarms
        with open(data_file, 'w') as f:
            json.dump(self.user_data, f)

    def wake_user(self, user_id, target_time):
        user = self.bot.get_user(user_id)
        if user:
            message = self.get_wake_message(target_time.astimezone(timezone(timedelta(hours=2))).hour)
            asyncio.run_coroutine_threadsafe(
                user.send(f"Debout {user.mention} ! Il est {target_time.astimezone(timezone(timedelta(hours=2))).strftime('%H:%M')} ! {message}"),
                self.bot.loop
            )
        del self.alarms[str(user_id)]
        self.save_user_data()

    def get_wake_message(self, hour):
        messages = {
            0: "T'es un vampire ou quoi ?",
            1: "Pas encore couché ou déjà levé ? Va te recoucher.",
            2: "Franchement, à quoi tu joues à cette heure ?",
            3: "Les fantômes vont t'attraper, retourne dormir.",
            4: "Il n'y a que les boulangers qui bossent à cette heure.",
            5: "Un peu tôt pour sauver le monde, non ?",
            6: "Le soleil se lève à peine, bonne chance.",
            7: "L'heure des braves, ou des fous.",
            8: "Déjà debout ? Va prendre un café.",
            9: "Une matinée bien remplie t'attend.",
            10: "C'est presque l'heure de la pause café.",
            11: "Bientôt l'heure de manger, tiens bon.",
            12: "Réveil en pleine journée, quel luxe.",
            13: "T'es prêt pour affronter l'après-midi ?",
            14: "L'heure de la sieste est proche.",
            15: "Encore debout ? Bravo, champion.",
            16: "T'as encore du boulot, courage.",
            17: "La fin de journée approche.",
            18: "Soirée tranquille en vue ?",
            19: "Pas l'heure de faire la fête, sérieux.",
            20: "Les rêves sont pour plus tard.",
            21: "Encore debout à cette heure ?",
            22: "Va te coucher, demain est un autre jour.",
            23: "Les rêves n'attendent plus, dors."
        }
        return messages.get(hour, "Heure bizarre, mais on verra bien !")

    @commands.command()
    async def wbtb(self, ctx, time: str = None):
        user = ctx.author
        if time is None:
            await ctx.send(f"T'as oublié de me dire quand te réveiller ! T'as cru que t'étais Pikimi ou quoi ? Utilise `o!wbtb 9h` avant de plonger dans le monde des rêves.")
            return
        
        parsed_time = self.parse_time(time)
        if not parsed_time:
            await ctx.send("T'as fumé quoi pour penser que c'était une heure valide ? T'as pris exemple sur Happy hap et Noé ? Utilise `9h`, `9h00`, `9:00`, `9`, etc.")
            return

        hour, minute = parsed_time
        if hour >= 24 or minute >= 60:
            await ctx.send("Sérieusement, tu rêves éveillé avec cette heure là. Essayez un format valide comme `9h` ou `9h30`.")
            return

        now = datetime.now(timezone.utc)

        # Calculer l'heure cible en UTC+2
        target_time = now.replace(hour=hour - 2, minute=minute, second=0, microsecond=0)
        if target_time < now:
            target_time += timedelta(days=1)

        wait_time = (target_time - now).total_seconds()
        self.alarms[str(user.id)] = target_time.isoformat()
        self.save_user_data()

        comment = self.get_wake_message(target_time.astimezone(timezone(timedelta(hours=2))).hour)

        await ctx.send(f"Réveil programmé à {target_time.astimezone(timezone(timedelta(hours=2))).strftime('%H:%M')} pour {user.mention}. Bonne nuit et fais de beaux rêves lucides ! {comment}")

        self.bot.loop.call_later(wait_time, self.wake_user, user.id, target_time)

    @commands.command()
    async def wbtblist(self, ctx):
        if not self.alarms:
            await ctx.send("Il n'y a pas d'alarmes programmées. Continue de rêver, mais n'oublie pas de te réveiller !")
            return

        embed = discord.Embed(title="Alarmes WBTB programmées", color=discord.Color.blue())
        for user_id, alarm_time_str in self.alarms.items():
            user = await self.bot.fetch_user(int(user_id))
            alarm_time = datetime.fromisoformat(alarm_time_str).astimezone(timezone(timedelta(hours=2)))
            hour = alarm_time.hour
            description = self.get_wake_description(hour)

            embed.add_field(
                name=f"{user.name} ({alarm_time.strftime('%H:%M')}) - {description}", 
                value='\u200b',  # Utilise un espace invisible pour le champ de valeur
                inline=False
            )
            embed.set_thumbnail(url=user.avatar_url)
        
        await ctx.send(embed=embed)

    def get_wake_description(self, hour):
        descriptions = {
            0: "le vampire",
            1: "le noctambule",
            2: "l'énigmatique",
            3: "l'insomniaque",
            4: "le boulanger",
            5: "le courageux",
            6: "le vaillant",
            7: "l'ambitieux",
            8: "le caféinomane",
            9: "l'énergique",
            10: "le matinal",
            11: "le survivant",
            12: "le chanceux",
            13: "le combattant",
            14: "le siesteur",
            15: "le persistant",
            16: "le travailleur",
            17: "le tenace",
            18: "le crépusculaire",
            19: "l'anticipateur",
            20: "le nocturne",
            21: "le tardif",
            22: "le procrastinateur",
            23: "le rêveur"
        }
        return descriptions.get(hour, "l'étrange")

    def parse_time(self, time_str):
        time_str = time_str.lower().replace('h', ':').replace(' ', '')
        match = re.match(r'(\d{1,2}):?(\d{2})?', time_str)
        if not match:
            return None
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        return hour, minute

def setup(bot):
    bot.add_cog(WBTB(bot))
