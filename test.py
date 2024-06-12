def map_real_to_screen(display_screen, screen_dim, length_per_pixel, struct_frame):
    y_max = screen_dim[1]
    x_min = screen_dim[2]

    origin = ((struct_frame.origin[0] - x_min) / length_per_pixel, (y_max - struct_frame.origin[1]) / length_per_pixel)

    for part in struct_frame.parts:
        part.rect.center = origin + part.relative_struct_real
        display_screen.blit(part.image, part.rect)

    center_of_mass = ((struct_frame.cg[0] - x_min) / length_per_pixel, (y_max - struct_frame.cg[1]) / length_per_pixel)
