
#je moet je hier niets van aantrekken dit was om de output van de ai te testen (conclusie gimini kan totaal nie tellen en gegereert veel te lange texten :(   zucht )

# def remove_empty_lines(file_path):
#     with open(file_path, "r", encoding="utf-8") as file:
#         lines = file.readlines()
#     with open(file_path, "w", encoding="utf-8") as file:
#         for line in lines:
#             if line.strip():  # Check if the line is not empty
#                 file.write(line)

def count_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    return len(lines)

def count_characters_per_line(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        character_counts = [len(line.strip()) for line in lines]
        for i, count in enumerate(character_counts, start=1):
            print(f"Lijn {i}: {count} karakters")
        return character_counts

# Voorbeeld van het aanroepen van de functie
bestandspad = "water.txt"
aantal_lijnen = count_lines(bestandspad)
count_characters_per_line(bestandspad)
print(f"Aantal lijnen in het bestand: {aantal_lijnen}")

