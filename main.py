import discord
from discord.ext import commands
from discord import app_commands
import datetime
import math
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class KaraHilalBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("Comenzile Slash (Kara Hilal + Kara Wash - Ultimate Edition) au fost sincronizate cu succes!")

bot = KaraHilalBot()

# ==================== PALETĂ CULORI TEMATICE (KH LOGO STYLE) ====================
KH_BLUE = discord.Color.from_rgb(0, 136, 255)   # Albastru Electric KH (Logo KH)
KH_CYAN = discord.Color.from_rgb(0, 229, 255)   # Cyan Neon Kara Wash

# ==================== PERMISIUNI ROLES ====================
SUPER_ADMIN_ROLE = "."

MAFIA_ROLES = [
    "⋮ Kara Hilal", 
    "Kara Hilal", 
    "Lider", 
    "Co-Lider", 
    "Capo", 
    "Admin Mafie", 
    "."
]

WASH_ADMIN_ROLES = [
    "Director Kara", 
    "Kara", 
    "Angajat Kara Wash", 
    "Kara Wash", 
    "."
]

# Rolul exclusiv pentru Director (reset pontaj)
DIRECTOR_WASH_ROLE = [
    "Director Kara",
    "."
]

# Rolul exclusiv pentru /pontaje_active
HR_ROLES = [
    "Resurse Umane",
    "."
]

# ==================== CANALE DE LOGURI ====================
LOG_ACTIVITATI_CHANNEL = "log-activitati"
LOG_PONTAJE_CHANNEL = "log-pontaje"
LOG_BULETINE_SECRET_CHANNEL = "evidensa-buletine"
LOG_SEIF_CHANNEL = "log-seif"
LOG_SPALATORIE_CHANNEL = "log-spalatorie"
LOG_INACTIVITATI_CHANNEL = "log-inactivitati"

async def send_log(guild: discord.Guild, channel_name: str, embed: discord.Embed):
    channel = discord.utils.get(guild.text_channels, name=channel_name)
    if channel:
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            pass

def has_super_admin_perm():
    def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.guild_permissions.administrator:
            return True
        user_roles = [role.name for role in interaction.user.roles]
        return SUPER_ADMIN_ROLE in user_roles
    return app_commands.check(predicate)

def has_mafia_perm():
    def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.guild_permissions.administrator:
            return True
        user_roles = [role.name for role in interaction.user.roles]
        return any(role in user_roles for role in MAFIA_ROLES)
    return app_commands.check(predicate)

def has_wash_perm():
    def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.guild_permissions.administrator:
            return True
        user_roles = [role.name for role in interaction.user.roles]
        return any(role in user_roles for role in WASH_ADMIN_ROLES)
    return app_commands.check(predicate)

def has_director_wash_perm():
    def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.guild_permissions.administrator:
            return True
        user_roles = [role.name for role in interaction.user.roles]
        return any(role in user_roles for role in DIRECTOR_WASH_ROLE)
    return app_commands.check(predicate)

def has_hr_perm():
    def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.guild_permissions.administrator:
            return True
        user_roles = [role.name for role in interaction.user.roles]
        return any(role in user_roles for role in HR_ROLES)
    return app_commands.check(predicate)

# ==================== BAZĂ DE DATE REȚETE COMPLETĂ ====================

