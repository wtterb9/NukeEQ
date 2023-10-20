import re


def parse_item_data(data):
    item = {}

    # Extract object name
    m = re.search("Object '(.+?)',", data)
    if m:
        item['name'] = m.group(1)

    # Extract item type
    m = re.search("Item type: (.+)", data)
    if m:
        item['type'] = m.group(1)

    # Extract abilities
    m = re.search("abilities: (.+)", data)
    if m:
        item['abilities'] = m.group(1)

    # Extract locations (worn, tattoo, or implant)
    location_type = "Worn" if "Worn Location(s):" in data else (
        "Tattoo" if "Tattoo Location(s):" in data else "Implant")
    m = re.search(f"{location_type} Location\(s\): (.+)", data)
    if m:
        item[f'{location_type.lower()}_locations'] = m.group(1)

    # Extract item properties
    item_properties = re.findall("ANTI_\w+|HUM|GLOW|MAGIC|NOBITS", data)
    item['properties'] = item_properties

    # Extract weight, value, rent, and min level
    m = re.search("Weight: (\d+), Suggested Retail Value: (\d+), Rent: (\d+), Min. level: (\d+)", data)
    if m:
        item['weight'] = int(m.group(1))
        item['value'] = int(m.group(2))
        item['rent'] = int(m.group(3))
        item['min_level'] = int(m.group(4))

    # Extract damage dice (only if present)
    m = re.search("Damage Dice is '(\d+D\d+)' for an average per-round damage of (\d+\.\d+).", data)
    if m:
        item['damage_dice'] = m.group(1)
        item['average_damage'] = float(m.group(2))

    # Extract affects
    affects = re.findall("Affects: (\w+|\w+_\w+) By (-?\d+)", data)
    item['affects'] = {a[0]: int(a[1]) for a in affects}

    return item


# Sample data
data = """
Object 'a tek implant capsule', Item type: IMPLANT
Item will give you following abilities:  NOBITS 
Implant Location(s): TAKE IMP_FINGER IMP_NECK IMP_CHEST IMP_SKULL IMP_LEG IMP_FOOT IMP_HAND IMP_ARM
IMP_STOMACH IMP_WRIST 
Item is: NOBITS 
Weight: 1, Suggested Retail Value: 2000, Rent: 200, Min. level: 0
Can affect you as :
   Affects: HITROLL By 2
   Affects: MANA_REGEN By 1
   Affects: MOVE_REGEN By 1
   Affects: HIT_REGEN By 1
"""

print(parse_item_data(data))
