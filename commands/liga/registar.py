import json
import os
import discord

PILOTOS_JSON = "jsons/pilotos.json"
NUMEROS_PROIBIDOS = {
    1, 2, 3, 4, 5, 6, 10, 11, 14, 16, 17, 18, 20, 21, 22,
    24, 27, 31, 42, 44, 47, 55, 63, 81, 87, 88
}

EQUIPAS_ROLE_ID = {
    "McLaren": 1352324048150855891,
    "Mercedes": 1352324189281063063,
    "Red Bull": 1352324328313716778,
    "Williams": 1352324417845334107,
    "Aston Martin": 1352324503979429918,
    "Kick Sauber": 1352324556366286889,
    "Ferrari": 1352324675983773768,
    "Alpine": 1352324722117050410,
    "Racing Bulls": 1352324838064390228,
    "Haas": 1352324972852416563,
}

PILOTOS_OFICIAIS = {
    "Red Bull": ["Verstappen", "Perez"],
    "Ferrari": ["Leclerc", "Sainz"],
    "Mercedes": ["Hamilton", "Russell"],
    "McLaren": ["Norris", "Piastri"],
    "Aston Martin": ["Alonso", "Stroll"],
    "Racing Bulls": ["Ricciardo", "Tsunoda"],
    "Haas": ["Magnussen", "Hülkenberg"],
    "Williams": ["Albon", "Sargeant"],
    "Alpine": ["Ocon", "Gasly"],
    "Kick Sauber": ["Bottas", "Zhou"]
}

def carregar_pilotos():
    if os.path.exists(PILOTOS_JSON):
        with open(PILOTOS_JSON, "r") as f:
            return json.load(f)
    return {}

def get_numeros_disponiveis():
    usados = {p["numero"] for p in carregar_pilotos().values()}
    return [
        discord.app_commands.Choice(name=str(i), value=i)
        for i in range(100)
        if i not in NUMEROS_PROIBIDOS and i not in usados
    ][:25]

def get_equipas_autocomplete(current: str):
    pilotos = carregar_pilotos()
    contagem = {equipe: 0 for equipe in EQUIPAS_ROLE_ID}
    for p in pilotos.values():
        contagem[p["equipa"]] += 1
    current_lower = current.lower()
    return [
        discord.app_commands.Choice(name=nome, value=nome)
        for nome in EQUIPAS_ROLE_ID
        if current_lower in nome.lower() and contagem[nome] < 2
    ][:25]

def get_pilotos_disponiveis(equipa: str, current: str):
    if equipa not in PILOTOS_OFICIAIS:
        return []
    usados = {p["piloto_replacable"] for p in carregar_pilotos().values() if p["equipa"] == equipa}
    return [
        discord.app_commands.Choice(name=nome, value=nome)
        for nome in PILOTOS_OFICIAIS[equipa]
        if nome not in usados and current.lower() in nome.lower()
    ][:25]

def register_registar_command(bot):
    @bot.tree.command(name="registar", description="Regista-te na liga de F1 com um número, nick e equipa.")
    @discord.app_commands.describe(
        nick="O nick que queres usar",
        numero="Número (0 a 99)",
        equipa="A tua equipa de F1",
        piloto_replacable="Piloto oficial que estás a substituir"
    )
    async def registar(interaction: discord.Interaction, nick: str, numero: int, equipa: str, piloto_replacable: str):
        user_id = str(interaction.user.id)

        if not (0 <= numero <= 99):
            await interaction.response.send_message("⚠️ O número deve estar entre 0 e 99.", ephemeral=True)
            return

        if numero in NUMEROS_PROIBIDOS:
            await interaction.response.send_message("🚫 Esse número é reservado e não pode ser usado.", ephemeral=True)
            return

        if equipa not in EQUIPAS_ROLE_ID:
            await interaction.response.send_message("❌ Equipa inválida ou cheia. Escolhe outra equipa.", ephemeral=True)
            return

        if piloto_replacable not in PILOTOS_OFICIAIS.get(equipa, []):
            await interaction.response.send_message("❌ Esse piloto não pertence a essa equipa!", ephemeral=True)
            return

        pilotos = carregar_pilotos()

        if user_id in pilotos:
            await interaction.response.send_message("⚠️ Já estás registado! Não podes registar-te novamente.", ephemeral=True)
            return

        # Verifica se a equipa já tem 2 pilotos
        count_equipa = sum(1 for p in pilotos.values() if p["equipa"] == equipa)
        if count_equipa >= 2:
            await interaction.response.send_message("❌ Essa equipa já tem 2 pilotos registados.", ephemeral=True)
            return

        # Verifica se o piloto já está usado
        if any(p["piloto_replacable"] == piloto_replacable and p["equipa"] == equipa for p in pilotos.values()):
            await interaction.response.send_message("❌ Esse piloto já está a ser substituído por outro jogador.", ephemeral=True)
            return

        # Verifica número já usado
        if any(p["numero"] == numero for p in pilotos.values()):
            await interaction.response.send_message("❌ Esse número já está a ser usado por outro piloto.", ephemeral=True)
            return

        pilotos[user_id] = {
            "nick": nick,
            "numero": numero,
            "equipa": equipa,
            "piloto_replacable": piloto_replacable,
            "discordId": user_id,
            "isAdmin": False
        }

        os.makedirs(os.path.dirname(PILOTOS_JSON), exist_ok=True)
        with open(PILOTOS_JSON, "w") as f:
            json.dump(pilotos, f, indent=2)

        novo_nick = f"{numero} - {nick}"
        try:
            await interaction.user.edit(nick=novo_nick)
        except discord.Forbidden:
            await interaction.response.send_message(
                f"✅ Registo feito como `{novo_nick}`, mas não consegui mudar o teu nickname.",
                ephemeral=True
            )

        # Atribuir role da equipa
        role_id = EQUIPAS_ROLE_ID.get(equipa)
        if role_id:
            role = interaction.guild.get_role(role_id)
            if role:
                await interaction.user.add_roles(role)

        await interaction.response.send_message(
            f"✅ Registado como **{novo_nick}** pela equipa **{equipa}** (substituindo **{piloto_replacable}**).",
            ephemeral=True
        )

    @registar.autocomplete("numero")
    async def autocomplete_numero(interaction: discord.Interaction, current: str):
        return get_numeros_disponiveis()

    @registar.autocomplete("equipa")
    async def autocomplete_equipa(interaction: discord.Interaction, current: str):
        return get_equipas_autocomplete(current)

    @registar.autocomplete("piloto_replacable")
    async def autocomplete_piloto(interaction: discord.Interaction, current: str):
        equipa = getattr(interaction.namespace, "equipa", None)
        return get_pilotos_disponiveis(equipa, current)
