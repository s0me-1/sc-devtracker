
emoji_aliases_map = {
    ':first_place_medal:': ':1st_place_medal:',
    ':second_place_medal:': ':2nd_place_medal:',
    ':third_place_medal:': ':3rd_place_medal:',
}


def get_valid_shortcode(shortcode):
    return emoji_aliases_map[shortcode]

def get_patchable_shortcodes(shortcodes):
    return [sc for sc in shortcodes if sc in emoji_aliases_map.keys()]