RECIPES = {
    # --- DROGURI ---
    "cocaina": {"nume": "🍃 Cocaină (4 plicuri)", "output_qty": 4, "ingredients": {"frunze": 12, "plic_gol": 4, "amoniac": 1, "sodiu": 1}},
    "crack": {"nume": "💨 Cocaine Crack (2 plicuri)", "output_qty": 2, "ingredients": {"plic_cocaina": 1, "apa": 2, "bricheta": 1}},
    "meth": {"nume": "💉 Seringă Meth (3 bucăți)", "output_qty": 3, "ingredients": {"amoniac": 1, "detergent": 2, "absint": 4, "seringa_gola": 3}},
    "joint": {"nume": "🚬 Joint Marijuana (1 bucată)", "output_qty": 1, "ingredients": {"marijuana_maruntita": 1, "filtru": 1, "foita": 1, "grinder": 1}},
    "adderall": {"nume": "💊 Pastile Adderall (1 tableta)", "output_qty": 1, "ingredients": {"acid_benzoic": 1, "acetona": 1, "metamphetamina": 1, "tub_pastile": 1}},
    "pachet_tigari": {"nume": "📦 Pachet de Țigări (1 bucată)", "output_qty": 1, "ingredients": {"tutun_maruntit": 20, "foita": 5, "filtru": 5, "pachet_gol": 1, "rasnita_tutun": 1}},

    # --- ARME MICI ---
    "weapon_pistol": {"nume": "🔫 Weapon Pistol", "output_qty": 1, "ingredients": {"bani": 13000, "element": 1, "cadru": 1, "teava": 1, "mecanism": 1}},
    "pistol50": {"nume": "🔫 Pistol .50", "output_qty": 1, "ingredients": {"bani": 32500, "element": 3, "cadru": 1, "teava": 1, "mecanism": 1}},
    "microsmg": {"nume": "🔫 Micro SMG", "output_qty": 1, "ingredients": {"bani": 39000, "element": 3, "cadru": 1, "teava": 1, "mecanism": 1}},
    "pistol_mk2": {"nume": "🔫 Pistol MK2", "output_qty": 1, "ingredients": {"bani": 32500, "element": 3, "cadru": 1, "teava": 1, "mecanism": 1}},
    "machinepistol": {"nume": "🔫 MachinePistol (TEC-9)", "output_qty": 1, "ingredients": {"bani": 97500, "element": 5, "cadru": 1, "teava": 1, "mecanism": 1}},
    "vintage_pistol": {"nume": "🔫 Vintage Pistol", "output_qty": 1, "ingredients": {"bani": 117000, "element": 9, "cadru": 1, "teava": 1, "mecanism": 1}},
    "ceramic_pistol": {"nume": "🔫 Ceramic Pistol", "output_qty": 1, "ingredients": {"bani": 45500, "element": 4, "cadru": 1, "teava": 1, "mecanism": 1}},

    # --- ARME MARI ---
    "sawnoff_shotgun": {"nume": "💥 SawnOff Shotgun", "output_qty": 1, "ingredients": {"bani": 145000, "element": 12, "cadru": 1, "teava": 1, "mecanism": 1}},
    "assault_rifle": {"nume": "⚔️ Assault Rifle", "output_qty": 1, "ingredients": {"bani": 58500, "element": 7, "cadru": 1, "teava": 1, "mecanism": 1}},
    "assault_rifle_mk2": {"nume": "⚔️ Assault Rifle MK2", "output_qty": 1, "ingredients": {"bani": 65000, "element": 10, "cadru": 1, "teava": 1, "mecanism": 1}},
    "double_action": {"nume": "🔫 Double Action Revolver", "output_qty": 1, "ingredients": {"bani": 130000, "element": 9, "cadru": 1, "teava": 1, "mecanism": 1}},
    "compact_rifle": {"nume": "⚔️ Compact Rifle", "output_qty": 1, "ingredients": {"bani": 117000, "element": 12, "cadru": 1, "teava": 1, "mecanism": 1}},
    "gusenberg": {"nume": "💥 Gusenberg Sweeper", "output_qty": 1, "ingredients": {"bani": 162500, "element": 13, "cadru": 1, "teava": 1, "mecanism": 1}},
    "navy_revolver": {"nume": "🔫 Navy Revolver", "output_qty": 1, "ingredients": {"bani": 195000, "element": 15, "cadru": 1, "teava": 1, "mecanism": 1}},
    "revolver": {"nume": "🔫 Revolver", "output_qty": 1, "ingredients": {"bani": 182000, "element": 15, "cadru": 1, "teava": 1, "mecanism": 1}},

    # --- ARME ALBE ---
    "knife": {"nume": "🔪 Knife (Cuțit)", "output_qty": 1, "ingredients": {"bani": 13000, "element": 1, "cauciuc": 1}},
    "bata": {"nume": "🏏 Bâtă de Baseball", "output_qty": 1, "ingredients": {"bani": 8000, "placaj": 5}},
    "rozeta": {"nume": "🥊 Rozetă", "output_qty": 1, "ingredients": {"bani": 10000, "element": 1, "cauciuc": 1}},
    "dagger": {"nume": "🗡️ Dagger", "output_qty": 1, "ingredients": {"bani": 13000, "element": 1, "placaj": 5}},
    "switchblade": {"nume": "🔪 SwitchBlade", "output_qty": 1, "ingredients": {"bani": 195000, "element": 1, "cauciuc": 5}},
    "macheta": {"nume": "🪓 Machetă", "output_qty": 1, "ingredients": {"bani": 26000, "element": 2, "cauciuc": 5}},
    "battle_axe": {"nume": "🪓 Battle Axe", "output_qty": 1, "ingredients": {"bani": 26000, "element": 2, "cauciuc": 2, "placaj": 2}},
    "lanterna": {"nume": "🔦 Lanternă", "output_qty": 1, "ingredients": {"bani": 13000, "element": 1, "bec": 1, "lupa": 1, "arc": 1}},

    # --- MUNIȚIE ---
    "munitie_weapon_pistol": {"nume": "🔹 Muniție Weapon Pistol (15 gloanțe)", "output_qty": 15, "ingredients": {"praf_de_pusca": 5}},
    "munitie_pistol50": {"nume": "🔹 Muniție Pistol .50 (15 gloanțe)", "output_qty": 15, "ingredients": {"praf_de_pusca": 5}},
    "munitie_microsmg": {"nume": "🔹 Muniție Micro SMG (30 gloanțe)", "output_qty": 30, "ingredients": {"praf_de_pusca": 5}},
    "munitie_pistol_mk2": {"nume": "🔹 Muniție Pistol MK2 (15 gloanțe)", "output_qty": 15, "ingredients": {"praf_de_pusca": 5}},
    "munitie_machinepistol": {"nume": "🔹 Muniție TEC-9 (30 gloanțe)", "output_qty": 30, "ingredients": {"praf_de_pusca": 5}},
    "munitie_vintage_pistol": {"nume": "🔹 Muniție Vintage Pistol (15 gloanțe)", "output_qty": 15, "ingredients": {"praf_de_pusca": 5}},
    "munitie_ceramic_pistol": {"nume": "🔹 Muniție Ceramic Pistol (15 gloanțe)", "output_qty": 15, "ingredients": {"praf_de_pusca": 5}},
    "munitie_sawnoff": {"nume": "🔹 Muniție SawnOff Shotgun (50 gloanțe)", "output_qty": 50, "ingredients": {"praf_de_pusca": 5}},
    "munitie_assault_rifle": {"nume": "🔹 Muniție Assault Rifle (30 gloanțe)", "output_qty": 30, "ingredients": {"praf_de_pusca": 5}},
    "munitie_assault_rifle_mk2": {"nume": "🔹 Muniție Assault Rifle MK2 (30 gloanțe)", "output_qty": 30, "ingredients": {"praf_de_pusca": 5}},
    "munitie_double_action": {"nume": "🔹 Muniție Double Action (15 gloanțe)", "output_qty": 15, "ingredients": {"praf_de_pusca": 5}},
    "munitie_compact_rifle": {"nume": "🔹 Muniție Compact Rifle (30 gloanțe)", "output_qty": 30, "ingredients": {"praf_de_pusca": 5}},
    "munitie_gusenberg": {"nume": "🔹 Muniție Gusenberg (30 gloanțe)", "output_qty": 30, "ingredients": {"praf_de_pusca": 5}},
    "munitie_navy_revolver": {"nume": "🔹 Muniție Navy Revolver (15 gloanțe)", "output_qty": 15, "ingredients": {"praf_de_pusca": 5}},
    "munitie_revolver": {"nume": "🔹 Muniție Revolver (15 gloanțe)", "output_qty": 15, "ingredients": {"praf_de_pusca": 5}},

    # --- ATAȘAMENTE ---
    "atasament_p50_ext": {"nume": "🔧 Atasament P.50 - Extended Weapon", "output_qty": 1, "ingredients": {"element_fixare": 1, "otel": 1, "arc": 5}},
    "atasament_p50_flash": {"nume": "🔧 Atasament P.50 - Flashlight", "output_qty": 1, "ingredients": {"element_fixare": 1, "otel": 1, "bec": 1, "lupa": 2}},
    "atasament_p50_supp": {"nume": "🔧 Atasament P.50 - Suppressor", "output_qty": 1, "ingredients": {"element_fixare": 1, "otel": 1, "cauciuc": 3}},
    "atasament_tec9_ext": {"nume": "🔧 Atasament TEC-9 - Extended Weapon", "output_qty": 1, "ingredients": {"element_fixare": 3, "otel": 1, "arc": 5}},
    "atasament_tec9_supp": {"nume": "🔧 Atasament TEC-9 - Suppressor", "output_qty": 1, "ingredients": {"element_fixare": 3, "otel": 1, "cauciuc": 3}},
    "atasament_vintage_ext": {"nume": "🔧 Atasament Vintage - Extended Weapon", "output_qty": 1, "ingredients": {"element_fixare": 1, "otel": 1, "arc": 5}},
    "atasament_vintage_supp": {"nume": "🔧 Atasament Vintage - Suppressor", "output_qty": 1, "ingredients": {"element_fixare": 3, "otel": 1, "cauciuc": 3}},
    "atasament_ceramic_ext": {"nume": "🔧 Atasament Ceramic - Extended Weapon", "output_qty": 1, "ingredients": {"element_fixare": 1, "otel": 1, "arc": 5}},
    "atasament_ceramic_supp": {"nume": "🔧 Atasament Ceramic - Suppressor", "output_qty": 1, "ingredients": {"element_fixare": 3, "otel": 1, "cauciuc": 3}},
    "atasament_mk2_ext": {"nume": "🔧 Atasament MK2 - Extended Weapon", "output_qty": 1, "ingredients": {"element_fixare": 3, "otel": 1, "arc": 5}},
    "atasament_mk2_flash": {"nume": "🔧 Atasament MK2 - Flashlight", "output_qty": 1, "ingredients": {"element_fixare": 1, "otel": 1, "bec": 1, "lupa": 2}},
    "atasament_mk2_supp": {"nume": "🔧 Atasament MK2 - Suppressor", "output_qty": 1, "ingredients": {"element_fixare": 3, "otel": 1, "cauciuc": 3}},
    "atasament_mk2_scope": {"nume": "🔧 Atasament MK2 - Scope", "output_qty": 1, "ingredients": {"element_fixare": 1, "otel": 1, "lupa": 2}},
    "atasament_mk2_comp": {"nume": "🔧 Atasament MK2 - Compensator", "output_qty": 1, "ingredients": {"element_fixare": 1, "otel": 1}},
    "atasament_pistol_ext": {"nume": "🔧 Atasament Pistol - Extended Weapon", "output_qty": 1, "ingredients": {"element_fixare": 1, "otel": 1, "arc": 5}},
    "atasament_pistol_flash": {"nume": "🔧 Atasament Pistol - Flashlight", "output_qty": 1, "ingredients": {"element_fixare": 1, "otel": 1, "bec": 1, "lupa": 2}},
    "atasament_pistol_supp": {"nume": "🔧 Atasament Pistol - Suppressor", "output_qty": 1, "ingredients": {"element_fixare": 1, "otel": 1, "cauciuc": 3}},
    "atasament_microsmg_ext": {"nume": "🔧 Atasament MicroSMG - Extended Weapon", "output_qty": 1, "ingredients": {"element_fixare": 2, "otel": 1, "arc": 5}},
    "atasament_microsmg_flash": {"nume": "🔧 Atasament MicroSMG - Flashlight", "output_qty": 1, "ingredients": {"element_fixare": 1, "otel": 1, "bec": 1}},
    "atasament_microsmg_supp": {"nume": "🔧 Atasament MicroSMG - Suppressor", "output_qty": 1, "ingredients": {"element_fixare": 2, "otel": 1, "cauciuc": 3}},
    "atasament_microsmg_scope": {"nume": "🔧 Atasament MicroSMG - Scope", "output_qty": 1, "ingredients": {"element_fixare": 1, "otel": 1}},
    "atasament_compact_ext": {"nume": "🔧 Atasament Compact Rifle - Extended Weapon", "output_qty": 1, "ingredients": {"element_fixare": 8, "otel": 1, "arc": 8}}
}

