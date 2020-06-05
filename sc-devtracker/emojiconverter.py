
official_emoji_map = {
    ':first_place_medal:': ':1st_place_medal:',
    ':second_place_medal:': ':2nd_place_medal:',
    ':third_place_medal:': ':3rd_place_medal:',
}


def get_converted_sc(shortcode):
    return official_emoji_map[shortcode]
