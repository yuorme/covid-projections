#!/usr/bin/env python
# coding: utf-8

# Generates list of plotly sequential color schemes that have decreasing luminance and have 12 colors

import plotly.express as px

def calc_luminance(rgb):
    R = rgb[0]
    G = rgb[1]
    B = rgb[2]
    return (R+R+R+B+G+G+G+G)>>3


# Get list of all sequential color themes
named_colorscales = px.colors.named_colorscales()
style_lists = [[style,getattr(px.colors.sequential,style)] for style in dir(px.colors.sequential) if style.lower() in named_colorscales and len(getattr(px.colors.sequential,style)) >= 12]

decreasing_color_scales = []
for style in style_lists:
    prev_color = None
    for color in style[1]:
        if '#' in color:
            # to deal with pesky Plotly3. Making it a string again to avoid extra code chunk
            color = 'rgb'+ str(tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)))
        # if first color, assign to prev_color
        if prev_color is None:
            prev_color = calc_luminance(eval(color[3:]))
        else:
            # check that current color luminance geq to previous
            if calc_luminance(eval(color[ 3 : ])) >= prev_color:
                break
    else:
        decreasing_color_scales.append(style)