async def recipe_autocomplete(interaction: discord.Interaction, current: str):
    choices = []
    for key, data in RECIPES.items():
        if current.lower() in data['nume'].lower() or current.lower() in key.lower():
            choices.append(app_commands.Choice(name=data['nume'], value=key))
            if len(choices) >= 25:
                break
    return choices

# ==================== DATA STORES ====================
active_shifts = {}
total_time = {}
agenda_telefonica = [] 
misiune_curenta = {"titlu": "Nicio misiune activă", "descriere": "Conducerea nu a stabilit încă nicio misiune.", "recompensa": "-"}

def format_seconds(seconds: float) -> str:
    total_sec = int(seconds)
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    secs = total_sec % 60
    return f"{hours}h {minutes}m {secs}s"

# ==================== FORMULAR INACTIVITATE ====================

class InactivitateApprovalView(discord.ui.View):
    def __init__(self, applicant: discord.Member):
        super().__init__(timeout=None)
        self.applicant = applicant

    @discord.ui.button(label="Aprobă", style=discord.ButtonStyle.success, emoji="✅")
    async def btn_aprob(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_roles = [role.name for role in interaction.user.roles]
        if not (any(r in user_roles for r in MAFIA_ROLES) or interaction.user.guild_permissions.administrator):
            await interaction.response.send_message("❌ Doar Conducerea poate aproba inactivitățile!", ephemeral=True)
            return

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.set_field_at(3, name="Status Cerere", value=f"✅ **APROBATĂ** de {interaction.user.mention}", inline=False)
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Respinge", style=discord.ButtonStyle.danger, emoji="❌")
    async def btn_respinge(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_roles = [role.name for role in interaction.user.roles]
        if not (any(r in user_roles for r in MAFIA_ROLES) or interaction.user.guild_permissions.administrator):
            await interaction.response.send_message("❌ Doar Conducerea poate respinge inactivitățile!", ephemeral=True)
            return

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.set_field_at(3, name="Status Cerere", value=f"❌ **RESPINSĂ** de {interaction.user.mention}", inline=False)
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

class InactivitateModal(discord.ui.Modal, title="📝 Formular Inactivitate Kara Hilal"):
    data_inceput = discord.ui.TextInput(label="Data Început", placeholder="Ex: 15/10/2026", required=True)
    data_sfarsit = discord.ui.TextInput(label="Data Sfârșit", placeholder="Ex: 20/10/2026", required=True)
    motiv = discord.ui.TextInput(label="Motiv Inactivitate", style=discord.TextStyle.paragraph, placeholder="Motivul scurt...", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("✅ Cererea ta de inactivitate a fost trimisă către Conducere!", ephemeral=True)

        embed = discord.Embed(title="⚡ KARA HILAL — CERERE INACTIVITATE", color=KH_BLUE, timestamp=datetime.datetime.now())
        embed.add_field(name="👤 Membru", value=interaction.user.mention, inline=True)
        embed.add_field(name="📅 Perioadă", value=f"`{self.data_inceput.value}` ➔ `{self.data_sfarsit.value}`", inline=True)
        embed.add_field(name="📝 Motiv", value=self.motiv.value, inline=False)
        embed.add_field(name="Status Cerere", value="⏳ **ÎN AȘTEPTARE**", inline=False)
        embed.set_footer(text="Kara Hilal Management • Așteaptă decizia Liderilor")

        view = InactivitateApprovalView(applicant=interaction.user)
        log_channel = discord.utils.get(interaction.guild.text_channels, name=LOG_INACTIVITATI_CHANNEL)
        if log_channel:
            await log_channel.send(embed=embed, view=view)

# ==================== ACTIVITĂȚI & SUMAR ====================

class ActivityView(discord.ui.View):
    def __init__(self, titlu_activitate, organizator: discord.Member):
        super().__init__(timeout=None)
        self.titlu = titlu_activitate
        self.organizator = organizator
        self.prezenti = set()
        self.absenti = set()
        self.intarzieri = set()

    async def update_embed(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0]
        prez_str = "\n".join([m.mention for m in self.prezenti]) if self.prezenti else "*Niciunul*"
        abs_str = "\n".join([m.mention for m in self.absenti]) if self.absenti else "*Niciunul*"
        int_str = "\n".join([m.mention for m in self.intarzieri]) if self.intarzieri else "*Niciunul*"

        embed.set_field_at(2, name=f"✅ Prezenți ({len(self.prezenti)})", value=prez_str, inline=True)
        embed.set_field_at(3, name=f"❌ Absenți ({len(self.absenti)})", value=abs_str, inline=True)
        embed.set_field_at(4, name=f"⏳ Întârzie ({len(self.intarzieri)})", value=int_str, inline=True)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Prezent", style=discord.ButtonStyle.primary, emoji="✅")
    async def btn_prezent(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.absenti.discard(interaction.user)
        self.intarzieri.discard(interaction.user)
        self.prezenti.add(interaction.user)
        await self.update_embed(interaction)

    @discord.ui.button(label="Absent", style=discord.ButtonStyle.danger, emoji="❌")
    async def btn_absent(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.prezenti.discard(interaction.user)
        self.intarzieri.discard(interaction.user)
        self.absenti.add(interaction.user)
        await self.update_embed(interaction)

    @discord.ui.button(label="Întârzii", style=discord.ButtonStyle.secondary, emoji="⏳")
    async def btn_intarzie(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.prezenti.discard(interaction.user)
        self.absenti.discard(interaction.user)
        self.intarzieri.add(interaction.user)
        await self.update_embed(interaction)

    @discord.ui.button(label="Oprește Activitatea", style=discord.ButtonStyle.danger, emoji="⏹️", row=1)
    async def btn_stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.organizator and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Doar organizatorul poate opri activitatea!", ephemeral=True)
            return

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(view=self)

        sumar_embed = discord.Embed(title=f"📊 SUMAR FINAL ACTIVITATE — {self.titlu}", color=KH_BLUE, timestamp=datetime.datetime.now())
        sumar_embed.add_field(name=f"✅ Prezenți ({len(self.prezenti)})", value="\n".join([m.mention for m in self.prezenti]) if self.prezenti else "*Niciunul*", inline=False)
        sumar_embed.add_field(name=f"❌ Absenți ({len(self.absenti)})", value="\n".join([m.mention for m in self.absenti]) if self.absenti else "*Niciunul*", inline=False)
        sumar_embed.add_field(name=f"⏳ Întârziați ({len(self.intarzieri)})", value="\n".join([m.mention for m in self.intarzieri]) if self.intarzieri else "*Niciunul*", inline=False)
        sumar_embed.set_footer(text=f"Activitate Încheiată de {interaction.user.display_name}")

        await interaction.channel.send(embed=sumar_embed)
        await send_log(interaction.guild, LOG_ACTIVITATI_CHANNEL, sumar_embed)

    @discord.ui.button(label="Adaugă / Exclude Membru", style=discord.ButtonStyle.secondary, emoji="⚙️", row=1)
    async def btn_manage(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.organizator and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Doar organizatorul poate gestiona membrii!", ephemeral=True)
            return
        await interaction.response.send_modal(ManageMemberModal(self))

class ManageMemberModal(discord.ui.Modal, title="Gestionare Membru Activitate"):
    nume_membru = discord.ui.TextInput(label="ID sau Nume Discord / Mențiune", placeholder="Ex: @nume sau ID", required=True)
    actiune = discord.ui.TextInput(label="Acțiune", placeholder="Scrie 'adauga' sau 'exclude'", required=True)

    def __init__(self, view: ActivityView):
        super().__init__()
        self.view_obj = view

    async def on_submit(self, interaction: discord.Interaction):
        target_str = self.nume_membru.value.strip()
        member = None

        if target_str.startswith("<@") and target_str.endswith(">"):
            clean_id = target_str.replace("<@", "").replace(">", "").replace("!", "")
            if clean_id.isdigit():
                member = interaction.guild.get_member(int(clean_id))
        elif target_str.isdigit():
            member = interaction.guild.get_member(int(target_str))
        else:
            member = discord.utils.get(interaction.guild.members, name=target_str)

        if not member:
            await interaction.response.send_message(f"❌ Nu am găsit membrul: `{target_str}`", ephemeral=True)
            return

        act = self.actiune.value.strip().lower()
        if "adauga" in act:
            self.view_obj.absenti.discard(member)
            self.view_obj.intarzieri.discard(member)
            self.view_obj.prezenti.add(member)
            await interaction.response.send_message(f"✅ Membrul {member.mention} a fost adăugat la **Prezenți**.", ephemeral=True)
        elif "exclude" in act or "sterge" in act:
            self.view_obj.prezenti.discard(member)
            self.view_obj.absenti.discard(member)
            self.view_obj.intarzieri.discard(member)
            await interaction.response.send_message(f"🗑️ Membrul {member.mention} a fost exclus din listă.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Acțiune invalidă! Scrie 'adauga' sau 'exclude'.", ephemeral=True)

# ==================== BULETIN MODAL ====================

class BuletinModal(discord.ui.Modal, title="🪪 Registru Buletin IC"):
    nume = discord.ui.TextInput(label="Nume", placeholder="Nume din buletin", required=True)
    prenume = discord.ui.TextInput(label="Prenume", placeholder="Prenume din buletin", required=True)
    telefon = discord.ui.TextInput(label="Telefon", placeholder="Ex: 555-0192", required=True)
    cnp = discord.ui.TextInput(label="CNP", placeholder="CNP-ul", required=True)

    def __init__(self, imagine_buletin: discord.Attachment):
        super().__init__()
        self.imagine = imagine_buletin

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("✅ Datele au fost transmise în baza de date secretă!", ephemeral=True)

        embed = discord.Embed(title="⚡ KARA HILAL — BULETIN ÎNREGISTRAT", color=KH_BLUE, timestamp=datetime.datetime.now())
        embed.add_field(name="👤 Nume & Prenume", value=f"{self.nume.value} {self.prenume.value}", inline=True)
        embed.add_field(name="📱 Telefon", value=self.telefon.value, inline=True)
        embed.add_field(name="🆔 CNP", value=self.cnp.value, inline=False)
        embed.add_field(name="📩 Trimis de", value=interaction.user.mention, inline=False)
        if self.imagine:
            embed.set_image(url=self.imagine.url)

        channel = discord.utils.get(interaction.guild.text_channels, name=LOG_BULETINE_SECRET_CHANNEL)
        if channel:
            await channel.send(embed=embed)

# ==================== COMENZI PRINCIPALE MAFIA KARA HILAL ====================

@bot.tree.command(name="statie", description="📻 [EXCLUSIV GRADUL .] Anunță frecvența și parola pentru stație pe canalul dedicat")
@has_super_admin_perm()
@app_commands.describe(frecventa="Frecvența stației (ex: 100.5)", parola="Parola de la stație", detalii="Detalii suplimentare (opțional)")
async def statie(interaction: discord.Interaction, frecventa: str, parola: str, detalii: str = "Păstrați stația curată în timpul acțiunilor!"):
    target_channel = None
    for channel in interaction.guild.text_channels:
        if "frecventa-statie" in channel.name.lower():
            target_channel = channel
            break

    embed = discord.Embed(
        title="📻 FRECVENȚĂ STAȚIE ACTIVĂ — KARA HILAL",
        description="**Conducerea a stabilit o nouă frecvență de comunicare! Conectați-vă imediat.**",
        color=KH_BLUE,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="📡 Frecvență Stație", value=f"`{frecventa}`", inline=True)
    embed.add_field(name="🔑 Parolă Stație", value=f"`{parola}`", inline=True)
    embed.add_field(name="📝 Instrucțiuni / Detalii", value=detalii, inline=False)
    embed.add_field(name="👑 Anunțat de", value=interaction.user.mention, inline=False)
    embed.set_footer(text="Kara Hilal Radio Communication System • Confidențial")

    if target_channel:
        await target_channel.send(content="@everyone 🌙 **FRECVENȚĂ STAȚIE ACTUALIZATĂ!**", embed=embed)
        await interaction.response.send_message(f"✅ Frecvența și parola au fost postate pe canalul {target_channel.mention}!", ephemeral=True)
    else:
        await interaction.channel.send(content="@everyone 🌙 **FRECVENȚĂ STAȚIE ACTUALIZATĂ!**", embed=embed)
        await interaction.response.send_message("⚠️ Canalul `frecventa-statie` nu a fost găsit cu exactitate, am postat pe canalul curent!", ephemeral=True)


@bot.tree.command(name="backup", description="🚨 Trimite un semnal de alarmă de urgență pentru toți membrii mafiei!")
@has_mafia_perm()
@app_commands.describe(locatie="Locația exactă", detalii="Detalii confruntare")
async def backup(interaction: discord.Interaction, locatie: str, detalii: str = "Fără detalii"):
    embed = discord.Embed(title="🚨 ALERTĂ MAXIMĂ KH — BACKUP SOLICITAT! 🚨", description="**Toți membrii conectați să intervină imediat!**", color=discord.Color.blue(), timestamp=datetime.datetime.now())
    embed.add_field(name="📍 Locație", value=locatie, inline=False)
    embed.add_field(name="📝 Detalii", value=detalii, inline=False)
    embed.add_field(name="👤 Solicitat de", value=interaction.user.mention, inline=True)
    embed.set_footer(text="Apasă F8 și conectează-te pe FiveM!")

    await interaction.response.send_message(content="@everyone 🌙 **ÎNTĂRIRI URGENTE!**", embed=embed)


@bot.tree.command(name="seif_deposit", description="📦 Înregistrează o depunere în seiful Kara Hilal")
@has_mafia_perm()
@app_commands.describe(obiect_sau_suma="Suma sau obiectele depuse", detalii="Mențiuni")
async def seif_deposit(interaction: discord.Interaction, obiect_sau_suma: str, detalii: str = "Nicio mențiune"):
    embed_public = discord.Embed(title="📦 SEIF KARA HILAL — DEPUNERE ÎNREGISTRATĂ", description=f"Depunere efectuată de {interaction.user.mention}.", color=KH_BLUE, timestamp=datetime.datetime.now())
    embed_public.add_field(name="📥 Conținut Depozit", value=obiect_sau_suma, inline=False)
    await interaction.response.send_message(embed=embed_public)

    log_embed = discord.Embed(title="🔒 LOG CONFIDENȚIAL — DEPUNERE SEIF", color=KH_BLUE, timestamp=datetime.datetime.now())
    log_embed.add_field(name="👤 Membru", value=interaction.user.mention, inline=True)
    log_embed.add_field(name="📥 Depozit", value=obiect_sau_suma, inline=False)
    await send_log(interaction.guild, LOG_SEIF_CHANNEL, log_embed)


@bot.tree.command(name="calculeaza", description="🧮 Calculator rețete, muniție și atașamente")
@has_mafia_perm()
@app_commands.describe(produs="Produsul dorit", cantitate_dorita="Cantitatea dorită")
@app_commands.autocomplete(produs=recipe_autocomplete)
async def calculeaza(interaction: discord.Interaction, produs: str, cantitate_dorita: int):
    recipe = RECIPES.get(produs)
    if not recipe:
        await interaction.response.send_message("❌ Rețeta nu a fost găsită!", ephemeral=True)
        return

    crafts_needed = math.ceil(cantitate_dorita / recipe["output_qty"])
    total_obtinut = crafts_needed * recipe["output_qty"]

    embed = discord.Embed(title="🧮 CALCULATOR CRAFTING — KARA HILAL", description=f"**Produs:** {recipe['nume']}\n**Dorite:** `{cantitate_dorita}` | **Reale:** `{total_obtinut}` ({crafts_needed} ture)", color=KH_BLUE)

    req_text = ""
    for ing, qty in recipe["ingredients"].items():
        total_qty = qty * crafts_needed
        if ing == "bani":
            req_text += f"💵 **Bani:** `${total_qty:,}`\n"
        else:
            req_text += f"🔹 **{ing.replace('_', ' ').capitalize()}:** `{total_qty}` bucăți\n"

    embed.add_field(name="📦 Resurse Necesare", value=req_text, inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="reminder", description="📢 Programază un reminder automat pentru o ședință / activitate")
@has_mafia_perm()
@app_commands.describe(minute_asteptare="Peste câte minute să se trimită reminder-ul", mesaj="Mesajul / Detaliile despre activitate")
async def reminder(interaction: discord.Interaction, minute_asteptare: int, mesaj: str):
    await interaction.response.send_message(f"⏰ Reminder programat! Va fi trimis peste `{minute_asteptare}` minute.", ephemeral=True)
    await asyncio.sleep(minute_asteptare * 60)
    
    embed = discord.Embed(title="🔔 REMINDER ACTIVITATE — KARA HILAL", description=f"**Atenție!** În curând începe o activitate importantă!\n\n**Detalii:** {mesaj}", color=KH_BLUE, timestamp=datetime.datetime.now())
    embed.set_footer(text="Intrați pe FiveM și pregătiți-vă de acțiune!")
    await interaction.channel.send(content="@everyone 🌙 **REMINDER ACTIVITATE!**", embed=embed)


@bot.tree.command(name="misiune_set", description="🎯 [LIDERI / .] Setează o misiune săptămânală")
@has_mafia_perm()
@app_commands.describe(titlu="Titlul Misiunii", descriere="Instrucțiunile/Misiunea", recompensa="Ce primesc la final")
async def misiune_set(interaction: discord.Interaction, titlu: str, descriere: str, recompensa: str):
    global misiune_curenta
    misiune_curenta = {"titlu": titlu, "descriere": descriere, "recompensa": recompensa}
    
    embed = discord.Embed(title=f"🎯 MISIUNE NOUĂ STABILITĂ: {titlu}", description=descriere, color=KH_BLUE, timestamp=datetime.datetime.now())
    embed.add_field(name="🎁 Recompensă / Bonus", value=recompensa, inline=False)
    await interaction.response.send_message(content="@everyone 🌙 **MISIUNE NOUĂ ACTIVATĂ!**", embed=embed)


@bot.tree.command(name="misiune_view", description="🎯 Vizualizează misiunea săptămânală activă")
@has_mafia_perm()
async def misiune_view(interaction: discord.Interaction):
    embed = discord.Embed(title=f"🎯 MISIUNE SĂPTĂMÂNALĂ ACTIVĂ", description=f"**Titlu:** {misiune_curenta['titlu']}\n\n**Descriere:** {misiune_curenta['descriere']}", color=KH_BLUE)
    embed.add_field(name="🎁 Recompensă", value=misiune_curenta['recompensa'], inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="inactivitate", description="📝 Completează un formular de inactivitate")
@has_mafia_perm()
async def inactivitate(interaction: discord.Interaction):
    await interaction.response.send_modal(InactivitateModal())


@bot.tree.command(name="trimite_buletin", description="Trimite evidența buletinului tău")
@has_mafia_perm()
@app_commands.describe(poza_buletin="Poză buletin")
async def trimite_buletin(interaction: discord.Interaction, poza_buletin: discord.Attachment):
    await interaction.response.send_modal(BuletinModal(imagine_buletin=poza_buletin))


@bot.tree.command(name="creeaza_activitate", description="[LIDERI / .] Inițiază o activitate")
@has_mafia_perm()
@app_commands.describe(titlu="Titlu", ora_data="Data & Ora", descriere="Instrucțiuni")
async def creeaza_activitate(interaction: discord.Interaction, titlu: str, ora_data: str, descriere: str):
    embed = discord.Embed(title=f"⚡ ACTIVITATE MAFIE: {titlu}", description=descriere, color=KH_BLUE)
    embed.add_field(name="🕒 Data & Ora", value=ora_data, inline=False)
    embed.add_field(name="👑 Organizator", value=interaction.user.mention, inline=False)
    embed.add_field(name="✅ Prezenți (0)", value="*Niciunul*", inline=True)
    embed.add_field(name="❌ Absenți (0)", value="*Niciunul*", inline=True)
    embed.add_field(name="⏳ Întârzie (0)", value="*Niciunul*", inline=True)

    view = ActivityView(titlu_activitate=titlu, organizator=interaction.user)
    await interaction.response.send_message(content="@everyone 🌙 **ACTIVITATE NOUĂ KH!**", embed=embed, view=view)


@bot.tree.command(name="agenda_add", description="📞 Adaugă un contact RP în agendă")
@has_mafia_perm()
@app_commands.describe(nume_rp="Nume IC", functie_factiune="Rol / Facțiune", numar_telefon="Număr IC")
async def agenda_add(interaction: discord.Interaction, nume_rp: str, functie_factiune: str, numar_telefon: str):
    agenda_telefonica.append({"nume": nume_rp, "functie": functie_factiune, "telefon": numar_telefon})
    embed = discord.Embed(title="📞 CONTACT ADĂUGAT ÎN AGENDĂ", color=KH_BLUE)
    embed.add_field(name="👤 Nume IC", value=nume_rp, inline=True)
    embed.add_field(name="💼 Rol", value=functie_factiune, inline=True)
    embed.add_field(name="📱 Telefon", value=f"`{numar_telefon}`", inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="agenda_search", description="📞 Caută un număr de telefon RP în agendă")
@has_mafia_perm()
@app_commands.describe(cautare="Numele sau funcția căutată")
async def agenda_search(interaction: discord.Interaction, cautare: str):
    rezultate = [c for c in agenda_telefonica if cautare.lower() in c['nume'].lower() or cautare.lower() in c['functie'].lower()]
    if not rezultate:
        await interaction.response.send_message(f"🔍 Nu am găsit contacte pentru: `{cautare}`", ephemeral=True)
        return

    embed = discord.Embed(title=f"📞 REZULTATE AGENDĂ: '{cautare}'", color=KH_BLUE)
    text_rezultate = "".join([f"👤 **{c['nume']}** ({c['functie']}) ➔ 📱 `{c['telefon']}`\n" for c in rezultate])
    embed.add_field(name="Contacte Găsite", value=text_rezultate, inline=False)
    await interaction.response.send_message(embed=embed)

# ==================== COMENZI PONTAJ & DEPUNERI SPĂLĂTORIE (Kara Wash) ====================

@bot.tree.command(name="spalatorie_depunere", description="🧼 Înregistrează încasări pentru Kara Wash")
@has_wash_perm()
@app_commands.describe(suma="Suma", tip_operatiune="Tip operațiune", detalii="Detalii")
async def spalatorie_depunere(interaction: discord.Interaction, suma: str, tip_operatiune: str, detalii: str = "Nicio mențiune"):
    embed_public = discord.Embed(title="🧼 KARA WASH — DEPUNERE ÎNREGISTRATĂ", description=f"Depus de {interaction.user.mention}.", color=KH_CYAN, timestamp=datetime.datetime.now())
    embed_public.add_field(name="💰 Suma", value=suma, inline=True)
    embed_public.add_field(name="📋 Tip", value=tip_operatiune, inline=True)
    await interaction.response.send_message(embed=embed_public)

    log_embed = discord.Embed(title="🧾 LOG SPĂLĂTORIE", color=KH_CYAN, timestamp=datetime.datetime.now())
    log_embed.add_field(name="👤 Membru", value=interaction.user.mention, inline=True)
    log_embed.add_field(name="💵 Suma", value=suma, inline=True)
    await send_log(interaction.guild, LOG_SPALATORIE_CHANNEL, log_embed)


@bot.tree.command(name="pontaj_start", description="🟢 Pornește tura de muncă la Kara Wash")
@has_wash_perm()
async def pontaj_start(interaction: discord.Interaction):
    if interaction.user.id in active_shifts:
        await interaction.response.send_message("⚠️ Ești deja pontat!", ephemeral=True)
        return
    active_shifts[interaction.user.id] = datetime.datetime.now()
    await interaction.response.send_message(f"🟢 Spor la muncă, {interaction.user.mention}! Tura ta a început.", ephemeral=True)


@bot.tree.command(name="pontaj_stop", description="🔴 Încheie tura de muncă la Kara Wash")
@has_wash_perm()
async def pontaj_stop(interaction: discord.Interaction):
    if interaction.user.id not in active_shifts:
        await interaction.response.send_message("❌ Nu ești pontat!", ephemeral=True)
        return
    start_time = active_shifts.pop(interaction.user.id)
    sec = (datetime.datetime.now() - start_time).total_seconds()
    total_time[interaction.user.id] = total_time.get(interaction.user.id, 0.0) + sec
    await interaction.response.send_message(f"🔴 Tură încheiată! Durată sesiune: `{format_seconds(sec)}`", ephemeral=True)


@bot.tree.command(name="pontaje_active", description="🟢 [HR] Afișază membrii care au tura de muncă deschisă în acest moment")
@has_hr_perm()
async def pontaje_active(interaction: discord.Interaction):
    if not active_shifts:
        await interaction.response.send_message("🟢 Nu există nicio tură activă în acest moment la Kara Wash.", ephemeral=True)
        return

    embed = discord.Embed(title="🟢 PONTAJE ACTIVE — KARA WASH", color=KH_CYAN, timestamp=datetime.datetime.now())
    text_active = ""
    
    for uid, start_time in active_shifts.items():
        durata_curenta = (datetime.datetime.now() - start_time).total_seconds()
        text_active += f"🟢 <@!{uid}> — În tură de **{format_seconds(durata_curenta)}**\n"

    embed.add_field(name=f"Angajați Activi ({len(active_shifts)})", value=text_active, inline=False)
    embed.set_footer(text="Kara Wash HR System • Monitorizare Live Ture")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="top_pontaj", description="🏆 Clasament ore Kara Wash")
@has_wash_perm()
async def top_pontaj(interaction: discord.Interaction):
    if not total_time:
        await interaction.response.send_message("📊 Niciun pontaj înregistrat!", ephemeral=True)
        return
    sorted_u = sorted(total_time.items(), key=lambda x: x[1], reverse=True)[:10]
    embed = discord.Embed(title="🏆 CLASAMENT PONTAJ — KARA WASH", color=KH_CYAN)
    text = "".join([f"🥇 <@!{uid}> — **{format_seconds(s)}**\n" for uid, s in sorted_u])
    embed.add_field(name="Top Angajați", value=text, inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="profil_pontaj", description="📊 Verifică propriul tău profil și orele pontate la Kara Wash")
@has_wash_perm()
async def profil_pontaj(interaction: discord.Interaction):
    target = interaction.user
    user_id = target.id
    secunde_totale = total_time.get(user_id, 0.0)
    este_activ = user_id in active_shifts

    embed = discord.Embed(title=f"📋 Profil Pontaj — {target.display_name}", color=KH_CYAN)
    if este_activ:
        durata = (datetime.datetime.now() - active_shifts[user_id]).total_seconds()
        embed.add_field(name="🟢 Stare Curentă", value=f"În tură ({format_seconds(durata)})", inline=False)
    else:
        embed.add_field(name="🔴 Stare Curentă", value="Inactiv", inline=False)

    embed.add_field(name="⏳ Timp Total Acumulat", value=format_seconds(secunde_totale), inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="reset_pontaj", description="🔄 [EXCLUSIV DIRECTOR KARA] Resetează pontajul")
@has_director_wash_perm()
@app_commands.describe(membru="Membru de resetat", reset_toti="Setează pe True pentru resetare totală")
async def reset_pontaj(interaction: discord.Interaction, membru: discord.Member = None, reset_toti: bool = False):
    if reset_toti:
        total_time.clear()
        active_shifts.clear()
        embed = discord.Embed(title="🧹 RESET GENERAL PONTAJ", description="Toate orele au fost resetate la 0!", color=KH_CYAN)
        await interaction.response.send_message(embed=embed)
        return

    if membru is not None:
        total_time.pop(membru.id, None)
        active_shifts.pop(membru.id, None)
        embed = discord.Embed(title="🔄 RESET PONTAJ MEMBRU", description=f"Pontajul pentru {membru.mention} a fost resetat.", color=KH_CYAN)
        await interaction.response.send_message(embed=embed)
        return

    await interaction.response.send_message("❌ Alege un membru sau setează `reset_toti: True`!", ephemeral=True)


# Tratare Erori Permisiuni
@statie.error
@creeaza_activitate.error
@reminder.error
@misiune_set.error
@misiune_view.error
@inactivitate.error
@trimite_buletin.error
@calculeaza.error
@agenda_add.error
@agenda_search.error
@backup.error
@seif_deposit.error
@reset_pontaj.error
@spalatorie_depunere.error
@pontaj_start.error
@pontaj_stop.error
@pontaje_active.error
@top_pontaj.error
@profil_pontaj.error
async def perm_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("❌ Nu ai gradul necesar pentru a executa această comandă!", ephemeral=True)

bot.run(os.getenv("DISCORD_TOKEN"))
